# venture-sim

A Claude Code skill for people who are tired of testing money ideas one at a time in real life.

Instead of spending three months on one idea, hitting a wall and starting the next, it puts many ideas into a simulated world at once:

- **Player:** one Claude per field. It researches the field with real numbers (sources and dates) and writes a plan with decision rules.
- **World:** another Claude per field. It checks the five assumptions the plan depends on most, then plays the market against the plan month by month. Prospects say no, suppliers re-price, events happen.
- **Judge:** a neutral Claude. It ranks every field and names the best change or combination. It also says what the simulation cannot tell you, and writes a **14-day real-world test** with numbers that mean continue or stop.

You then go and run one cheap two-week test, not ten slow ones.

```
profile + fields
   │
   ├─ facts (shared conditions, researched once)
   │
   ├─ player 01 ─► world 01 ─┐
   ├─ player 02 ─► world 02 ─┤
   │      …                  ├─► scoreboard ─► judge ─► VERDICT.md
   └─ player N ─► world N  ──┘
```

## Install

```bash
git clone https://github.com/aliarmanmasoumi-byte/venture-sim-skill
cp -r venture-sim-skill/skills/venture-sim ~/.claude/skills/
```

Then, in Claude Code, type `/venture-sim €1,000/month net within a year`, or just ask "what business should I do?".

Use `--quick` for 5 fields and tighter caps.

## How a run goes

1. **Profile.** Claude writes `.sim/profile.md` from what it knows about you. It covers your goal as a net-profit number, location, hours, money cap, unfair advantages, what you already tried (and the wall each attempt hit), dislikes and hard constraints. See `templates/profile.example.md`.
2. **Fields.** Claude proposes N diverse fields built on your advantages, and you swap any you don't like. Each one becomes a personal brief: a role, the business, the questions that decide it, and the objections it must answer.
3. **Run.** `sim.py` writes every brief, tracks what is done, and pipelines the work: each world starts as soon as its player finishes.
4. **Verdict.** `VERDICT.md` holds the scoreboard (built from each world's machine-readable `results` block) plus the judge's ranking, winner, combinations, limits and 14-day tests.

## Cost

| fields | sub-agent calls | upper token estimate |
|---|---|---|
| 5 (`--quick`) | 12 | ~2.0M |
| 10 | 22 | ~3.8M |

The estimates come from the first real run. This version's hard search caps and write-once rule aim lower. On subscription plans a 10-field run usually pauses at session limits 2–3 times. Everything is on disk, so it resumes where it stopped.

## What changed after the first real run

The skill grew out of a real 10-field run. These fixes came from it:

- **Hard search caps** (12 per player, 6 per world). Soft guidance was ignored: players made 40–60 tool calls each.
- **A shared facts job.** Exchange rates, currency rules, logistics and platforms are researched once instead of ten times.
- **Write once.** Agents burned tokens re-trimming files to hit word limits; now ±5% is fine.
- **Standard probabilities:** `p_any` (at least one month at the target) vs `p_avg` (a 3-month average). Without that, worlds reported different things.
- **A machine-readable `results` block** in every world file, so the scoreboard is built by the script, not by a model re-reading twenty files.
- **The judge reads the worlds plus only the top three plans,** which cuts its input roughly in half.
- **Resume-first.** When a session limit stops agents, message them to continue instead of relaunching. `sim.py next` lists anything still missing.

## Honest limits

- Each world is one run by one kind of model on a handful of searches. The probabilities are calibrated judgement, not statistics.
- The simulation cannot tell whether anyone will actually pay **you**. That is what the 14-day test is for.
- "No field reaches your target in a year" is a common and useful result. The skill is told never to soften it.

## Rules the agents follow

- Research only: no contacting anyone, signing up, posting or buying.
- No plan that depends on deceiving banks, platforms, partners, customers or regulators, or on getting around laws or sanctions.

## Credits

Inspired by [court-skill](https://github.com/alexyc9381/court-skill) by Alex Chen. MIT licensed.
