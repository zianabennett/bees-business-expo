# Decision analysis

The [generated report](../outputs/operations-report.md) identifies six blocked confirmed vendors and a small financial exposure beyond the total allowance. The appropriate response depends on the type of gap. Treating every incomplete row as equally urgent would hide important dependencies.

## Resolve the first dependency for Alder and Ink

V005 lacks setup information, a booth assignment, and an arrival confirmation. Its setup information was due at T-10, making that request four days overdue at the T-6 review. The next action is to obtain the missing information, not send three unrelated reminders.

The vendor coordinator should ask for the specific outstanding setup requirements, confirm when they will be available, and update the record. Placement can then proceed using the actual requirements. This preserves a clear owner and avoids presenting an incomplete assignment as a finished task.

## Separate a power requirement from a generic missing field

V008 has a booth and an arrival plan, but its requested power arrangement is unapproved. The deadline was T-7. The logistics lead must establish an approved arrangement or agree on a feasible change with the vendor before marking the record ready.

The model does not require approvals from vendors who need no power. That distinction prevents a blanket checklist from creating unnecessary work while retaining the condition that matters for this vendor.

## Correct the B06 conflict before reporting readiness

V006 and V007 both occupy B06 in the input data. Both have otherwise complete records. Counting them as ready would make the preparation percentage look better while leaving the event with an unresolved physical conflict.

The logistics lead should confirm the vendors' requirements, select a compatible available booth for one, and communicate the change. In a business-rule test, changing V007's assignment to B07 removes the conflict and raises readiness from six to eight vendors. That calculation demonstrates the rule's effect; compatibility still requires human review because the current inventory does not model booth characteristics.

## Control commitments before closing invitations

The model has 14 places and 12 confirmed vendors. Three invitations remain open. Confirming all three would exceed capacity by one, even though the assignment list appears to contain several empty booth IDs.

The event lead should review invitation commitments before outreach closes the remaining decisions. One option is to confirm only the number of vendors the event can accommodate and use a transparent waiting process for the remaining invitation. Increasing capacity is another option only if space, logistics, and cost constraints permit it. The model deliberately does not select which business should receive priority because it contains no agreed selection criteria.

## Review the baseline and the additional exposure separately

The $1,235 baseline forecast includes $515 paid, $560 committed but unpaid, and $160 still estimated. It exceeds the $1,200 category plan by $35 but remains below the $1,350 total ceiling. Supplies contribute a $40 overrun and refreshments contribute $20. Favorable category variances offset part of the increases.

This position supports a targeted review rather than an indiscriminate spending freeze. The finance lead should check the supplies and refreshments assumptions and verify that outstanding estimates include the work still needed.

The additional-exposure scenario adds $80 for power support and $50 for supplies. These amounts are incremental to the baseline, not replacements for existing lines. The resulting $1,365 forecast exceeds the ceiling by $15. Before authorizing the full increase, the team needs at least $15 in validated offsets or additional funding. The model does not assume a proposed saving is achievable until someone verifies it.

## What I would carry forward

The operating lesson is to define completion before measuring it, retain the difference between an invitation and a commitment, and examine expected total cost rather than cash paid alone. A next version would record the owner and rationale for each change, making it possible to review how the team resolved exceptions over time.

[Operating brief](operations-brief.md) · [Run of show](run-of-show.md) · [Return to the case study](../README.md)
