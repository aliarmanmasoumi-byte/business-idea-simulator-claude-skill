# Simulation rules — read fully before you start

**Purpose:** find the field where the person in `profile.md` reaches **{TARGET}** soonest, with room to grow beyond it.

Each field has two agents:
- a PLAYER, which researches the field and writes a plan;
- a WORLD, which checks that plan against reality and plays the market month by month.

A neutral JUDGE then compares all fields. Month 1 of the simulation is **{START}**, and the run lasts **{HORIZON} months**.

Folder: `{RUN_DIR}`

## Rules for every agent
1. **Research only.** Never contact anyone, send messages or emails, post, sign up, buy, or log in anywhere. Web search and fetch are read-only. Write only your own output file.
2. **Real data.**
   - Every key number (prices, costs, fees, demand, conversion rates) needs a source URL and its date. If you have no source, mark it [est] and give one line of reasoning.
   - Prefer sources from the last 18 months.
   - Use the currencies in `profile.md`.
   - Use `facts.md` (if present) for anything shared by all fields: exchange rates, taxes, logistics, payment realities. Don't re-research what it already covers.
3. **Lawful and open.** No plan may depend on deceiving banks, platforms, partners, customers or regulators, or on getting around laws or sanctions. Don't research or describe workarounds. Cross-border payments use the normal lawful route the trade already uses; show only its cost and delay.
4. **Money cap.**
   - Starting cash is at most **{CAP}**, unless `profile.md` says otherwise. No loans.
   - Profits may be reinvested.
   - Outside capital is allowed only if you name who would put it in and why they would.
5. **Calibrated, not hopeful.** Use base rates: cold outreach gets a few percent of replies, and most new small businesses miss their year-1 targets. An unproven assumption lowers the score; it does not get the benefit of the doubt.
6. **Use the person's real advantages** in `profile.md`. Where the field file lists known objections, answer them with evidence.
7. **Respect the person's constraints** in `profile.md`. Only "hard constraints" filter a field out.
8. **Write once.**
   - Draft, count, then write the file a single time.
   - Words are counted without table pipes, and going ±5% over the limit is fine. Don't burn effort on re-trimming.
   - Write in English; the final summary is translated for the person.

## PLAYER → `players/NN-slug.md` (max {PLAYER_WORDS} words)
1. **Facts:** the numbers the plan stands on, each with its source and date (or [est]).
2. **The business in one paragraph:** what is sold, to whom, and why this person.
3. **Unit economics:** price, cost and margin per unit, order or client.
4. **Plan:** setup cash, itemised and within the cap; then months 1–3, 4–6 and 7–{HORIZON}, with targets.
5. **Decision rules:** 8–12 lines of the form "if X by month N → do Y". The world applies them without you.
6. **Growth path** beyond the target: what must be true, and the main steps.
7. **Five riskiest assumptions,** each with a confidence %.
8. **Two-week real-world test:** the steps, the cost, and the numbers that mean continue or stop.

## WORLD → `worlds/NN-slug.md` (max {WORLD_WORDS} words)
You are the market: neither the player's friend nor its enemy.
1. Read `profile.md`, `rules.md`, `facts.md` (if present), the field file and the player's file.
2. **Check the five assumptions the plan depends on most** with your own searches. Mark each one holds / partly / fails, with its source, and simulate with your verified numbers.
3. **Simulate months 1–{HORIZON} as one realistic run.**
   - Apply the player's decision rules. Where they are silent, act as a sensible founder with this profile would.
   - Most prospects say no, deals slip, and suppliers re-price.
   - Inject 3–6 realistic events, good and bad, each with a reason.
   - Respect the person's hours and cash. Cash never goes below zero.
   - Table: month | what happened | customers/orders | revenue | costs | net profit | cash | hours/week.
4. **Years 2–3 by quarter:** what has to happen to grow, and whether it plausibly does.
5. **Results in words:** the binding constraint, where the plan broke, and a one-line verdict.
6. **End with this exact machine-readable block.** Use numbers in the profile's main currency, months as `M<n>` or `none`, and probabilities in %.

   - `p_any` is the chance of **at least one** month at the target.
   - `p_avg` is the chance of a **3-month average** at the target.

```results
first_profit_month: M6
first_target_month: none
m12_net_base: 290
m12_net_bad: 0
m12_net_good: 700
y3_net_base: 1800
peak_cash: 2400
hours_per_week: 30
p_any_m6: 3%
p_any_m12: 27%
p_avg_m12: 10%
binding_constraint: margin per kit and the 30 h/week cap
verdict: closest field, but the target needs a hard summer
```

## JUDGE → `judge/verdict.md` (max {JUDGE_WORDS} words)
Read `profile.md`, `rules.md`, `scoreboard.md` and every `worlds/*.md`. Read `players/*.md` only for the top three in the scoreboard. Trust the worlds over the players, and penalise assumptions that failed checks.
1. **Bottom line** in two sentences. If no field reaches the target within {HORIZON} months, say so plainly and name the closest.
2. **Scoreboard:** keep the script's table, adding a fit score (1–5) and the top risk for each field.
3. **Ranking:** one line each.
4. **Winner and runner-up:** why, and the single change that raises the winner's odds most.
5. **Combinations:** two fields that share customers, supply or skills, if the files support it, with the hours it would take.
6. **What the simulation cannot tell:** e.g. whether anyone will pay this person, shocks, network depth, real hours.
7. **14-day real-world tests** for the winner (and the runner-up): day-by-day steps, cost, and the numbers that mean continue or stop.
8. **Why each of the others loses:** one line each.

Be blunt and calibrated. Never inflate a probability to give hope.
