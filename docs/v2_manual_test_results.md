# Example Workflow 1
Pet Cafe User Purchasing Example Flow
The user "dragonluvr5" decides that they want to buy a treat for their favorite dragon in the cafe. They check the cafe catalog to make sure there are multiple treats available. They see the treat "razz berry" costs 50 gold and decide to add 2.

# Testing Results 1
**Check the catalog by calling ```GET /catalog```:**
1. ```
   curl -X 'GET' \
    'http://cute-creature-cafe.onrender.com/catalog/' \
    -H 'accept: application/json'
    ```
2. ```
    [{"sku": "HONEY", "name": "honey", "price": 8, "satiety": 8}
    {"sku": "GOGI_BERRY", "name": "gogi berry", "price": 10, "satiety": 10}
    {"sku": "RAZZ_BERRY", "name": "razz berry", "price": 10, "satiety": 10}
    {"sku": "CLOUD_CANDY", "name": "cloud candy", "price": 15, "satiety": 15}
    {"sku": "NABNAB_BERRY", "name": "nabnab berry", "price": 15, "satiety": 15}
    {"sku": "PINAP_BERRY", "name": "pinap berry", "price": 20, "satiety": 20}
    {"sku": "CRUMBLY_COOKIE", "name": "crumbly cookie", "price": 20, "satiety": 20}
    {"sku": "VANILLA_FLUFF", "name": "vanilla fluff", "price": 22, "satiety": 22}
    {"sku": "SEAWEED_SNACK", "name": "seaweed", "price": 25, "satiety": 25}
    {"sku": "SHINY_BERRY", "name": "shiny berry", "price": 27, "satiety": 27}
    {"sku": "CUCUMBER_SALAD", "name": "cucumber salad", "price": 30, "satiety": 30}
    {"sku": "SPICE_COOKIE", "name": "spice cookie", "price": 38, "satiety": 38}
    {"sku": "SHADOW_BREAD", "name": "shadow bread", "price": 42, "satiety": 42}
    {"sku": "SARDINE", "name": "sardine", "price": 45, "satiety": 45}
    {"sku": "TAIYAKI", "name": "taiyaki", "price": 55, "satiety": 55}
    {"sku": "KEBAB", "name": "kebab", "price": 75, "satiety": 75}
    {"sku": "STEAK_SKEWER", "name": "steak skewer", "price": 95, "satiety": 95}]

    ```

**Create a cart by calling ```POST /carts``` to get a cart with id `2`:**
1. ```
    curl -X 'POST' \
      'http://cute-creature-cafe.onrender.com/carts/' \
      -H 'accept: application/json' \
      -H 'access_token: oi1i2O9tZgaExzgC' \
      -H 'Content-Type: application/json' \
      -d '{
      "user_id": 1,
      "username": "dragonluvr5"
      }'
    ```
2. ```
    {
        "cart_id": 2
    }
    ```

**Then they call ```POST /carts/2/items/RAZZ_BERRY``` and pass in a quantity of 2:**
1. ```
    curl -X 'PUT' \
      'http://cute-creature-cafe.onrender.com/carts/2/items/RAZZ_BERRY' \
      -H 'accept: application/json' \
      -H 'access_token: oi1i2O9tZgaExzgC' \
      -H 'Content-Type: application/json' \
      -d '{
      "quantity": 2
    }'
    ```
2. ```
    {
     "success": true
    }
    ```
**Then they checkout by calling ```POST /carts/2/checkout``` and jump with glee as the treats enter their inventory.**
1. ```
    curl -X 'POST' \
      'http://cute-creature-cafe.onrender.com/carts/2/checkout' \
      -H 'accept: application/json' \
      -H 'access_token: oi1i2O9tZgaExzgC' \
      -d ''
    ```
2. ```
    {
        "total_treats_bought": 2,
        "total_gold_paid": 20
    }
    ```

## Example Workflow 2

User "dragonluvr5" has the goal of adopting all creatures available. They check their affinity levels with the available creatures and decide to interact with the creature named Blaze, who has an id of `2` and an affinity level `95` with the user. They feed the creature two `RAZZ_BERRY`s and play with it. Then, they adopt the creature because they have enough affinity with it.

### Testing Results 2

**First, they call `GET /users/1/creatures` to view the creatures.**
1. ```
    curl -X 'GET' \
        'http://cute-creature-cafe.onrender.com/users/1/creatures/' \
        -H 'accept: application/json' \
        -H 'access_token: oi1i2O9tZgaExzgC'
    ```
