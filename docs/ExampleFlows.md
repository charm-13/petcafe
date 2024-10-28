## Example flows for the PetCafe

## 1. Pet Cafe User Purchasing Example Flow

The user "dragonluvr5" decides that they want to buy a treat for their favorite dragon in the cafe. They check the cafe catalog to make sure there are multiple treats available. They see the treat "razz berry" costs 50 gold and decide to add 2.
To buy that treat they:
1. Check the catalog by calling ```GET /catalog```
2. Create a cart by calling ```POST /carts``` to get a cart with id `702`,
3. Then they call ```POST /carts/702/items/RAZZ_BERRY``` and pass in a quantity of 2.
4. Then they checkout by calling ```POST /carts/702/checkout``` and jump with glee as the treats enter their inventory. 

## 2. Pet Cafe User-Pet Interaction Example Flow

The user identified by id `475` has the goal of adopting all creatures available, and strategizes by prioritizing interactions with the ones they have the lowest affinity with.
They check their affinity levels with the available creatures and decide to interact with the creature with id `25`, who has an affinity level `20` with the user. They feed the creature `RAZZ_BERRY`s and play with it. Then, they adopt the creature because they have enough affinity with it.
To satisfy the needs of the creature they do the following.

1. Call `POST /users/475/creatures` to view the creatures
2. Call `GET /users/475/creatures/25/stats` to get the creature's current hunger and happiness levels.
3. Feed the creature using a treat by calling `POST /users/475/creatures/25/feed/RAZZ_BERRY`.
4. Play with the creature by calling `POST /users/475/creatures/25/play`.
5. Call `POST /users/475/creatures/25/adopt` to adopt that creature
 

## 3. Pet Cafe User Viewing Example Flow

A user with id `20` wants to view the list of pets that are available to interact with. They view the list and then check their own inventory to see what they have, if they have treats or sufficient gold. They become violently upset at the inventory and the available pets, so they decide to delete their account.

To do these actions, they:
1. Start by calling ```GET /inventory/20``` to view their inventory
2. Then call ```GET /creatures/20``` to view the list of available creatures and their current affinity with them.
3. Finally, they call ```DELETE /users/20/delete``` to delete their account.
