---
name: venture-sim
description: >-
  Find which way to make money actually works for one specific person before they spend months
  testing ideas one by one in real life. Several fields are each given to a PLAYER Claude (real
  research + a plan with decision rules) and a WORLD Claude (checks the plan's key assumptions and
  plays the market month by month), then a neutral JUDGE ranks them and writes a 14-day real-world
  test for the winner. Use when the user asks "what business should I do", "how can I make money",
  wants many ideas compared at once, says they are tired of trying ideas one at a time, or says
  "venture sim" / "simulate my options".
argument-hint: "[--quick] [--fields N] <goal, e.g. €1,000/month net within a year>"
license: MIT
metadata:
  author: "Arman Masoumi (@aliarmanmasoumi-byte)"
  source: "https://github.com/aliarmanmasoumi-byte/business-idea-simulator-claude-skill"
  version: "1.0.0"
---

# venture-sim

People often test money ideas one at a time in real life, spending months on each: build, outreach, silence, next idea. This skill runs many of them at once in a simulated world:

- A **player** researches each field with real numbers and writes a plan with decision rules.
- A **world** checks the plan's riskiest assumptions and plays the market against it, month by month.
- A **judge** compares them all.

Then the person runs only the winner's cheap 14-day test in the real world.

You are the organiser. You never write a player's plan, a world's run or the judge's verdict yourself.

What the user typed: `$ARGUMENTS`. If it is blank, take the goal from the conversation.

## The tool

All bookkeeping goes through `sim.py` in this skill's folder:

```bash
python3 "${CLAUDE_SKILL_DIR}/sim.py" <command>
```

Below, `SIM` means that command. If the path looks unexpanded, use the skill's base directory. Runs live in `.sim/<run>/` in the current directory, and `.sim/LATEST` points at the newest run.

## Step 1: the profile (the most important step)

**Sub-agents cannot see this conversation.** Write `.sim/profile.md` so it stands on its own; `templates/profile.example.md` shows the shape. Fill it from what the user said and what you already know (memory, earlier sessions). Ask only for what is truly missing, in one short list.

It must contain:
- **Goal as a number:** e.g. "€1,000/month net to start, room to grow to tens of thousands". Insist on net profit, not revenue.
- **Where they live**, which languages they speak, and how many hours a week they have.
- **Money cap** for all tests together, and what is off-limits (savings, loans).
- **Unfair advantages:** family, contacts, skills, assets, location.
- **Track record:** what they already tried and the real walls each one hit. Respect the effort; a wall is not "quitting".
- **What they dislike**, and their **hard constraints**. Only hard constraints remove a field.
- **Known conditions** of their country or market that every field faces.

## Step 2: choose the fields with the user

Propose N fields (default 10, 5 with `--quick`):
- Make them diverse in business model: trade, export, B2B service, product, local retail, content.
- Build each on the profile's advantages.
- Don't re-propose what already failed unless you have a genuinely new angle.

Show the list as one short line per field and let the user swap any. If the user says most fields look alike (e.g. all built on one skill), take the hint and widen the list.

Then write `.sim/fields.md` with one `## <title>` section per field. Each section is a **personal brief**, not a topic:
- a role ("You are the fig-export operator")
- the business in two lines
- a "find out with data" list of the questions that decide it
- the known objections it must answer with evidence

`templates/fields.example.md` shows two of them.

## Step 3: size it and start

```bash
SIM plan --fields N            # one line: calls and an upper token estimate
SIM init --profile .sim/profile.md --fields .sim/fields.md \
         --target "€1,000/month net profit" --cap "€3,000" --start "November 2026" [--quick]
```

Tell the user the size in one line, e.g. "10 fields: 22 sub-agent calls". Also say that on a subscription plan it will likely pause at session limits and resume from the files.

## Step 4: run it

Always drive the run with `SIM next`, then `SIM prompts --ready --wave 5`. That command writes one brief per ready job and prints, for each, the exact Agent call: `general-purpose`, with the prompt "Read <brief> and follow it exactly."

The order of jobs:
1. **facts:** one agent researches the shared conditions once (exchange rates, currency rules, logistics, platforms), so ten players don't each re-search them.
2. **players:** launched in waves of up to 5.
3. **worlds:** pipeline them. As soon as a player finishes, run `SIM next` and launch that field's world. Don't wait for the whole wave.
4. **judge:** once every world exists. `SIM prompts` builds `scoreboard.md` from the worlds' `results` blocks first.

Before the judge, run `SIM check`. It lists files over their word limit and worlds missing their `results` block. Re-run a world without a block once.

**When the session limit hits**, agents stop mid-task. Their work so far is kept.
- After the reset, send each stopped agent a short message ("limit reset, continue where you stopped, write your file once") instead of relaunching it.
- If that fails, `SIM next` lists the missing jobs to relaunch.
- If a job fails twice, tell the user. Never write its output yourself.

Give the user one short status line per finished world, not the results. The comparison comes at the end.

## Step 5: the verdict

```bash
SIM render     # writes VERDICT.md = scoreboard + judge
```

Report in the user's language, short. Include:
- the bottom line;
- the top three with their probabilities;
- the judge's best change or combination;
- what the simulation cannot tell;
- the winner's 14-day test with its continue/stop numbers;
- the path to `VERDICT.md`.

Rules for you:
- Never soften or inflate the verdict. "No field reaches the target in a year" is useful information.
- If the winner is something the user rejected before, say so plainly. The numbers chose it, not you.
- These are model judgements from single runs, not statistics. Say it once; don't hedge every line.
- Offer to start day 1 of the winner's test.
