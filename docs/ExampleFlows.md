## Example flows for the PetCafe

## 1. Pet Cafe User Purchasing Example Flow

The user "dragonluvr5" decides that they want to buy a treat for their favorite dragon in the cafe. They check the cafe catalog by calling ```GET /catalog``` to make sure there are multiple treats available. They see the treat with id 328 which costs 50 gold.
To buy that treat they:
1. Create a cart by calling ```POST /carts``` to get a cart with id 702,
2. Then they call ```POST /carts/702/items/328``` and pass in a quantity of 2.
3. Then they checkout by calling ```POST /carts/702/checkout``` and jump with glee as the treats enter their inventory. 

## 2. Pet Cafe User-Pet Interaction Example Flow

The user identified by id `475` has the goal of adopting all creatures available, and strategizes by prioritizing interactions with the ones they have the lowest affinity with.
They call `POST /creatures/475` to check their affinity levels with the available creatures, and decide to interact with the creature with id `25`, who has affinity level `20` with the user.
To satisfy the needs of the creature they do the following.
1. Call `GET /creatures/475/stats` and pass in a `creature_id` of 25 to get the creature's current hunger and happiness levels.
2. Feed the creature using a treat by calling `POST /creatures/475/feed` and passing in `creature_id` and `treat_id`.
3. Play with the creature by calling `POST /creatures/475/play` and passing in the `creature_id`.
4. Check the creature's updated happiness and hunger levels using `GET /creatures/475/stats` again.
5. Rinse and repeat until the creature is either full or completely happy.

## 3. Pet Cafe User Viewing Example Flow

A user with id 20 wants to view the list of pets that are available to interact with. They view the list and then check their own inventory to see what they have, if they have treats or sufficient gold. They become violently upset at the inventory and the available pets, so they decide to delete their account.

To do these actions, they:
1. Start by calling ```GET /inventory/20``` to view their inventory
2. Then call ```GET /creatures/20``` to view the list of available creatures and their current affinity with them.
3. Finally, they call ```DELETE /users/20/delete``` to delete their account.
