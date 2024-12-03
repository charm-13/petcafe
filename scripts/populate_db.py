import sqlalchemy
import os
import dotenv
from faker import Faker
import numpy as np
import random

def database_connection_url():
    dotenv.load_dotenv()
    DB_USER: str = os.environ.get("POSTGRES_USER")
    DB_PASSWD = os.environ.get("POSTGRES_PASSWORD")
    DB_SERVER: str = os.environ.get("POSTGRES_SERVER")
    DB_PORT: str = os.environ.get("POSTGRES_PORT")
    DB_NAME: str = os.environ.get("POSTGRES_DB")
    return f"postgresql://{DB_USER}:{DB_PASSWD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"

from src import database as db

# From Pierce's code - do this if there is a new way to ceate DB engine with docker
# Create a new DB engine based on our connection string
# db = sqlalchemy.create_engine(database_connection_url(), use_insertmanyvalues=True)

num_users = 5000
num_creatures = 1000
num_purchases_per_user = 50
num_treats_per_user = 50
num_user_creature_conn = 50
num_gold_trans = 100
fake = Faker()

users = [{"username": fake.unique.user_name()} for _ in range(num_users)]
treat_list = [ "CLOUD_CANDY", "CRUMBLY_COOKIE", "CUCUMBER_SALAD", "GOGI_BERRY", "HONEY",
                "KEBAB", "NABNAB_BERRY", "PINAP_BERRY", "RAZZ_BERRY", "SARDINE"]
creatures = [
    {
        "name": fake.first_name(),
        "type": fake.random_element(elements=[
            "water_turtle", "fire_lizard", "grass_dragon", "sea_ghost", "psychic_unicorn",
            "fighter_cow", "silly_cat", "electric_sheep", "fluffy_fairy", "flying_bug"
        ]),
        "happiness": random.randint(0, 100),
        "hunger": random.randint(0, 100),
        "stage": random.randint(1,3)
    }
    for i in range(num_creatures)
]

user_inv = []
for user in users:
    treat_totals = {sku: 0 for sku in treat_list}  
    for _ in range(num_treats_per_user):
        sku = fake.random_element(treat_list)
        change = random.randint(-1, 10)
        if treat_totals[sku] + change < 0:
            change = random.randint(0, 10)  
        treat_totals[sku] += change
        user_inv.append({
            "user_id": user["id"],
            "treat_sku": sku,
            "quantity": change,
        })


user_gold = []
for user in users:
    total_gold = 0  
    for i in range(num_gold_trans):
        change = random.randint(-50, 200)
        if total_gold + change < 0:
            change = random.randint(0, 200)  
        total_gold += change
        user_gold.append({
            "user_id": user["id"],
            "amount": change,
        })


user_creature_connections = [
    {
        "user_id": user["id"],
        "creature_id": random.randint(1, num_creatures),
        "affinity": random.randint(0, 100),
        "is_adopted": fake.boolean(chance_of_getting_true=50),
    }
    for user in users
    for i in range(num_user_creature_conn)
]

user_purchases = []
for user in users:
    treat_totals = {sku: 0 for sku in treat_list}  
    for inv in user_inv:
        if inv["user_id"] == user["id"]:
            treat_totals[inv["treat_sku"]] += inv["quantity"]

    for _ in range(num_purchases_per_user):
        sku = fake.random_element(treat_list)
        if treat_totals.get(sku, 0) > 0:  
            treat_totals[sku] -= 1
            user_purchases.append({
                "user_id": user["id"],
                "item_sku": sku,
            })


# fake data
with db.begin() as connection:
    connection.execute(
        sqlalchemy.text("INSERT INTO users (username) VALUES (:username)"), users
    )
    connection.execute(
        sqlalchemy.text(
            "INSERT INTO creatures (name, type, happiness, hunger) VALUES (:name, :type, :happiness, :hunger)"
        ),
        creatures,
    )
    connection.execute(
        sqlalchemy.text(
            "INSERT INTO users_inventory (user_id, treat_sku, quantity) VALUES (:user_id, :treat_sku, :quantity)"
        ),
        user_inv,
    )
    connection.execute(
        sqlalchemy.text(
            "INSERT INTO user_gold (user_id, amount) VALUES (:user_id, :amount)"
        ),
        user_gold,
    )
    connection.execute(
        sqlalchemy.text(
            "INSERT INTO user_creature_connection (user_id, creature_id, affinity, is_adopted) VALUES (:user_id, :creature_id, :affinity, :is_adopted)"
        ),
        user_creature_connections,
    )
    connection.execute(
        sqlalchemy.text(
            "INSERT INTO purchases (user_id, item_sku, quantity) VALUES (:user_id, :creature_id, :affinity, :is_adopted)"
        ),
        user_creature_connections,
    )

    