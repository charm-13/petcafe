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


@router.get("/{user_id}/inventory")
def get_inventory(user_id: int):
    with db.engine.begin() as connection:
        user = (
            connection.execute(
                sqlalchemy.text(
                    """SELECT username, gold
                                FROM users
                                WHERE users.id = :id"""
                ),
                {"id": user_id},
            )
            .mappings()
            .fetchone()
        )
        treats = (
            connection.execute(
                sqlalchemy.text(
                    """SELECT treat_sku, quantity 
                                FROM users_treat_inventory
                                WHERE user_id = :id
                                AND quantity > 0"""
                ),
                {"id": user_id},
            )
            .mappings()
            .fetchall()
        )
        pets = (
            connection.execute(
                sqlalchemy.text(
                    """SELECT name 
                                FROM user_creature_connection
                                LEFT JOIN creatures ON user_creature_connection.creature_id = creatures.id
                                WHERE user_id = :id
                                AND user_creature_connection.is_adopted = True"""
                ),
                {"id": user_id},
            )
            .mappings()
            .fetchall()
        )

    treat_list = []
    pet_list = []
    for treat in treats:
        treat_list.append({"treat": treat["treat_sku"], "quantity": treat["quantity"]})
    for pet in pets:
        pet_list.append(pet["name"])

    print(f"Treats: {treat_list}, Pets: {pet_list}, User: {user}")

    return {
        "name": user["username"],
        "treats": treat_list,
        "gold": user["gold"],
        "pets": pet_list,
    }


class NewUser(BaseModel):
    username: str


@router.post("/create")
def create_user(user: NewUser):
    with db.engine.begin() as connection:
        id = (
            connection.execute(
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
            )
            .one()
            .id
        )
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