2. ```
    [
        { "name": "Aquaquel", "id": 21, "type": "water_turtle", "affinity": 0, "is_adopted": false },
        { "name": "Blaze", "id": 2, "type": "fire_lizard", "affinity": 95, "is_adopted": false },
        { "name": "Brawlow", "id": 14, "type": "fighter_cow", "affinity": 0, "is_adopted": false },
        { "name": "Fayblossom", "id": 19, "type": "fluffy_fairy", "affinity": 0, "is_adopted": false },
        { "name": "Flutterbop", "id": 8, "type": "flying_bug", "affinity": 0, "is_adopted": false },
        { "name": "Flyka", "id": 18, "type": "flying_bug", "affinity": 3, "is_adopted": false },
        { "name": "Grumblevine", "id": 20, "type": "grass_dragon", "affinity": 2, "is_adopted": false },
        { "name": "Haunter Glow", "id": 15, "type": "sea_ghost", "affinity": 2, "is_adopted": false },
        { "name": "Infernyx", "id": 12, "type": "fire_lizard", "affinity": 0, "is_adopted": false },
        { "name": "Mindara", "id": 6, "type": "psychic_unicorn", "affinity": 0, "is_adopted": false },
        { "name": "Mystara", "id": 16, "type": "psychic_unicorn", "affinity": 6, "is_adopted": false },
        { "name": "Nibbly", "id": 13, "type": "silly_cat", "affinity": 0, "is_adopted": false },
        { "name": "Puffilia", "id": 9, "type": "fluffy_fairy", "affinity": 0, "is_adopted": false },
        { "name": "Rumbull", "id": 4, "type": "fighter_cow", "affinity": 0, "is_adopted": false },
        { "name": "Shellwater", "id": 11, "type": "water_turtle", "affinity": 0, "is_adopted": false },
        { "name": "Shocuff", "id": 17, "type": "electric_sheep", "affinity": 0, "is_adopted": false },
        { "name": "Spectrip", "id": 5, "type": "sea_ghost", "affinity": 1, "is_adopted": false },
        { "name": "Thornvyne", "id": 10, "type": "grass_dragon", "affinity": 0, "is_adopted": false },
        { "name": "Whiskaroo", "id": 3, "type": "silly_cat", "affinity": 100, "is_adopted": true },
        { "name": "Zap E. Wool", "id": 7, "type": "electric_sheep", "affinity": 0, "is_adopted": false }
    ]
    ```
**They, they call `GET /users/1/creatures/2/stats` to get Blaze's current hunger and happiness levels.**
1. ```
    curl -X 'GET' \
        'http://cute-creature-cafe.onrender.com/users/1/creatures/2/stats' \
        -H 'accept: application/json' \
        -H 'access_token: oi1i2O9tZgaExzgC'
    ```

2. ```
    {
        "name": "Blaze",
        "type": "fire_lizard",
        "hunger": 46,
        "happiness": 90,
        "affinity": 95
    }
    ```

**Seeing that Blaze is very hungry, they feed Blaze using two of their treats by calling `POST /users/1/creatures/2/feed/RAZZ_BERRY` twice.**
1. ```
    curl -X 'POST' \
        'http://127.0.01:3000/users/1/creatures/2/feed/RAZZ_BERRY' \
        -H 'accept: application/json' \
        -H 'access_token: oi1i2O9tZgaExzgC' \
        -d ''
    ```
2. ```
    {
        "feed_success": true,
        "gold_earned": 3,
        "change_in_hunger": 10,
        "change_in_happiness": 0,
        "change_in_affinity": 2
    }
    ```

**They play with Blaze by calling `POST /users/1/creatures/2/play`.**
1. ```
    curl -X 'POST' \
        'http://cute-creature-cafe.onrender.com/users/1/creatures/2/play' \
        -H 'accept: application/json' \
        -H 'access_token: oi1i2O9tZgaExzgC' \
        -d ''
    ```

2. ```
    {
        "play_success": true,
        "gold_earned": 2,
        "change_in_affinity": 1,
        "change_in_happiness": 1
    }
    ```

**They check their affinity with Blaze again by calling `GET /users/1/creatures/2/stats`.**
1. ```
    curl -X 'GET' \
        'http://cute-creature-cafe.onrender.com/users/1/creatures/2/stats' \
        -H 'accept: application/json' \
        -H 'access_token: oi1i2O9tZgaExzgC'
    ```

2. ```
    {
        "name": "Blaze",
        "type": "fire_lizard",
        "hunger": 66,
        "happiness": 91,
        "affinity": 100
    }
    ```

**Finally, they see they have strong enough of a bond to adopt Blaze, and excitedly call `POST /users/1/creatures/2/adopt` to welcome Blaze into their home.**

1. ```
    curl -X 'POST' \
        'http://cute-creature-cafe.onrender.com/users/1/creatures/2/adopt' \
        -H 'accept: application/json' \
        -H 'access_token: oi1i2O9tZgaExzgC' \
        -d ''
    ```

2. ```
    {
        "success": true
    }
    ```