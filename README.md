# Black Business Expo Outreach, Operations and Finance

I served on the Finance Committee and later as Finance Chair of the Black Economic Empowerment Society at the University of Virginia. For its Black Business Expo, I helped recruit Black-owned and student businesses through email, phone calls, in-person conversations and flyers. The event brought together 30+ participating businesses and connected them with the campus community.

The project begins with a recruitment question: what would make a business interested in taking part, and what follow-up would help it commit? The independent work samples then connect that outreach to event delivery and financial planning.

**Project scope.** Historical role and outreach context are described above. The playbook, message templates and Python implementation were created afterward as independent portfolio samples. Vendor records, schedules, financial amounts and operating-model results are synthetic. The templates are not messages sent during the original event, and the modeled results do not measure its actual recruitment conversion or financial performance.

## My role and the original context

**UVA Black Economic Empowerment Society · Finance Leadership, Vendor Outreach and Event Coordination**

I served on the Finance Committee and as Finance Chair, and helped lead the Black Business Expo. My experience connected financial responsibility with the coordination needed to bring participating businesses into an event. The historical expo involved 30+ vendors; the smaller dataset below was created specifically to make this new operating model easy to inspect.

The outreach samples show how I would organize prospects, explain the value of participating and follow up on unanswered questions. The operating model then makes readiness and financial exposure visible after a business has committed.

[Portfolio overview](https://zianabennett.github.io/#work) · [Experience and leadership](https://zianabennett.github.io/#experience)

## Explore the Outreach Project

| New sample | What it demonstrates |
|---|---|
| [Recruitment playbook](docs/outreach-playbook.md) | Audience fit, channel choices, follow-up ownership, signup and the handoff to event coordination |
| [Outreach templates](docs/outreach-templates.md) | Adaptable email and call language, in-person conversation guidance, flyer copy and common questions |
| [Visual portfolio case](https://zianabennett.github.io/v2/expo.html) | The original recruitment story alongside the independent planning examples |

The purpose was to help Black-owned and student businesses reach campus buyers and build connections. The historical evidence establishes participation scale and outreach methods; it does not establish channel conversion rates or incremental vendor sales.

## The Operating Problem I Chose to Model

A list of confirmed vendors does not establish that the event is ready. A vendor can still lack setup information, an approved power arrangement, a usable booth, or an arrival plan. Similarly, a low paid-expense total can conceal commitments and upcoming costs.

This project makes those gaps visible at six days before the event. It connects a readiness model to a prioritized action queue and a forecast of total spending. The goal is to identify the decision an organizer should make next, with enough detail for someone else to act on it.

## Start with the results

The [generated operations report](outputs/operations-report.md) contains the complete vendor review, action list, and financial calculations.

| Question | Result in the demonstration |
|---|---|
| How many confirmed vendors are ready? | 6 of 12, or 50% |
| What prevents the others from being ready? | Missing setup information, a pending power request, a duplicate booth assignment, an unassigned booth, and an unconfirmed arrival window |
| Can every open invitation become a commitment? | There are 3 open invitations and capacity for 2 additional vendors |
| Does the baseline forecast fit the spending ceiling? | $1,235 forecast against a $1,350 ceiling, leaving $115 |
| What happens if the additional modeled costs occur? | A $130 increase produces a $1,365 forecast, exceeding the ceiling by $15 |

## Decisions that matter

I would first resolve the overdue setup-information request and pending power arrangement. I would also address the duplicate assignment at booth B06: two otherwise prepared vendors cannot both be counted as ready when they have the same booth. Moving one record to a compatible available booth would resolve that specific conflict for both vendors.

I would review the three outstanding invitations before making further commitments. The model counts all confirmed vendors against capacity, including those whose booth assignments are incomplete. This avoids treating an administrative gap as an available place.

For finance, I would examine the $40 supplies overrun and $20 refreshments overrun while checking the assumptions behind remaining estimates. The baseline fits the total allowance, but the modeled additional exposure does not. Any authorization of that full increase needs an offset or additional funding.

## How the work is organized

- [Operating brief](docs/operations-brief.md) explains scope, readiness rules, dependencies, and responsibilities.
- [Decision analysis](docs/decision-analysis.md) connects the calculated exceptions to recommended actions and tradeoffs.
- [Run of show](docs/run-of-show.md) defines relative dates and completion gates.
- [Data definitions](data/README.md) explain the inputs and financial accounting conventions.

## Reproduce the report

From this repository's directory, run:

```bash
python3 scripts/build_report.py
python3 -m unittest discover -s tests -v
```

The project uses only the Python standard library. The first command rebuilds the Markdown report from the JSON inputs. The tests check operational rules, including conditional power approval, duplicate assignments, capacity commitments, and the treatment of paid versus unpaid costs.

## Limits and next improvement

The model assumes one booth per vendor and does not optimize physical placement. It helps identify decisions; it does not automatically approve vendors or spending. A useful next extension would add booth compatibility and an audit trail showing who changed each status and why.
