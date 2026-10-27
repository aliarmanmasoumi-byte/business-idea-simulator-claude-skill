#!/usr/bin/env python3
"""venture-sim bookkeeping: run folder, briefs, resume, scoreboard, verdict.

Stdlib only. State lives in .sim/<run>/state.json under the current directory;
.sim/LATEST points at the newest run.
"""
import argparse
import datetime
import json
import pathlib
import re
import shutil
import sys
import unicodedata

SKILL_DIR = pathlib.Path(__file__).resolve().parent
SIM_ROOT = pathlib.Path(".sim")

# Tokens per sub-agent call, measured on the first real run (Opus, Oct 2026).
# The caps in this version aim lower, so treat these as an upper estimate.
COST = {"facts": 90_000, "player": 180_000, "world": 170_000, "judge": 210_000}

RESULTS_RE = re.compile(r"```results\s*\n(.*?)```", re.S)
FIELD_RE = re.compile(r"^##\s+(.+?)\s*$", re.M)


def words(text):
    """Word count that ignores table pipes, arrows and other bare punctuation."""
    return len([w for w in re.split(r"\s+", text) if re.search(r"\w", w)])


def slugify(title, n):
    ascii_title = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z0-9]+", "-", ascii_title.lower()).strip("-")
    return (s[:40].strip("-") or "field") if s else f"field-{n}"


def run_dir(run=None):
    if run:
        return SIM_ROOT / run
    latest = SIM_ROOT / "LATEST"
    if not latest.exists():
        sys.exit("No run yet. Start one with: sim.py init --profile ... --fields ...")
    return SIM_ROOT / latest.read_text(encoding="utf-8").strip()


