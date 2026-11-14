# Required test cases to implement

This file tracks the cases from the take-home brief. No automated tests are implemented in this scaffold yet.

- Equal split of 100.00 among three members allocates 33.34, 33.33, 33.33 and leaves zero-sum balances.
- Reject exact shares that do not sum to the expense amount.
- Reject amounts with more than two decimal places.
- Repeating an idempotency key creates only one expense, including concurrent requests.
- Alice cannot read or write group 2.
- Only the payer can soft-delete an expense.
