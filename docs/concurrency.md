# Concurrency Phenomena

## Case 1: Write Skew - Dual Evolution
This would be the case where multiple different users evolve the same creature at the same time and cause the creature's stage to be invalid.

For example, User A (id `1`), who has adopted the creature named `Blaze` of ID `2`, decides they want to evolve Blaze, who is currently at stage 2, to stage 3.

They call the `/users/1/creatures/2/evolve` endpoint, which begins a transaction that selects Blaze's current stage (`2`), and does several checks to make sure that Blaze meets the requirements for evolution, including that User A has adopted Blaze, Blaze has max hunger and happiness, and Blaze's current stage is less than 3.

In the middle of the those checks, another person, User B (id `2`), who has also adopted Blaze, also decides to evolve the creature. User B calls `/users/2/creatures/2/evolve`, which begins a second transaction that selects Blaze's current stage (`2`), and does those same checks.

Meanwhile, the first transaction (for User A) finishes its checks and does an `UPDATE` to increment Blaze's stage to `3`. Blaze is now considered to be at max stage of evolution.

Afterwards, User B's transaction, which runs and passes the checks on its stored result for Blaze's stage (`2`), also proceeds to `UPDATE` by incrementing Blaze's stage. However, this results in Blaze having a stage of `4`, which is an invalid value.

![Sequence diagram for case 1](case1_concurrency.png)

Since a creature's stage of evolution determines their max happiness and hunger levels (defined by a table), this would create errors the next time anyone calls any creature interaction endpoint that checks Blaze's maximum stats (no associated values with "stage 4").

### Prevention
This could be solved in multiple ways.
- On a database level, PostgreSQL's isolation level could be set to `REPEATABLE READ`. In this example, this would mean that User A's call would acquire a row-level read lock on Blaze's stats in the creatures table during the transaction, preventing User B's call from reading or modifying Blaze's stats until User A's transaction has finished.
- An additional check could be performed by putting `WHERE stage < 3` in the `UPDATE` statement in the endpoint.
- A constraint `stage < 3` could be applied to the `stage` attribute itself in the table definition.

