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

## 2. Creature Interactions

### 2.1. Feed Creature

### 2.2. Play with Creature

### 2.3 Adopt Creature


## 3. User Functions

### 3.1. Get User Inventory `/inventory/` (GET)

Retrieves the inventory of the user.

**Response**:

```json
[
    {
        "name": "string",
        "treats": "string",
        "gold": "integer", 
        "pets": "string"
    }
]
```


### 3.2. Delete User  `/users/{user_id}/delete` (DELETE)

Deletes user profile.

**Response**:

```json
[
    {
        "success": "boolean"
    }
]
```


## 4. Creature Functions

### 4.1. Get Creature Stats `/creatures/` (GET)

Retrieves the stats of the creature.

**Response**:

```json
[
    {
        "name": "string",
        "hunger": "integer", /* Between 1 and 20 */
        "favourite_treat": "integer", /* ID of favourite treat*/
        "hated_treat": "integer", /* ID of most hated treat*/
        "happiness": "integer" /* Between 1 and 10 */
    }
]
```

### 4.2. Get Creature `/creatures/` (GET)

Retrieves the list of creatures.

**Request**:

```json

{
    "user_id": "integer",
}

```

**Response**:

```json
[
    {
        "name": "string",
        "type": "string",
        "affinity": "integer"
    }
]
```