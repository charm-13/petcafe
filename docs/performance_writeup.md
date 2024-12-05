## Fake Data Modeling
**[Python file for constructing a million rows](github.com/charm-13/petcafe/blob/main/src/scripts/populate_db.py)**

### Tables:
1. Creature_types - Kept types the same to lend more room for unique possible combinations while breeding
2. Creatures - Added 1000 fake creatures for users to choose from.
3. Evolution_stages - Stayed the same to maintain the standard 3 evolution stages
4. Purchases - Added 100,000 rows. On average, a user might make 50 treat purchases to feed creatures. The purchase quantity would go up in later purchases due to having more gold, leading to them needing to eventually make less purchases
5. Treats - Kept treats the same
6. User_creature_connection - Added 200,000 rows, estimating that a user will play with on average 100 creatures.
7. User_gold - Added 400,000 rows. This is a ledgerized table, so we added 200 rows per user to account for possible purchases and pet interactions.
8. Users - Added 2000 fake users, gives us a large and realistic sense of how many people might play this game
9. Users_inventory - Added 300,000 rows. This is a ledgerized table for user treats, so added 150 rows per user as an estimated average of treat purchases and feeding creatures.

## Performance Results of Endpoints

### Users
1. **/users/register:** (2 queries) 0.386 + 0.23 = 0.616ms
2. **/users/login:** N/A (no queries)
3. **/users/remove:** (1 query) 44.719ms
4. **/users/inventory:** (2 queries) 13.146 + 16.689 = 29.835ms
5. **/users/adoptions:** (1 query) 0.974ms

### Creatures
1. **/creatures/:** (1 query) 2.323ms
2. **/creatures/{creature_id}/stats:** (1 query) 1.08ms
3. **/creatures/{creature_id}/feed/{treat_sku}:** (6 queries) 19.901 + 1.103 + 0.374 + 0.665 + 0.867 + 0.907 = 23.817ms
4. **/creatures/{creature_id}/play:** (4 queries) 1.309 + 0.398 + 0.509 + 0.731 = 2.947ms
5. **/creatures/{creature_id}/adopt:** (2 queries) 1.023 + 0.541 = 1.564ms
6. **/creatures/breed:** (4 queries) 1.207 + 0.954 + 0.914 + 0.974 = 4.049ms
7. **/creatures/{creature_id}/evolve:** (2 queries) 1.219 + 0.755 = 1.974ms

### Shop
1. **/shop/catalog/:** (1 query) 0.267ms
2. **/shop/purchase:** (4 queries) 14.411 + 6.857 + 0.756 + 0.957 = 22.981ms

### Slowest Endpoints
1. /users/remove
2. /users/inventory
3. /creatures/{creature_id}/feed/{treat_sku}

## Performance Tuning
### 1. /users/remove
#### `EXPLAIN ANALYZE DELETE FROM users WHERE id = {user_id}`
```
Delete on users  (cost=0.28..8.29 rows=0 width=0) (actual time=0.127..0.127 rows=0 loops=1)
  ->  Index Scan using users_pkey on users  (cost=0.28..8.29 rows=1 width=6) (actual time=0.035..0.035 rows=1 loops=1) |
        Index Cond: (id = {user_id}::uuid)
Planning Time: 0.241 ms
Trigger for constraint purchases_user_id_fkey: time=5.846 calls=1
Trigger for constraint user_creature_connection_user_id_fkey: time=0.697 calls=1
Trigger for constraint user_gold_user_id_fkey: time=19.090 calls=1
Trigger for constraint users_inventory_user_id_fkey: time=15.073 calls=1
Execution Time: 40.913 ms
```
The query scans the user table to find the specific id
#### Index
```
CREATE INDEX idx_users ON users (id, username)
```

