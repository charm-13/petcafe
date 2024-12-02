# API Specification for PetCafe

## 1. User Purchasing

### 1.1. Get Catalog - `/shop/catalog/` (GET)

Retrieves the catalog of items in the cafe.

**Response**:

```json
[
    {
        "sku": "string",
        "name": "string",
        "price": "integer", 
        "satiety": "integer" /* Between 1 and 100 */
    }
]
```

### 1.2. Purchase - `/shop/purchase/` (POST)

Creates a new cart for a specific user.

**Request**:

```json
{
  "order_id": "integer",
  "treat_sku": "string",
  "quantity": "integer"
}
```

**Response**:

```json
{
    "message": "string"
}
``` 

## 2. Creature Functions

### 2.1. Get Creatures `/creatures` (GET)

Retrieves the list of creatures available to interact with in the cafe.

**Response**:

```json
[
    {
        "name": "string",
        "id": "integer",
        "type": "string",
        "affinity": "integer", /* Between 0 and 100 */
        "is_adopted": "boolean",
        "stage": "integer" /* 1, 2, or 3 */
    }
]
```

### 2.2. Get Creature Stats `/creatures/{creature_id}/stats` (GET)

Retrieves the stats of the specified creature, including their current hunger and happiness levels, and their affinity with the user.

**Response**:

```json
{
    "name": "string",
    "type": "string",
    "hunger": "integer", /* 0-100, 0 being max hungry and 100 being not hungry */
    "happiness": "integer", /* Between 0 to 100 */
    "affinity": "integer", /* Between 0 to 100 */
    "stage": "integer" /* 1, 2, or 3 */
}
```

### 2.3. Feed Creature `/creatures/{creature_id}/feed/{treat_id}` (POST)

Feeds the specified creature a treat of the specified id. Response returns the gold earned and changes in stats of the creature affected by the action, which are dependent on the treat used to feed the creature. If the creature has max hunger level at the time of the call, the treat is not decremented from the user's inventory.

**Response**:

```json
{
        "message": "string", /* indicator of creature's favorability towards treat */
        "gold_earned": "integer", /* 0 if hated, 3 if normal, 5 if loved */
        "change_in_hunger": "integer", /* 0 if treat is hated; else dependent on treat satiety */
        "change_in_happiness": "integer", /* 10 if favorite, 2 if normal, -5 if hated */
        "change_in_affinity": "integer",  /* 5 if favorite, 2 if normal, -2 if hated */
}
```

### 2.2. Play with Creature `/creatures/{creature_id}/play` (POST)

Plays with the specified creature. Increases a creature's happiness and affinity with user. Playing with a pet at max happiness does not earn the user any gold or affinity.

**Response**:
```json
{
    "gold_earned": "integer", /* 2 gold */
    "affinity": "integer", /* new affinity with creature */
    "happiness": "integer" /* new happiness of creature */
}
```
### 2.3 Adopt Creature `/creatures/{creature_id}/adopt` (POST)

Adopts a creature. User's affinity level with the specified creature must be 100.

**Response:**

```json
"OK"
```
### 2.4 Breed Creatures `/creatures/breed` (POST)

Breeds 2 creatures together. Creatures must be adopted by the user. Name corresponds to the name for the new creature.

**Request:**

```json
{
    "creature_id_1": "integer",
    "creature_id_2": "integer",
    "name": "string"
}
```

**Response:**

```json
{
    "name": "string",
    "id": "integer",
    "type": "string",
    "fav_treat": "string",
    "hated_treat": "string"
}
```
### 2.5 Evolve Creatures `/creatures/{creature_id}/evolve` (POST)

Each creature can be 1 of 3 stages. This evolves a creature to the next stage. 

**Response:**

```json
{
    "stage": "integer" /* 1, 2, or 3 */
}
```

## 3. User Functions

### 3.1. User Registration  `/users/register` (POST)

Creates a new user with the given email, username, and password.

**Request**:

```json
{
  "email": "user@example.com", 
  "username": "string",
  "password": "string"
}
```

**Response**:

```json
{
    "message": "string",
    "user_id": "uuid",
    "access_token": 
}
```

### 3.1. User Login  `/users/register` (POST)

Logs in user with the given email and password.

**Request**:

```json
{
  "email": "user@example.com", /* example@example.com */
  "username": "string",
  "password": "string"
}
```

**Response**:

```json
{
    "user_id": "uuid",
    "access_token": "string" /* unique to each user and each session */ 
}
```

### 3.3. Delete User  `/users/{username}/remove` (DELETE)

Deletes user profile.

**Response**:

```json
{
    "message": "string"
}
```

### 3.4. Get User Inventory `/users/{username}/inventory` (GET)

Retrieves the gold and treat inventory of the user.

**Response**:

```json
{
    "username": "string",
    "gold": "integer", 
    "treats": [ /* List of treats in the users inventory */
            {
            "sku": "string",
            "quantity": "integer"
            }, 
        ] 
}
```

### 3.5. Get User Adoptions `/users/{username}/adoptions` (GET)

Retrieves the name and stage for each creature the user has adopted.

**Response**:

```json
[
    {
    "name": "string", /* name of the creature */
    "stage": "integer" /* 1, 2, or 3 */
    },
]
```
