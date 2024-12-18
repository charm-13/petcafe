# Example workflow
Pet Cafe User Viewing Example Flow
A new user creates their account with username "dragonluvr5" and is assigned id `1`. They want to view the list of creatures that are available to interact with. 
They view the list of pets and then check their own inventory to see what they have. They realize they have 0 gold and 0 treats and on top of that, they hate 
the names of the pets!! They become violently upset at the situation, so they decide to delete their account.

# Testing results
**Start by calling `POST /users/create` and pass in "dragonluvr5". They're assigned id `1`:**
1. ```
    curl -X 'POST' \ 
        'http://cute-creature-cafe.onrender.com/users/create' \
        -H 'accept: application/json' \
        -H 'access_token: oi1i2O9tZgaExzgC' \
        -H 'Content-Type: application/json' \
        -d '{"username": "dragonluvr5"}'
    ```
2. ```
    {
        "user_id": 1
    }
    ```

**Then they call `GET /inventory/1` to view their inventory:**
1. ```
    curl -X 'POST' \
        'http://cute-creature-cafe.onrender.com/users/1/inventory' \
        -H 'accept: application/json' \
        -H 'access_token: oi1i2O9tZgaExzgC' \
        -d ''
    ```
2. ```
    {
        "name": "dragonluvr5",
        "treats": [],
        "gold": 0,
        "pets": []
    }
    ```

**Then call `GET /creatures/1` to view the list of available creatures and their current affinity with them:**
1. ```
    curl -X 'POST' \
        'http://cute-creature-cafe.onrender.com/users/1/creatures/' \
        -H 'accept: application/json' \
        -H 'access_token: oi1i2O9tZgaExzgC' \
        -d ''
    ```
2. ```
    [
        {"name": "Whiskaroo", "type": "silly_cat", "affinity": 0, "is_adopted": false},
        {"name": "Rumbull", "type": "fighter_cow", "affinity": 0, "is_adopted": false},
        {"name": "Spectrip", "type": "sea_ghost", "affinity": 0, "is_adopted": false},
        {"name": "Mindara", "type": "psychic_unicorn", "affinity": 0, "is_adopted": false},
        {"name": "Flutterbop", "type": "flying_bug", "affinity": 0, "is_adopted": false},
        {"name": "Thornvyne", "type": "grass_dragon", "affinity": 0, "is_adopted": false},
        {"name": "Shellwater", "type": "water_turtle", "affinity": 0, "is_adopted": false},
        {"name": "Infernyx", "type": "fire_lizard", "affinity": 0, "is_adopted": false},
        {"name": "Nibbly", "type": "silly_cat", "affinity": 0, "is_adopted": false},
        {"name": "Brawlow", "type": "fighter_cow", "affinity": 0, "is_adopted": false},
        {"name": "Mystara", "type": "psychic_unicorn", "affinity": 0, "is_adopted": false},
        {"name": "Shocuff", "type": "electric_sheep", "affinity": 0, "is_adopted": false},
        {"name": "Flyka", "type": "flying_bug", "affinity": 0, "is_adopted": false},
        {"name": "Fayblossom", "type": "fluffy_fairy", "affinity": 0, "is_adopted": false},
        {"name": "Grumblevine", "type": "grass_dragon", "affinity": 0, "is_adopted": false},
        {"name": "Aquaquel", "type": "water_turtle", "affinity": 0, "is_adopted": false},
        {"name": "Zap E. Wool", "type": "electric_sheep", "affinity": 0, "is_adopted": false},
        {"name": "Blaze", "type": "fire_lizard", "affinity": 0, "is_adopted": false},
        {"name": "Haunter Glow", "type": "sea_ghost", "affinity": 0, "is_adopted": false},
        {"name": "Puffilia", "type": "fluffy_fairy", "affinity": 0, "is_adopted": false}
    ]
    ```
Finally, they call `DELETE /users/1/delete` to delete their account:
1. ```
    curl -X 'DELETE' \
        'http://cute-creature-cafe.onrender.com/users/1/delete' \
        -H 'accept: application/json' \
        -H 'access_token: oi1i2O9tZgaExzgC'
    ```
2. ```"OK"```
