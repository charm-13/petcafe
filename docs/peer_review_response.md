# Peer Review Responses
## Schema/API Design
### Issue #8:
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
_LGTM_ yay :)
#### Users
/users/{user_id}/delete
1. _I'm not sure you want to have this endpoint. It leaves the door open for a malicious user to iterate over id's and start deleting users. IF you do want to keep this functionality, then I'd suggest making your user id's in `/users/create` generate id's that are more unique and harder to guess._
<br>We do want to keep this functionality. We implemented user authentication (users will have to sign up/in with a username and password). This endpoint would be fixed to account for this possibility.
/users/{user_id}/creatures/{creature_id}/feed/{treat_sku}
1. _This endpoint is vulnerable to idempotency issues. Consider requiring the client to pass in a unique transaction id with each call and then check if that call has already been made before making any changes to data._
<br>? revisit

### Issue #17

1. _The user has an inventory of snacks that never runs out (if the user buys a snack it will always show up in their inventory when they call GET /users/{user_id}/inventory and can't be removed) so the fact that PUT /carts/{cart_id}/items/{item_sku} requests that the user to input a quantity of snacks is pointless since the code doesn't seem to check if the user has enough snacks to feed the creatures and will just let the user continuously feed creature until their hunger level reaches 100._
<br>Not true because we change quantity in the feed endpoint

2. _Going back to the previous point GET /users/{user_id}/inventory should also show how many of a specific snack the user has in their inventory if you are going to be asking the user how many of a certain snack they want to buy in PUT /carts/{cart_id}/items/{item_sku}._
<br>To be fixed

3. _Right now adopting a creature doesn't seem serve a purpose other than changing is_adopted from false to true. You could use it to unlock other special interactions with the creatures you can only do if you adopt a creature._
<br>Addressed in our new endpoints

4. _The users_treat_inventory table referenced in creatures.py for the feed_creature() function is not in the schema.sql file._
<br>To be fixed

5. _Instead of returning a boolean for play_success and feed_success when playing with or feeding a creature you can throw an error saying that the happiness or hunger respectively are maxed and won't raise the creature's affinity. To be more explicit about what's happening._
<br>To be fixed

6. _Currently, it doesn't seem like username is being used for anything after being created._
<br>Username is not a required field anymore

7. _It would be a good idea to specify that POST /carts/{cart_id}/checkout should only be called once for a specific cart. Since there would no need to keep the cart around unless you want to add an order history for all users._
<br>We are changing the logic for cart checkouts to fix this

8. _When setting up the creatures table in schema.sql there are default values for happiness that don't seem to be used when starting off._
<br>They are used to start the creatures off at max happiness, then happiness goes down if they are not played with or fed for certain intervals of time

9. _I noticed that there is an seemingly unused health column when setting up the creatures table in schema.sql. Could this be used later? For example, you could create a battle function using the health._
<br>We got rid of the health column because we have no intention of using it

10. _I think that all the creatures should start off lower hunger and happiness values. That way the user doesn't hit a metaphorical brick wall maxing out happiness and hunger pretty much immediately after starting off._
<br>These values go down periodically so the user would just have to wait to be able to interact with the creatureagain

11. _In POST /users/{user_id}/creatures/{creature_id}/feed/{treat_id} you could also return a string with the creature's response to the treat it was just fed to make it more clear to the user if the creature liked the treat it was just fed._
<br>To be fixed

12. _Since DELETE /users/{user_id}/delete takes in the user_id as input you should specify that with a request block alongside the response block in APISpec.md_
<br>Resolved

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
Done
2. _The check to make sure the cart_id exists can also be done in that one sql query. A psycopg2.errors.ForeignKeyException is thrown if it attempts to insert a cart_id that doesnt exist in carts or an item_sku that doesn't exist in treats. Consider catching that error and returning an appropriate error message._
Done
3. _No checks being done on the quantity. This means the user can add negative quantities and then get gold when they checkout._
Done. Now, the user must input a quantity of 1 or greater.
/carts/{cart_id}/checkout/
1. _Code does not check if the user associated with this cart can afford to checkout. This allowed me to checkout an item and then go into debt (negative gold)._

2. _Same cart can be checked out multiple times (though I guess this could be a feature not a bug if you want)_

3. _The 4 database calls here can be collapsed into two. The first updates the users gold, and the second to insert into users_treat_inventory. The check to make sure the cart exists, calculating the total paid,  total bought can also be done in one sql query._

#### Catalog
/catalog/
- LGTM

#### Users
/users/create/

1. _Wrap in a try except block._ 

2. _Consider checking username requirements. e.g length is greater than 0 but less than 20 char_

/users/{user_id}/delete
- _LGTM_

/users/{user_id}/inventory/

1. _Wrap db connection in try-catch block_

2. _Combine the 3 SELECT queries into one select query to reduce the number of round trips you're making to the db._ 

#### Creatures
/users/{user_id}/creatures/
1. Wrap the db.engine.begin() in a try-except block

2. Current sql query allows you to check the petcafe of a non-existent user_id. Consider modifying the SQL query to check if the user_id exists and throw an exception if it does not.

/users/{user_id}/creatures/{creature_id}/stats
1. _Wrap the db.engine.begin() in a try-except block_

2. _Consider checking if the creature_id exists in the creatures table. An Internal Server error occurs currently when providing a bad creature_id._ 

/users/{user_id}/creatures/{creature_id}/feed/{treat_sku}
1. _Wrap the db.engine.begin() in a try-except block_

2. _Both the stats and inventory queries can be combined into 1 query. Use a WITH block and move the inventory query into that. And then in the stats query, you can just select those rows from that query._

/users/{user_id}/creatures/{creature_id}/play
1. _Wrap the db.engine.begin() in a try-except block_

2. _Check if the creature_id is valid otherwise an Internal Server error occurs._

3. _Consider checking if the database connections and queries were successful and throw an exception if they were not._

/users/{user_id}/creatures/{creature_id}/adopt
1. _Wrap the db.engine.begin() in a try-except block_

### Issue #16

#### carts.py
1. _set_item_quantity() should have a check for if the user has enough gold to make a purchase. However since users start off with 0 gold if they buy anything they end up having negative gold. Unless you plan on implementing something about the user going into debt. Since you can currently buy any amount of the most expensive item essentially for free._
<br>This will be fixed with the new purchase logic

2. _The set_item_quantity() function should return a much more human readable error message when the user enters an item_sku that doesn't exist in the catalog. For example, you could return something like "We don't sell {item_sku} here." or "{item_sku} does not exist in the snack catalog"._
<br>Resolved

3. _(Similar to the previous comment) checkout() should also return a more human readable error when it fails. For example if the user enters a cart_id that doesn't belong to any existing cart it can return something like this:
{"error": "No cart with this id ({cart_id})  exists"}_
<br>Resolved

4. _Carts aren't being deleted after checkout() is called meaning that you can repeatedly purchase what ever gets added to the user's cart. After the user purchases the treats they want there is no need to keep their cart around._
<br>This will be fixed with the new purchase logic

#### creatures.py
1. _feed_creature() doesn't check if the user even has any treats to feed creatures. So buying snacks is pointless if your know what snacks are in the catalog. You should return an error message like "You don't have any snacks to feed them" if the user doesn't have any snacks._
<br>Not true, we do check for this and success shows 'False' if they don't have the treat

2. _In feed_creature() you pass in an item_sku, but you don't check if the user actually have that specific item in their inventory. Although with the way this function is currently implemented the user can pass in any item_sku that is the snack catalog and be able to feed the creatures without having that specific item in their inventory. For example, if the user buys a STEAK_SKEWER right after creating their then calls POST /users/{user_id}/creatures/{creature_id}/feed/{treat_id} while passing in RAZZ_BERRY as the treat_id they can feed the creature a razz berry without having one in their inventory_
<br>Addressed above

3. _feed_creature() Also doesn't check how many of the passed in snack the user has in their inventory. So they could just buy one random snack and continuously call POST /users/{user_id}/creatures/{creature_id}/feed/{treat_id} until the creature's hunger level reaches 100 where it stops them._
<br>Not true, quantity is updated on each call to accurately reflect how much the user has

4. _Although this might just be a personal preference, you could make it more explicit that if the creature liked the treat it was just fed when you call POST /users/{user_id}/creatures/{creature_id}/feed/{treat_id}. You could return a message with a response from the creature. For example, if the creature hated the you could return a message like "{creature_name} tossed the {treat_name} aside" or if they where feed their favorite treat "{creature_name} devoured the {treat_name}"_
<br>We will have a message in the response body for this

5. _play_with_creature() doesn't check if the user enters an invalid user_id or creature_id and returns and Internal Server Error if either of these values aren't in the table in this query_

`
stats = connection.execute(sqlalchemy.text("""SELECT happiness, COALESCE(user_creature_connection.affinity, 0) AS affinity
                                                FROM creatures 
                                                JOIN creature_types 
                                                    ON creatures.type = creature_types.type AND creatures.id = :creature   
                                                LEFT JOIN user_creature_connection 
                                                    ON creatures.id = user_creature_connection.creature_id AND user_id = :user_id"""),
                                                {"creature": creature_id, "user_id":user_id}).mappings().fetchone()`
#### users.py
1. _The DELETE query in delete_user() doesn't need to be formatted. Since it can easily fit in one line and just a readable on most displays._
<br>We are trying to use a formatting convention for our queries, which means that it might remain a multi line query f

2. _create_user() Can accept an empty string ("") as a username. Which doesn't seem to affect anything right now, but you should keep that in mind if you want to implement anything using the username in the future. So it would be a good idea to come up with some guidelines for creating a username._
<br>Resolved

#### More general comments
_You could move all your BaseModel (i.e NewUser and CartItem) Classes to the top of each file to improve readability._
<br>We like the idea of keeping them right above the function/s that use that BaseModel

## Test Results
### Issue #9

## Product Ideas
### Issue #10
- _Creature breeding and discovering new creatures. A new endpoint for if a user has adopted two creatures, they can breed the two and get a new baby creature. The endpoint would take in the two creatures and generate some new creature based on their characteristics and add it to the creatures table._
<br>We used this idea to make one of our complex endpoints, users can now breed two creatures that they've adopted together

- _Creature marketplace. Create a creature marketplace that the user can view by calling an endpoint. This returns a list of creatures, their stats, and how much gold a creature would cost to purchase. You could also create an endpoint for a user to list their own (adopted) creatures on the marketplace._
<br>The idea is that there are a fixed number of creatures, each one will always stay in the cafe. The marketplace would require a complete rework of how the game works.

### Issue #11

_Create an endpoint that can slowly lower the affinity levels of the pets over time if the user hasn't interacted with them in a significant amount of time. Which can be called every hour or some other specified amount of time. In order to encourage the user to regularly interact with the pet._
<br>We might implement this as a cron job later

_Create an endpoint that allows for a special interaction with the pet once they are adopted like being able to rename the pet for example. Or being able to release the pet. Since currently adopting pets has no purpose other than saying that you adopt them all. Or even add the ability for an adopted pet to play with non-adopted pets._
<br>We created the breeding and evolution endpoints so adoption can lead to something now