#### Rerun explain
```
"Delete on users  (cost=0.28..8.29 rows=0 width=0) (actual time=0.177..0.177 rows=0 loops=1)"
"  ->  Index Scan using idx_users on users  (cost=0.28..8.29 rows=1 width=6) (actual time=0.040..0.041 rows=1 loops=1)"
"        Index Cond: (id = 'b6513257-84ce-493f-919f-0b23af442633'::uuid)"
"Planning Time: 0.347 ms"
"Trigger for constraint purchases_user_id_fkey: time=7.449 calls=1"
"Trigger for constraint user_creature_connection_user_id_fkey: time=3.502 calls=1"
"Trigger for constraint user_gold_user_id_fkey: time=0.534 calls=1"
"Trigger for constraint users_inventory_user_id_fkey: time=0.500 calls=1"
"Execution Time: 12.247 ms"
```
This had the expected results. It still isn't the fastest amongst the endpoints but the performance improved by more than half.
### 2. /users/inventory
#### 1. `EXPLAIN ANALYZE SELECT username, gold FROM users AS u JOIN gold_view AS g ON g.user_id = u.id AND u.id = {user_id}`
```
Nested Loop  (cost=1000.56..6456.46 rows=1 width=18) (actual time=10.000..12.596 rows=1 loops=1)
  ->  Index Scan using users_pkey on users u  (cost=0.28..8.29 rows=1 width=26) (actual time=0.030..0.031 rows=1 loops=1)
        Index Cond: (id = {user_id}::uuid)
  ->  GroupAggregate  (cost=1000.28..6448.14 rows=1 width=24) (actual time=9.967..12.561 rows=1 loops=1)
        Group Key: u_1.id
        ->  Nested Loop Left Join  (cost=1000.28..6448.13 rows=1 width=20) (actual time=7.190..12.539 rows=207 loops=1)
              Join Filter: (g.user_id = u_1.id)
              ->  Index Only Scan using users_pkey on users u_1  (cost=0.28..8.29 rows=1 width=16) (actual time=0.016..0.020 rows=1 loops=1)
                    Index Cond: (id = {user_id}::uuid)
                    Heap Fetches: 1
              ->  Gather  (cost=1000.00..6437.33 rows=200 width=20) (actual time=7.172..12.492 rows=207 loops=1)
                    Workers Planned: 2
                    Workers Launched: 2
                    ->  Parallel Seq Scan on user_gold g  (cost=0.00..5417.33 rows=83 width=20) (actual time=5.159..6.912 rows=69 loops=3)
                          Filter: (user_id = {user_id}::uuid)
                          Rows Removed by Filter: 133267
Planning Time: 0.920 ms
Execution Time: 12.701 ms
```
The query first scans the user table to find the username and then joins the gold view where it scans each record. 

#### Index
```
CREATE INDEX idx_user_gold_id ON user_gold (user_id)
```

