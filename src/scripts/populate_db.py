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


import database as db

# From Pierce's code - do this if there is a new way to ceate DB engine with docker
# Create a new DB engine based on our connection string
# db = sqlalchemy.create_engine(database_connection_url(), use_insertmanyvalues=True)

num_users = 2000
num_creatures = 1000
num_purchases_per_user = 50
num_treats_per_user = 150
num_user_creature_conn = 100
num_gold_trans = 200
fake = Faker()


users = [
    {"id": fake.unique.uuid4(), "username": fake.unique.user_name()}
    for _ in range(num_users)
]
treat_list = [
    "CLOUD_CANDY",
    "CRUMBLY_COOKIE",
    "CUCUMBER_SALAD",
    "GOGI_BERRY",
    "HONEY",
    "KEBAB",
    "NABNAB_BERRY",
    "PINAP_BERRY",
    "RAZZ_BERRY",
    "SARDINE",
]
creatures = [
    {
        "id": i,
        "name": fake.unique.name(),
        "type": fake.random_element(
            elements=[
                "water_turtle",
                "fire_lizard",
                "grass_dragon",
                "sea_ghost",
                "psychic_unicorn",
                "fighter_cow",
                "silly_cat",
                "electric_sheep",
                "fluffy_fairy",
                "flying_bug",
            ]
        ),
        "happiness": random.randint(0, 100),
        "hunger": random.randint(0, 100),
        "stage": random.randint(1, 3),
    }
    for i in range(21, num_creatures + 1)
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
        user_inv.append(
            {
                "user_id": user["id"],
                "treat_sku": sku,
                "quantity": change,
            }
        )


user_gold = []
for user in users:
    total_gold = 0
    for i in range(num_gold_trans):
        change = random.randint(-50, 200)
        if total_gold + change < 0:
            change = random.randint(0, 200)
        total_gold += change
        user_gold.append(
            {
                "user_id": user["id"],
                "amount": change,
            }
        )


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
            user_purchases.append(
                {
                    "user_id": user["id"],
                    "item_sku": sku,
                }
            )


# fake data
with db.engine.begin() as connection:
    connection.execute(
        sqlalchemy.text(
            """
            INSERT INTO treats (sku, name, satiety, price)
            VALUES
                ('CLOUD_CANDY', 'cloud candy', 15, 15),
                ('CRUMBLY_COOKIE', 'crumbly cookie', 20, 20),
                ('CUCUMBER_SALAD', 'cucumber salad', 30, 30),
                ('GOGI_BERRY', 'gogi berry', 10, 10),
                ('HONEY', 'honey', 8, 8),
                ('KEBAB', 'kebab', 75, 75),
                ('NABNAB_BERRY', 'nabnab berry', 15, 15),
                ('PINAP_BERRY', 'pinap berry', 20, 20),
                ('RAZZ_BERRY', 'razz berry', 10, 10),
                ('SARDINE', 'sardine', 45, 45),
                ('SEAWEED_SNACK', 'seaweed', 25, 25),
                ('SHADOW_BREAD', 'shadow bread', 42, 42),
                ('SHINY_BERRY', 'shiny berry', 27, 27),
                ('SPICE_COOKIE', 'spice cookie', 38, 38),
                ('STEAK_SKEWER', 'steak skewer', 95, 95),
                ('TAIYAKI', 'taiyaki', 55, 55),
                ('VANILLA_FLUFF', 'vanilla fluff', 22, 22)
            ON CONFLICT DO NOTHING;

            INSERT INTO
                evolution_stages (stage, max_happiness, max_hunger)
            VALUES
                (1, 100, 100),
                (2, 500, 500),
                (3, 1000, 1000)
            ON CONFLICT DO NOTHING;

            INSERT INTO
                creature_types (type, fav_treat, hated_treat)
            VALUES
                ('water_turtle', 'SARDINE', 'KEBAB'),
                ('fire_lizard', 'SPICE_COOKIE', 'SEAWEED_SNACK'),
                ('grass_dragon', 'CUCUMBER_SALAD', 'SPICE_COOKIE'),
                ('sea_ghost', 'SHADOW_BREAD', 'CRUMBLY_COOKIE'),
                ('psychic_unicorn', 'SHINY_BERRY', 'SHADOW_BREAD'),
                ('fighter_cow', 'GOGI_BERRY', 'STEAK_SKEWER'),
                ('silly_cat', 'TAIYAKI', 'CUCUMBER_SALAD'),
                ('electric_sheep', 'CLOUD_CANDY', 'SARDINE'),
                ('fluffy_fairy', 'PINAP_BERRY', 'VANILLA_FLUFF'),
                ('flying_bug', 'VANILLA_FLUFF', 'HONEY')
            ON CONFLICT DO NOTHING;

            INSERT INTO
                creatures (id, name, type, happiness, hunger)
            VALUES
                (1, 'Aquaquel', 'water_turtle', 100, 0)
                (2, 'Blaze', 'fire_lizard', 100, 0),
                (3, 'Whiskaroo', 'silly_cat', 100, 0),
                (4, 'Rumbull', 'fighter_cow', 100, 0),
                (5, 'Spectrip', 'sea_ghost', 100, 0),
                (6, 'Mindara', 'psychic_unicorn', 100, 0),
                (7, 'Zap E. Wool', 'electric_sheep', 100, 0),
                (8, 'Flutterbop', 'flying_bug', 100, 0),
                (9, 'Puffilia', 'fluffy_fairy', 100, 0),
                (10, 'Thornvyne', 'grass_dragon', 100, 0),
                (11, 'Shellwater', 'water_turtle', 100, 0),
                (12, 'Infernyx', 'fire_lizard', 100, 0),
                (13, 'Nibbly', 'silly_cat', 100, 0),
                (14, 'Brawlow', 'fighter_cow', 100, 0),
                (15, 'Haunter Glow', 'sea_ghost', 100, 0),
                (16, 'Mystara', 'psychic_unicorn', 100, 0),
                (17, 'Shocuff', 'electric_sheep', 100, 0),
                (18, 'Flyka', 'flying_bug', 100, 0),
                (19, 'Fayblossom', 'fluffy_fairy', 100, 0),
                (20, 'Grumblevine', 'grass_dragon', 100, 0)
            ON CONFLICT DO NOTHING;
            """
        )
    )
    connection.execute(
        sqlalchemy.text(
            """
            INSERT INTO users (id, username)
            VALUES (:id, :username)
            """
        ),
        users,
    )
    connection.execute(
        sqlalchemy.text(
            """
            INSERT INTO creatures (name, type, happiness, hunger)
            VALUES (:name, :type, :happiness, :hunger)
            """
        ),
        creatures,
    )
    connection.execute(
        sqlalchemy.text(
            """
            INSERT INTO users_inventory (user_id, treat_sku, quantity)
            VALUES (:user_id, :treat_sku, :quantity)
            """
        ),
        user_inv,
    )
    connection.execute(
        sqlalchemy.text(
            """
            INSERT INTO user_gold (user_id, amount)
            VALUES (:user_id, :amount)
            """
        ),
        user_gold,
    )
    connection.execute(
        sqlalchemy.text(
            """
            INSERT INTO user_creature_connection (user_id, creature_id, affinity, is_adopted)
            VALUES (:user_id, :creature_id, :affinity, :is_adopted)
            """
        ),
        user_creature_connections,
    )
    connection.execute(
        sqlalchemy.text(
            """
            INSERT INTO purchases (user_id, item_sku, quantity)
            VALUES (:user_id, :creature_id, :affinity, :is_adopted)
            """
        ),
        user_creature_connections,
    )