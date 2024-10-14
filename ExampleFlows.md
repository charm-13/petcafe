## Example flows for the PetCafe

## 1. Pet Cafe User Purchasing Example Flow

The user "dragonluvr5" decides that they want to buy a treat for their favorite dragon in the cafe. They check the cafe catalog by calling ```GET/catalog``` to make sure there are dragon treats available. They see that they can afford 2 dragon treats, so they create a cart and add the 2 to it. Then they checkout and jump with glee as the treats enter their inventory. 

## 2. Pet Cafe User-Pet Interaction Example Flow

## 3. Pet Cafe User Viewing Example Flow

A user with id 20 wants to view the list of pets that are available to interact with. They view the list and then check their own inventory to see what they have, if they have treats or sufficient gold. They become violently upset at the inventory and the available pets, so they decide to delete their account.

To do these actions, they:
- start by calling GET /inventory to view their inventory
- then call GET /creatures to view the list of available creatures
- finally, they call DELETE /users/20/delete to delete their account
