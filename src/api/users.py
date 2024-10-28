import sqlalchemy
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src import database as db
from src.api import auth

router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/{user_id}/inventory")
def get_inventory(user_id: int):
    with db.engine.begin() as connection:
        inventory = connection.execute(
            sqlalchemy.text("""SELECT username, gold, treat_sku, name 
                                FROM users
                                JOIN users_inventory ON users.id = users_inventory.user_id
                                JOIN user_adoptions ON users.id = user_adoptions.user_id
                                JOIN creatures ON user_adoptions.creature_id = creatures.id
                                WHERE users.id = :id"""),
                                {"id": user_id}).mappings().fetchall()

    treats_list = []
    pets_list = []
    username = inventory[0]["username"]
    gold = inventory[0]["gold"]
    for item in inventory:
        if item["treat_sku"] not in treats_list:
            treats_list.append(item["treat_sku"])
        if item["name"] not in pets_list:
            pets_list.append(item["name"])

    return {
        "name": username,
        "treats": treats_list,
        "gold": gold, 
        "pets": pets_list
    }


class NewUser(BaseModel):
    username: str


@router.post("/create")
def create_user(user: NewUser):
    with db.engine.begin() as connection:
        id = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO users (username)
                           VALUES (:username)
                ON CONFLICT (username)
                  DO UPDATE
                        SET username = excluded.username
                RETURNING id
                """
            ),
            {"username": user.username},
        ).one().id
    return {"user_id": id}


@router.delete("/{user_id}/delete")
def delete_user(user_id: int):
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM users
                WHERE id = :user_id"""
            ),
            {"user_id": user_id},
        )
    return "OK"
