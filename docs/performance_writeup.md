# Fake Data Modeling
Should contain a link to the python file you used to construct the million rows of data for your service. Should also contain a writeup explaining how many final rows of data you have in each of your table to get to a million rows AND a justification for why you think your service would scale in that way. There is no single right answer to this, but your reasoning must be justifiable.
### Python file for constructing a million rows: 

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