# Peer Review Responses
## Schema/API Design
### Issue #8
#### Tables
1. _Consider decoupling users from their gold. This means making a table called sometihng like user_gold that is a ledger of all gold changes for every user. You can then create a view which aggregates the ledger and groups by user to get every users gold._
  <br>Yes [explain more]
2. _Consider decoupling the is_adopted column from the user_create_connections table. Instead, you can have a table called users_adopted which can be a ledger with users and any creatures they've adopted. Any new adoptions get inserted into the ledger. Checking if a user has a creature adopted is then just a query into the users_adopted ledger._
  <br>Since adoption is a boolean value that will not frequently change, we will keep it in the user_creature_connections table. The benefits of ledgerizing that column do not outweigh the cons.
3. _Consider decoupling the creatures table from their attributes and then storing those attributes in a seperate table as a ledger that way you can see all the changes in a creatures attribute and what caused it. You can also create a view from which you can aggregate your ledger to get the attributes of any character._
  <br>Since each creature's stats update every hour, ledgerizing that table would take up too much space (especially for such a small-scale project).
4. _Consider updating your users_treat_inventory to a ledger so you can get a history of any users inventory status._
  <br>Yes [explain more]
5. _carts_items can also be a ledger if you want_
  <br>Yes [explain more]

#### Carts
/carts/
1. _This endpoint does not have to require the user to pass in a username. Backend should be able to derive username from just the user_id. But username value doesn't seem to be necessary for your code regardless._
<br>This is true. We removed username as a required field.
2. _This endpoint is vulnerable to idempotency issues. Consider requiring the client to pass in a unique transaction id with each call and then check if that call has already been made before making any changes to data._
<br>? revisit
3. _Every endpoint except this one that requires a user_id takes the user_id in the URL. This endpoint takes it in the text box. Consider making it take the user_id in the URL for your endpoints to be more consistent with one another._
<br>Yes [explain more]. This can be applied to the entire carts.py module
/carts/{cart_id}/items/{item_sku}
1. _Current implementation allows you to add items to a cart that has already been checked out. Consider making a completed_carts table and updating it with cart_id's that have been checked out._
<br>We plan to change implementation of treat buying that will combine checkout and item quantity endpoints. That change will fix this issue.
2. _This endpoint is vulnerable to idempotency issues. Consider requiring the client to pass in a unique transaction id with each call and then check if that call has already been made before making any changes to data._
<br>? revisit
/carts/{cart_id}/checkout/
1. See tables 1

#### Catalog
_LGTM_ <br>yay :)

#### Users
/users/{user_id}/delete
1. _I'm not sure you want to have this endpoint. It leaves the door open for a malicious user to iterate over id's and start deleting users. IF you do want to keep this functionality, then I'd suggest making your user id's in `/users/create` generate id's that are more unique and harder to guess._
<br>We do want to keep this functionality. We implemented user authentication (users will have to sign up/in with a username and password). This endpoint would be fixed to account for this possibility.
/users/{user_id}/creatures/{creature_id}/feed/{treat_sku}
1. _This endpoint is vulnerable to idempotency issues. Consider requiring the client to pass in a unique transaction id with each call and then check if that call has already been made before making any changes to data._
<br>? revisit

## Code Review
### Issue #7
#### Carts
/carts/
1. _Consider wrapping your db connection with a try, except block here to support error handling._ 
Connections are wrapped in a try/except now.
2. _Currently, there is a 500 thrown if a user enters a user_id that is not in users. This is likely due to a foreign key  exception that occurs when a user attempts to create a cart with a user_id that is not in users. Consider catching this error and returning a helpful error message._
Fixed. Now it checks that user_id exists before inserting.
/carts/{cart_id}/items/{item_sku}
1. _Select and insert query could be combined into 1 to reduce db calls._ 
<br>Done
2. _The check to make sure the cart_id exists can also be done in that one sql query. A psycopg2.errors.ForeignKeyException is thrown if it attempts to insert a cart_id that doesnt exist in carts or an item_sku that doesn't exist in treats. Consider catching that error and returning an appropriate error message._
<br>Done
3. _No checks being done on the quantity. This means the user can add negative quantities and then get gold when they checkout._
<br>Done. Now the user must input a quantity of 1 or greater.
/carts/{cart_id}/checkout/
1. _Code does not check if the user associated with this cart can afford to checkout. This allowed me to checkout an item and then go into debt (negative gold)._
<br>The code now checks that users have enough gold!
2. _Same cart can be checked out multiple times (though I guess this could be a feature not a bug if you want)_
<br> Since we cart rework, no carts can be checked out twice.
3. _The 4 database calls here can be collapsed into two. The first updates the users gold, and the second to insert into users_treat_inventory. The check to make sure the cart exists, calculating the total paid,  total bought can also be done in one sql query._
<br>db connections are collapsed!

## Catalog
/catalog/
- _LGTM_
<br>yay :)

## Users
/users/create/
1. _Wrap in a try except block._ 
<br>Done
2. _Consider checking username requirements. e.g length is greater than 0 but less than 20 char_
<br>Done. Now the username must be between 5 and 20 characters. If it is outside that range, the endpoint returns an error.
/users/{user_id}/delete
- _LGTM_
<br>yay :)

/users/{user_id}/inventory/
1. _Wrap db connection in try-catch block_
<br>Done
2. _Combine the 3 SELECT queries into one select query to reduce the number of round trips you're making to the db._ 
<br>Good idea. We decided to split up the endpoint into 2 different ones. One is to get the user's username, gold, and treat inventory. The other gets the names of the adopted pets.

## Creatures
/users/{user_id}/creatures/
1. _Wrap the db.engine.begin() in a try-except block_
<br>Done
2. _Current sql query allows you to check the petcafe of a non-existent user_id. Consider modifying the SQL query to check if the user_id exists and throw an exception if it does not._
<br>

/users/{user_id}/creatures/{creature_id}/stats
1. _Wrap the db.engine.begin() in a try-except block_
<br>Done
2. _Consider checking if the creature_id exists in the creatures table. An Internal Server error occurs currently when providing a bad creature_id._ 
<br>

/users/{user_id}/creatures/{creature_id}/feed/{treat_sku}
1. _Wrap the db.engine.begin() in a try-except block_
<br>Done
2. _Both the stats and inventory queries can be combined into 1 query. Use a WITH block and move the inventory query into that. And then in the stats query, you can just select those rows from that query._
<br> ?

/users/{user_id}/creatures/{creature_id}/play
1. _Wrap the db.engine.begin() in a try-except block_
<br>Done
2. _Check if the creature_id is valid otherwise an Internal Server error occurs._
<br>
3. _Consider checking if the database connections and queries were successful and throw an exception if they were not._
<br>

/users/{user_id}/creatures/{creature_id}/adopt
1. _Wrap the db.engine.begin() in a try-except block_
<br>Done

## Test Results
### Issue #9

## Product Ideas
### Issue #10
- _Creature breeding and discovering new creatures. A new endpoint for if a user has adopted two creatures, they can breed the two and get a new baby creature. The endpoint would take in the two creatures and generate some new creature based on their characteristics and add it to the creatures table._
<br>Yes [explain more]

- _Creature marketplace. Create a creature marketplace that the user can view by calling an endpoint. This returns a list of creatures, their stats, and how much gold a creature would cost to purchase. You could also create an endpoint for a user to list their own (adopted) creatures on the marketplace._
<br>The idea is that there are a fixed number of creatures, each one will always stay in the cafe. The marketplace would require a complete rework of how the game works.
