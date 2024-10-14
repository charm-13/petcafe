## Example flows for the PetCafe

## 1. Pet Cafe User Purchasing Example Flow

The user "dragonluvr5" decides that they want to buy a treat for their favorite dragon in the cafe. They check the cafe catalog by calling ```GET /catalog``` to make sure there are multiple treats available. They see the treat with SKU "BUBBLY_FIRE_TREAT" which costs 50 gold.
To buy that treat they:
1. Create a cart by calling ```POST /carts``` to get a cart with id 702,
2. Then they call ```POST /carts/702/items/BUBBLY_FIRE_TREAT``` and pass in a quantity of 2.
3. Then they checkout by calling ```POST /carts/702/checkout``` and jump with glee as the treats enter their inventory. 

## 2. Pet Cafe User-Pet Interaction Example Flow

## 3. Pet Cafe User Viewing Example Flow

A user with id 20 wants to view the list of pets that are available to interact with. They view the list and then check their own inventory to see what they have, if they have treats or sufficient gold. They become violently upset at the inventory and the available pets, so they decide to delete their account.

To do these actions, they:
1. Start by calling ```GET /inventory``` to view their inventory
2. Then call ```GET /creatures``` to view the list of available creatures
3. Finally, they call ```DELETE /users/20/delete``` to delete their account.
