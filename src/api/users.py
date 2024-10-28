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
            sqlalchemy.text("""SELECT username, gold, treat_sku, creatures 
                            FROM users
                            JOIN users_inventory ON users.id = users_inventory.user_id
                            JOIN user_adoptions ON users.id = user_adoptions.user_id
                            JOIN creatures ON user_adoptions.creature_id = creatures.name
                            WHERE users.id = :id"""),
                            {"id": user_id}).mappings().fetchall()
    return {
        "name": inventory["username"],
        "treats": inventory["treat_sku"],
        "gold": inventory["gold"], 
        "pets": inventory["creatures"]
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