#### Rerun explain
```
"Nested Loop  (cost=6.52..709.97 rows=1 width=18) (actual time=0.152..0.153 rows=1 loops=1)"
"  ->  Index Scan using idx_users_id on users u  (cost=0.28..8.29 rows=1 width=26) (actual time=0.016..0.016 rows=1 loops=1)"
"        Index Cond: (id = 'deee2d13-1f2d-47dc-a45e-affe740175df'::uuid)"
"  ->  GroupAggregate  (cost=6.24..701.66 rows=1 width=24) (actual time=0.134..0.135 rows=1 loops=1)"
"        Group Key: u_1.id"
"        ->  Nested Loop Left Join  (cost=6.24..701.64 rows=1 width=20) (actual time=0.083..0.118 rows=200 loops=1)"
"              Join Filter: (g.user_id = u_1.id)"
"              ->  Index Only Scan using idx_users_id on users u_1  (cost=0.28..4.29 rows=1 width=16) (actual time=0.029..0.029 rows=1 loops=1)"
"                    Index Cond: (id = 'deee2d13-1f2d-47dc-a45e-affe740175df'::uuid)"
"                    Heap Fetches: 0"
"              ->  Bitmap Heap Scan on user_gold g  (cost=5.96..694.86 rows=199 width=20) (actual time=0.051..0.065 rows=200 loops=1)"
"                    Recheck Cond: (user_id = 'deee2d13-1f2d-47dc-a45e-affe740175df'::uuid)"
"                    Heap Blocks: exact=2"
"                    ->  Bitmap Index Scan on idx_user_gold_id  (cost=0.00..5.92 rows=199 width=0) (actual time=0.033..0.033 rows=200 loops=1)"
"                          Index Cond: (user_id = 'deee2d13-1f2d-47dc-a45e-affe740175df'::uuid)"
"Planning Time: 0.923 ms"
"Execution Time: 0.271 ms"
```
The execution time is a lot faster as expected.
#### 2. `EXPLAIN ANALYZE SELECT treat_sku AS sku, quantity FROM user_inventory_view WHERE user_id = {user_id} AND quantity > 0`
```
Subquery Scan on user_inventory_view  (cost=5804.73..5819.39 rows=49 width=18) (actual time=10.719..12.964 rows=10 loops=1)
  ->  Finalize GroupAggregate  (cost=5804.73..5818.90 rows=49 width=34) (actual time=10.718..12.961 rows=10 loops=1)
        Group Key: i.user_id, i.treat_sku
        Filter: (COALESCE(sum(i.quantity), '0'::bigint) > 0)
        ->  Gather Merge  (cost=5804.73..5816.39 rows=88 width=34) (actual time=10.707..12.949 rows=20 loops=1)
              Workers Planned: 1
              Workers Launched: 1
              ->  Partial GroupAggregate  (cost=4804.72..4806.48 rows=88 width=34) (actual time=8.485..8.498 rows=10 loops=2)
                    Group Key: i.user_id, i.treat_sku
                    ->  Sort  (cost=4804.72..4804.94 rows=88 width=30) (actual time=8.475..8.478 rows=77 loops=2)
                          Sort Key: i.treat_sku
                          Sort Method: quicksort  Memory: 33kB
                          Worker 0:  Sort Method: quicksort  Memory: 27kB
                          ->  Parallel Seq Scan on users_inventory i  (cost=0.00..4801.88 rows=88 width=30) (actual time=5.037..8.397 rows=77 loops=2)
                                Filter: (user_id = {user_id}::uuid)
                                Rows Removed by Filter: 149925
Planning Time: 0.605 ms
Execution Time: 13.060 ms
```
The query runs a scan on the inventory table to find rows with the user id, then the data is sorted using quicksort. Then it finds the treats where the quantity is 0.
#### Index
```
CREATE INDEX idx_user_inventory_user_id_quantity ON user_inventory (user_id, quantity);
```

#### Rerun explain
```
"Nested Loop Left Join  (cost=5.82..532.10 rows=14 width=54) (actual time=0.127..0.130 rows=1 loops=1)"
"  Join Filter: ((i.treat_sku = treats.sku) AND (i.user_id = users.id))"
"  ->  Nested Loop  (cost=0.28..9.52 rows=1 width=62) (actual time=0.032..0.034 rows=1 loops=1)"
"        ->  Seq Scan on treats  (cost=0.00..1.21 rows=1 width=36) (actual time=0.007..0.009 rows=1 loops=1)"
"              Filter: (sku = 'HONEY'::text)"
"              Rows Removed by Filter: 16"
"        ->  Index Scan using idx_users_id on users  (cost=0.28..8.29 rows=1 width=26) (actual time=0.023..0.024 rows=1 loops=1)"
"              Index Cond: (id = 'deee2d13-1f2d-47dc-a45e-affe740175df'::uuid)"
"  ->  GroupAggregate  (cost=5.54..522.42 rows=14 width=34) (actual time=0.091..0.091 rows=1 loops=1)"
"        Group Key: i.user_id, i.treat_sku"
"        ->  Bitmap Heap Scan on users_inventory i  (cost=5.54..522.17 rows=14 width=30) (actual time=0.072..0.086 rows=15 loops=1)"
"              Recheck Cond: (user_id = 'deee2d13-1f2d-47dc-a45e-affe740175df'::uuid)"
"              Filter: (treat_sku = 'HONEY'::text)"
"              Rows Removed by Filter: 135"
"              Heap Blocks: exact=2"
"              ->  Bitmap Index Scan on idx_user_inventory_user_id_quantity  (cost=0.00..5.54 rows=149 width=0) (actual time=0.051..0.051 rows=150 loops=1)"
"                    Index Cond: (user_id = 'deee2d13-1f2d-47dc-a45e-affe740175df'::uuid)"
"Planning Time: 1.199 ms"
"Execution Time: 0.222 ms"
```
The execution time decreases by a lot as expected.
### 3. /creatures/{creature_id}/feed/{treat_sku}
#### `EXPLAIN ANALYZE SELECT username, sku, satiety, COALESCE(quantity, 0) AS qty FROM treats JOIN users ON users.id = {user_id} AND sku = {treat_sku} LEFT JOIN user_inventory_view AS inv ON inv.treat_sku = sku AND inv.user_id = users.id`
```
Nested Loop Left Join  (cost=1000.43..6260.98 rows=15 width=54) (actual time=13.522..15.748 rows=1 loops=1) 
Join Filter: ((i.treat_sku = treats.sku) AND (i.user_id = users.id)) 
->  Nested Loop  (cost=0.43..16.47 rows=1 width=62) (actual time=0.040..0.048 rows=1 loops=1) 
        ->  Index Scan using treats_sku_key on treats  (cost=0.15..8.17 rows=1 width=36) (actual time=0.013..0.015 rows=1 loops=1) 
            Index Cond: (sku = {treat_sku}::text) 
        ->  Index Scan using users_pkey on users  (cost=0.28..8.29 rows=1 width=26) (actual time=0.025..0.030 rows=1 loops=1) 
            Index Cond: (id = {user_id}::uuid) 
->  Finalize GroupAggregate  (cost=1000.00..6244.33 rows=15 width=34) (actual time=13.477..15.694 rows=1 loops=1) 
        Group Key: i.user_id, i.treat_sku 
        ->  Gather  (cost=1000.00..6244.12 rows=9 width=34) (actual time=13.355..15.686 rows=2 loops=1) 
            Workers Planned: 1 
            Workers Launched: 1 
            ->  Partial GroupAggregate  (cost=0.00..5243.22 rows=9 width=34) (actual time=10.516..10.517 rows=1 loops=2) 
                    Group Key: i.user_id, i.treat_sku 
                    ->  Parallel Seq Scan on users_inventory i  (cost=0.00..5243.06 rows=9 width=30) (actual time=6.635..10.498 rows=8 loops=2) 
                        Filter: ((treat_sku = {treat_sku}::text) AND (user_id = {user_id}::uuid)) 
                        Rows Removed by Filter: 149994 
Planning Time: 0.974 ms 
Execution Time: 15.844 ms 
```
The query joins the users and inventory tables together and scans for the treat sku and user id.
#### Index
```
CREATE INDEX satiety_idx on treats (satiety)
```

