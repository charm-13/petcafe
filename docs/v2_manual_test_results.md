# Example Workflow 1
Pet Cafe User Purchasing Example Flow
The user "dragonluvr5" decides that they want to buy a treat for their favorite dragon in the cafe. They check the cafe catalog to make sure there are multiple treats available. They see the treat "razz berry" costs 50 gold and decide to add 2.

# Testing Results 1
**Check the catalog by calling ```GET /catalog```:**
1. ```
   curl -X 'GET' \
    'http://127.0.0.1:3000/catalog/' \
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
      'http://127.0.0.1:3000/carts/' \
      -H 'accept: application/json' \
      -H 'access_token: oi' \
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
      'http://127.0.0.1:3000/carts/2/items/RAZZ_BERRY' \
      -H 'accept: application/json' \
      -H 'access_token: oi' \
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
      'http://127.0.0.1:3000/carts/2/checkout' \
      -H 'accept: application/json' \
      -H 'access_token: oi' \
      -d ''
    ```
2. ```
    {
        "total_treats_bought": 2,
        "total_gold_paid": 20
    }
    ```