def load_state(run=None):
    rd = run_dir(run)
    path = rd / "state.json"
    if not path.exists():
        sys.exit(f"Missing {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(state):
    path = pathlib.Path(state["dir"]) / "state.json"
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")


def P(state, *parts):
    return pathlib.Path(state["dir"]).resolve().joinpath(*parts)


# ---------------------------------------------------------------- jobs

def all_jobs(state):
    jobs = []
    if state["facts"]:
        jobs.append({"id": "facts", "kind": "facts", "out": "facts.md", "needs": []})
    for f in state["fields"]:
        name = f"{f['id']}-{f['slug']}.md"
        jobs.append({"id": f"player-{f['id']}", "kind": "player", "field": f,
                     "out": f"players/{name}", "needs": ["facts.md"] if state["facts"] else []})
        jobs.append({"id": f"world-{f['id']}", "kind": "world", "field": f,
                     "out": f"worlds/{name}", "needs": [f"players/{name}"]})
    worlds = [j["out"] for j in jobs if j["kind"] == "world"]
    jobs.append({"id": "judge", "kind": "judge", "out": "judge/verdict.md", "needs": worlds})
    return jobs


def is_done(state, rel):
    p = P(state, rel)
    return p.exists() and words(p.read_text(encoding="utf-8", errors="ignore")) >= 150


def ready_jobs(state):
    return [j for j in all_jobs(state)
            if not is_done(state, j["out"]) and all(is_done(state, n) for n in j["needs"])]


# ---------------------------------------------------------------- briefs

def brief_text(state, job):
    files = [P(state, "profile.md"), P(state, "rules.md")]
    if state["facts"] and job["kind"] != "facts":
        files.append(P(state, "facts.md"))
    out = P(state, job["out"])
    guard = ("Research only: never contact anyone, sign up, post, buy, log in or send anything. "
             f"Write only to:\n{out}")
    if job["kind"] == "facts":
        titles = "\n".join(f"- {f['id']} {f['title']}" for f in state["fields"])
        return f"""You are the FACTS researcher for a venture simulation. Sub-agents cannot see the
conversation, so these files are your whole world. Read completely:
{P(state, 'profile.md')}
{P(state, 'rules.md')}

The fields that will be simulated:
{titles}

Research ONCE the conditions that several fields share, so the players don't each re-search them:
exchange rates (and the free-market rate if different), inflation, taxes and currency rules that
apply to trade, logistics and shipping realities, which payment and sales platforms work for this
person, licences common to small businesses, and recent shocks. Give each fact a source URL and
date. Do not evaluate any field. HARD CAP: {state['caps']['facts']} searches/fetches. Max
{state['words']['facts']} words; write the file once.
{guard}

Reply in at most 2 lines: the file path and the three facts most likely to change the results."""
    if job["kind"] == "judge":
        return f"""You are the neutral JUDGE of a venture simulation. Sub-agents cannot see the
conversation, so these files are your whole world. Read completely:
{P(state, 'profile.md')}
{P(state, 'rules.md')}
{P(state, 'scoreboard.md')}
then every file in {P(state, 'worlds')}
and, in {P(state, 'players')}, only the files of the top three fields in the scoreboard.

Then do what the JUDGE section of rules.md says. Do no web research; judge only from the files.
Write the file once (max {state['words']['judge']} words).
{guard}

Reply in at most 5 lines: the file path, the top three with p_any_m12, and the bottom line."""
    f = job["field"]
    read = "\n".join(str(x) for x in files + [P(state, "fields", f"{f['id']}-{f['slug']}.md")])
    if job["kind"] == "player":
        return f"""You are the PLAYER for field {f['id']} ({f['title']}) in a venture simulation.
Sub-agents cannot see the conversation, so these files are your whole world. Read completely:
{read}

Then do what your field file and the PLAYER section of rules.md say. HARD CAP:
{state['caps']['player']} web searches/fetches in total. Count them; when you reach the cap, stop
researching and write.{" Don't re-research what facts.md covers." if state["facts"] else ""} Draft, count, write the file ONCE
(max {state['words']['player']} words, table pipes don't count, ±5% is fine).
{guard}

Reply in at most 3 lines: the file path, its word count, and the single riskiest assumption."""
    if job["kind"] == "world":
        return f"""You are the WORLD for field {f['id']} ({f['title']}) in a venture simulation.
Sub-agents cannot see the conversation, so these files are your whole world. Read completely:
{read}
{P(state, 'players', f"{f['id']}-{f['slug']}.md")}

Then do what the WORLD section of rules.md says, including the closing ```results block exactly
as specified. HARD CAP: {state['caps']['world']} searches/fetches in total. Draft, count, write
the file ONCE (max {state['words']['world']} words, table pipes don't count, ±5% is fine).
{guard}

Reply in at most 3 lines: the file path, first_target_month, and p_any_m12 / p_avg_m12."""
# ---------------------------------------------------------------- results

def pct(v):
    m = re.search(r"-?\d+(?:\.\d+)?", v or "")
    if not m:
        return None
    x = float(m.group())
    return x * 100 if "%" not in v and 0 < x <= 1 else x


def parse_results(text):
    m = RESULTS_RE.search(text)
    if not m:
        return None
    out = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def scoreboard(state):
    rows = []
    for f in state["fields"]:
        p = P(state, "worlds", f"{f['id']}-{f['slug']}.md")
        r = parse_results(p.read_text(encoding="utf-8", errors="ignore")) if p.exists() else None
        rows.append((f, r or {}))
    rows.sort(key=lambda fr: (pct(fr[1].get("p_any_m12")) or -1, pct(fr[1].get("p_avg_m12")) or -1),
              reverse=True)
    cols = ["p_any_m6", "p_any_m12", "p_avg_m12", "first_target_month", "m12_net_base",
            "y3_net_base", "peak_cash", "binding_constraint"]
    lines = [f"# Scoreboard — target: {state['target']}", "",
             "| field | " + " | ".join(cols) + " |", "|" + "---|" * (len(cols) + 1)]
    for f, r in rows:
        cells = [r.get(c, "—") for c in cols] if r else ["—"] * (len(cols) - 1) + ["no results block"]
        lines.append(f"| {f['id']} {f['title']} | " + " | ".join(cells) + " |")
    text = "\n".join(lines) + "\n"
    P(state, "scoreboard.md").write_text(text, encoding="utf-8")
    return text


# ---------------------------------------------------------------- commands

def cmd_plan(a):
    n = a.fields or (5 if a.quick else 10)
    calls = n * 2 + 1 + (0 if a.no_facts else 1)
    tokens = n * (COST["player"] + COST["world"]) + COST["judge"] + (0 if a.no_facts else COST["facts"])
    print(f"{n} fields: {calls} sub-agent calls, up to ~{tokens / 1e6:.1f}M tokens "
          f"(first-run measurement; the caps aim lower). Expect session-limit pauses on "
          f"subscription plans; the run resumes from the files on disk.")


def cmd_init(a):
    profile = pathlib.Path(a.profile)
    fields_md = pathlib.Path(a.fields).read_text(encoding="utf-8")
    heads = list(FIELD_RE.finditer(fields_md))
    if not heads:
        sys.exit("The fields file needs one '## <title>' heading per field.")
    run = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    rd = SIM_ROOT / run
    for sub in ("fields", "players", "worlds", "judge", "briefs"):
        (rd / sub).mkdir(parents=True, exist_ok=True)
    shutil.copy(profile, rd / "profile.md")
    quick = a.quick
    state = {
        "run": run, "dir": str(rd.resolve()), "target": a.target, "cap": a.cap, "start": a.start,
        "horizon": a.horizon, "facts": not a.no_facts,
        "caps": {"facts": 10, "player": 8 if quick else 12, "world": 4 if quick else 6},
        "words": {"facts": 900, "player": 1200 if quick else 1500,
                  "world": 1000 if quick else 1300, "judge": 1500},
        "fields": [],
    }
    for i, h in enumerate(heads, 1):
        end = heads[i].start() if i < len(heads) else len(fields_md)
        title = h.group(1).strip()
        f = {"id": f"{i:02d}", "title": title, "slug": slugify(title, i)}
        body = fields_md[h.end():end].strip()
        (rd / "fields" / f"{f['id']}-{f['slug']}.md").write_text(
            f"# Field {f['id']} — {title}\n\n{body}\n", encoding="utf-8")
        state["fields"].append(f)
    rules = (SKILL_DIR / "templates" / "rules.md").read_text(encoding="utf-8")
    for k, v in {"TARGET": a.target, "CAP": a.cap, "START": a.start, "HORIZON": str(a.horizon),
                 "RUN_DIR": str(rd.resolve()), "PLAYER_WORDS": str(state["words"]["player"]),
                 "WORLD_WORDS": str(state["words"]["world"]),
                 "JUDGE_WORDS": str(state["words"]["judge"])}.items():
        rules = rules.replace("{" + k + "}", v)
    (rd / "rules.md").write_text(rules, encoding="utf-8")
    save_state(state)
    (SIM_ROOT / "LATEST").write_text(run, encoding="utf-8")
    print(f"Run {run}: {len(state['fields'])} fields in {rd.resolve()}")
    for f in state["fields"]:
        print(f"  {f['id']} {f['title']}")


def cmd_status(a):
    state = load_state(a.run)
    for j in all_jobs(state):
        mark = "done" if is_done(state, j["out"]) else "ready" if all(
            is_done(state, n) for n in j["needs"]) else "waiting"
        print(f"{j['id']:<10} {mark:<8} {j['out']}")


def cmd_next(a):
    state = load_state(a.run)
    if is_done(state, "judge/verdict.md"):
        print("FINISHED. Run: sim.py render")
        return
    ready = ready_jobs(state)
    print("Ready now:", " ".join(j["id"] for j in ready) or "nothing (wait for running agents)")
    print("Then: sim.py prompts --ready [--wave 5]")


def cmd_prompts(a):
    state = load_state(a.run)
    jobs = {j["id"]: j for j in all_jobs(state)}
    chosen = ready_jobs(state) if a.ready or not a.jobs else [jobs[i] for i in a.jobs]
    chosen = chosen[: a.wave] if a.wave else chosen
    if any(j["kind"] == "judge" for j in chosen):
        scoreboard(state)
    for j in chosen:
        bp = P(state, "briefs", f"{j['id']}.md")
        bp.write_text(brief_text(state, j), encoding="utf-8")
        print(f"- description: sim {j['id']}\n  subagent_type: general-purpose\n"
              f"  prompt: Read {bp} and follow it exactly. It is your whole brief.")
    if not chosen:
        print("Nothing ready. Check with: sim.py status")


def cmd_check(a):
    state = load_state(a.run)
    limits = {"facts": "facts", "player": "player", "world": "world", "judge": "judge"}
    for j in all_jobs(state):
        p = P(state, j["out"])
        if not p.exists():
            continue
        t = p.read_text(encoding="utf-8", errors="ignore")
        n, cap = words(t), state["words"][limits[j["kind"]]]
        flags = []
        if n > cap * 1.05:
            flags.append(f"over limit ({cap})")
        if j["kind"] == "world" and not parse_results(t):
            flags.append("NO results block")
        print(f"{j['id']:<10} {n:>5} words  {'; '.join(flags) or 'ok'}")


def cmd_scoreboard(a):
    print(scoreboard(load_state(a.run)))


def cmd_render(a):
    state = load_state(a.run)
    board = scoreboard(state)
    vp = P(state, "judge", "verdict.md")
    if not vp.exists():
        sys.exit("No judge verdict yet.")
    out = P(state, "VERDICT.md")
    out.write_text(board + "\n---\n\n" + vp.read_text(encoding="utf-8"), encoding="utf-8")
    print(out)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="sim.py")
    sub = ap.add_subparsers(dest="cmd", required=True)
    pl = sub.add_parser("plan")
    pl.add_argument("--fields", type=int)
    pl.add_argument("--quick", action="store_true")
    pl.add_argument("--no-facts", action="store_true")
    pi = sub.add_parser("init")
    pi.add_argument("--profile", required=True)
    pi.add_argument("--fields", required=True, help="markdown with one '## title' section per field")
    pi.add_argument("--target", required=True, help='e.g. "€1,000/month net profit"')
    pi.add_argument("--cap", default="€3,000", help="max starting cash")
    pi.add_argument("--start", required=True, help='simulation month 1, e.g. "November 2026"')
    pi.add_argument("--horizon", type=int, default=12)
    pi.add_argument("--quick", action="store_true")
    pi.add_argument("--no-facts", action="store_true")
    for name in ("status", "next", "check", "scoreboard", "render"):
        sp = sub.add_parser(name)
        sp.add_argument("--run")
    pp = sub.add_parser("prompts")
    pp.add_argument("jobs", nargs="*")
    pp.add_argument("--ready", action="store_true")
    pp.add_argument("--wave", type=int, default=0)
    pp.add_argument("--run")
    a = ap.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    {"plan": cmd_plan, "init": cmd_init, "status": cmd_status, "next": cmd_next,
     "prompts": cmd_prompts, "check": cmd_check, "scoreboard": cmd_scoreboard,
     "render": cmd_render}[a.cmd](a)


if __name__ == "__main__":
    main()
