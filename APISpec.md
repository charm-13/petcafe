# API Specification for PetCafe

## 1. User Purchasing

The API calls are made in this sequence when making a purchase:
1. `Get Catalog`
2. `New Cart`
3. `Add Item to Cart` (Can be called multiple times)
4. `Checkout Cart`

### 1.1. Get Catalog - `/catalog/` (GET)

Retrieves the catalog of items in the cafe.

**Response**:

```json
[
    {
        "sku": "string",
        "name": "string",
        "quantity": "integer",
        "price": "integer", 
        "satiety": "integer" /* Between 1 and 100 */
    }
]
```

### 1.2. New Cart - `/carts/` (POST)

Creates a new cart for a specific user.

**Request**:

```json
{
  "user_id": "integer",
  "username": "string"
}
```

**Response**:

```json
{
    "cart_id": "string" 
}
``` 

### 1.3. Add Item to Cart - `/carts/{cart_id}/items/{item_sku}` (PUT)

Updates the quantity of a specific item in a cart. 

**Request**:

```json
{
  "quantity": "integer"
}
```

**Response**:

```json
{
    "success": "boolean"
}
```

### 1.4. Checkout Cart - `/carts/{cart_id}/checkout` (POST)

Handles the checkout process for a specific cart.

**Response**:

```json
{
    "total_treats_bought": "integer",
    "total_gold_paid": "integer"
}
```

## 2. Creature Functions

### 2.1. Get Creatures `/users/{user_id}/creatures` (GET)

Retrieves the list of creatures available to interact with in the cafe.

**Response**:

```json
[
    {
        "name": "string",
        "type": "string",
        "affinity": "integer" /* Between 0 and 100 */
    }
]
```

### 2.2. Get Creature Stats `/users/{user_id}/creatures/{creature_id}/stats` (GET)

Retrieves the stats of the specified creature, including their current hunger and happiness levels, and their affinity with the user.

**Response**:

```json
{
    "name": "string",
    "type": "string",
    "hunger": "integer", /* Between 0 to 100 */
    "happiness": "integer", /* Between 0 to 100 */
    "affinity": "integer" /* Between 0 to 100 */
}
```

### 2.3. Feed Creature `/users/{user_id}/creatures/{creature_id}/feed/{treat_id}` (POST)

Feeds the specified creature a treat of the specified id. Response returns the gold earned and changes in stats of the creature affected by the action, which are dependent on the treat used to feed the creature. If the creature has max hunger level at the time of the call, the treat is not decremented from the user's inventory.

**Response**:

```json
{
    /* All 0 if pet is full */
        "gold_earned": "integer", /* 0 if hated, 3 if normal, 5 if loved */
        "change_in_hunger": "integer", /* 0 if treat is hated; else dependent on treat satiety */
        "change_in_happiness": "integer", /* 10 if favorite, 5 if normal, -5 if hated */
        "change_in_affinity": "integer",  /* 10 if favorite, 5 if normal, -5 if hated */
        "treat_used": "boolean" /* False if full */
}
```

### 2.2. Play with Creature `/users/{user_id}/creatures/{creature_id}/play` (POST)

Plays with the specified creature. Increases a creature's happiness and affinity with user. Playing with a pet at max happiness does not earn the user any gold or affinity.

**Response**:
```json
{
    "gold_earned": "integer",
    "affinity_earned": "integer"
}
```
### 2.3 Adopt Creature `/users/{user_id}/creatures/{creature_id}/adopt` (POST)

Adopts a creature. User's affinity level with the specified creature must be 100.

**Response:**

```json
{
    "success": "boolean"
}
```

## 3. User Functions

### 3.1. Get User Inventory `/users/{user_id}/inventory` (GET)

Retrieves the inventory of the user.

**Response**:

```json
{
    "name": "string",
    "treats": ["string", ...] /* List of treats in the users inventory */
    "gold": "integer", 
    "pets": ["string", ...] /* Pets that the user has adopted */
}
```

### 3.2. Create User  `/users/create` (POST)

Creates a new user with the specified username.

**Request**:

```json
{
  "username": "string"
}
```

**Response**:

```json
{
    "user_id": "integer"
}
```

### 3.3. Delete User  `/users/{user_id}/delete` (DELETE)

Deletes user profile.

**Response**:

```json
{
    "success": "boolean"
}
```
