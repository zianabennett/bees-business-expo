# Data definitions

The inputs belong to the independent exercise described in the [case study](../README.md). Both JSON files are readable without additional software. The reporting script reads them and writes a static Markdown report; it does not update statuses or contact participants.

## Vendor records

[vendors.json](vendors.json) contains 16 records and a 14-booth inventory. The T-6 review uses deadlines stored as integer days relative to the event day, T=0.

| Field | Meaning |
|---|---|
| `id` | Unique vendor record identifier |
| `name` and `category` | Descriptive labels for the scenario |
| `participation` | `confirmed`, `invited`, or `declined` |
| `setup_information_received` | Whether the required setup details are recorded |
| `power_required` | Whether this vendor requests power |
| `power_approved` | Whether the requested arrangement is approved; irrelevant when power is not required |
| `booth_id` | An inventory identifier, or `null` when unassigned |
| `arrival_window_confirmed` | Whether arrival details have been confirmed |

Confirmed vendors consume capacity before a booth is assigned. Only confirmed vendors may hold an assignment in this model. Duplicate booth assignments are accepted as an operational exception and explicitly block the affected vendors; unknown booth IDs and duplicate vendor IDs are rejected as invalid input.

## Budget records

[budget.json](budget.json) stores amounts as nonnegative integer cents in USD. Using cents avoids floating-point arithmetic in the financial calculations.

| Field | Meaning |
|---|---|
| `planned_cents` | Category allocation excluding contingency |
| `paid_cents` | Costs already paid |
| `committed_unpaid_cents` | Obligations incurred but not yet paid |
| `remaining_estimate_cents` | Additional expected cost not included in either prior state |
| `contingency_cents` | Separate allowance that increases the total ceiling |
| `incremental_cents` | Additional exposure above the baseline forecast in the separate scenario |

Each cost must occupy one state. When paying an existing commitment, increase paid costs and reduce committed costs by the same amount. Forecast equals paid plus committed unpaid plus remaining estimate. Category variance equals forecast minus plan. Positive variance means an overrun against that category's allocation.

The code checks types, nonnegative amounts, and identifiers. It cannot determine whether a person entered the same real expense twice under different categories. That remains a record-review responsibility.

[Generated report](../outputs/operations-report.md) · [Operating brief](../docs/operations-brief.md)