#### Rerun explain
```
"Nested Loop Left Join  (cost=5.82..532.10 rows=14 width=54) (actual time=0.132..0.135 rows=1 loops=1)"
"  Join Filter: ((i.treat_sku = treats.sku) AND (i.user_id = users.id))"
"  ->  Nested Loop  (cost=0.28..9.52 rows=1 width=62) (actual time=0.052..0.055 rows=1 loops=1)"
"        ->  Seq Scan on treats  (cost=0.00..1.21 rows=1 width=36) (actual time=0.023..0.024 rows=1 loops=1)"
"              Filter: (sku = 'HONEY'::text)"
"              Rows Removed by Filter: 16"
"        ->  Index Scan using idx_users_id on users  (cost=0.28..8.29 rows=1 width=26) (actual time=0.027..0.028 rows=1 loops=1)"
"              Index Cond: (id = 'deee2d13-1f2d-47dc-a45e-affe740175df'::uuid)"
"  ->  GroupAggregate  (cost=5.54..522.42 rows=14 width=34) (actual time=0.076..0.076 rows=1 loops=1)"
"        Group Key: i.user_id, i.treat_sku"
"        ->  Bitmap Heap Scan on users_inventory i  (cost=5.54..522.17 rows=14 width=30) (actual time=0.055..0.070 rows=15 loops=1)"
"              Recheck Cond: (user_id = 'deee2d13-1f2d-47dc-a45e-affe740175df'::uuid)"
"              Filter: (treat_sku = 'HONEY'::text)"
"              Rows Removed by Filter: 135"
"              Heap Blocks: exact=2"
"              ->  Bitmap Index Scan on idx_user_inventory_user_id_quantity  (cost=0.00..5.54 rows=149 width=0) (actual time=0.033..0.033 rows=150 loops=1)"
"                    Index Cond: (user_id = 'deee2d13-1f2d-47dc-a45e-affe740175df'::uuid)"
"Planning Time: 1.328 ms"
"Execution Time: 0.237 ms"
```
The execution time is a lot faster as expected.