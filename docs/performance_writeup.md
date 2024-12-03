# Fake Data Modeling
### Python file for constructing a million rows: https://github.com/charm-13/petcafe/blob/main/scripts/populate_db.py
### Tables:
1. Creature_types - Kept types the same to lend more room for unique possible combinations while breeding
2. Creatures - Added in 1000 fake creatures for users to choose from
3. Evolution_stages - Kept the same to maintain the standard 3 evolution stages
4. Purchases - On average, a user might make 50 treat purchases to feed creatures. The purchase quantity would go up in later purchases due to having more gold, leading to them needing to eventually make less purchases
5. Treats - Kept treats the same
6. User_creature_connection - Added in 200,000 rows because a user would probably play with 100 creatures on average
7. User_gold - Added in 400,000 rows. This is a ledgerized table, so we added in 200 rows per user to account for possible purchases and pet interactions.
8. Users - Added in 2000 fake users, gives us a large and realistic sense of how many people might play this game
9. Users_inventory - Added in 300,000 rows. This is a edgerized table for user treats, so added in 150 rows per user as average of treat purchases and feeding creatures

# Performance results of hitting endpoints
For each endpoint, list how many ms it took to execute. State which three endpoints were the slowest.

## Users
1. /users/register
2. /users/login
3. /users/remove
4. /users/inventory
5. /users/adoptions

## Creatures
1. /creatures/
2. /creatures/{creature_id}/stats
3. /creatures/{creature_id}/feed/{treat_sku}
4. /creatures/{creature_id}/play
5. /creatures/{creature_id}/adopt
6. /creatures/breed
7. /creatures/{creature_id}/evolve

## Shop
1. /shop/catalog/
2. /shop/purchase

## Three slowest endpoints
1.
2.
3.

# Performance tuning
For each of the three slowest endpoints, run explain on the queries and copy the results of running explain into the markdown file. Then describe what the explain means to you and what index you will add to speed up the query. Then copy the command for adding that index into the markdown and rerun explain. Then copy the results of that explain into the markdown and say if it had the performance improvement you expected. Continue this process until the three slowest endpoints are now acceptably fast (think about what this means for your service).

1.
2.
3.