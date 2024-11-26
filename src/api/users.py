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


class NewUser(BaseModel):
    username: str


@router.post("/create")
def create_user(user: NewUser):
    """
    Creates a new user with the given username. Returns the new user's id.
    """
    try:
        if len(user.username) < 5 or len(user.username) > 20:
            return {
                "success": False,
                "error": "Username must be between 5 and 20 characters.",
            }

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

    except Exception as e:
        print(f"An error occurred: {e}")
        return {"success": False, "error": str(e)}


@router.delete("/{user_id}/delete")
def delete_user(user_id: int):
    """
    Deletes a user with the given id.
    """
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


@router.get("/{user_id}/inventory")
def get_inventory(user_id: int):
    """
    Provides the username, amount of gold, and treats in the inventory of the user
    with the given id.
    """
    try:
        with db.engine.begin() as connection:
            inventory = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT
                        u.username,
                        g.gold,
                        i.treat_sku,
                        i.quantity
                    FROM users u
                    LEFT JOIN user_inventory_view i
                        ON i.user_id = u.id
                        AND i.quantity > 0
                    LEFT JOIN gold_view g
                        ON g.user_id = u.id
                    WHERE u.id = :id
                """
                ),
                {"id": user_id},
            ).mappings()

        treat_list = []
        username = None
        gold = None

        for item in inventory:
            if username is None and gold is None:
                username = item["username"]
                gold = item["gold"]

            if item["treat_sku"]:
                treat_list.append(
                    {"username": item["treat_sku"], "quantity": item["quantity"]}
                )

        if username == None or gold == None:
            return {"success": False, "error": f"User {user_id} does not exist."}

        return {"name": username, "gold": gold, "treats": treat_list}

    except Exception as e:
        print(f"An unexpected error has occurred: {e}")
        return {"success": False, "error": str(e)}


@router.get("/{user_id}/adoptions")
def get_adoptions(user_id: int):
    """
    Provides the name and stage of each creature the user with the given id has adopted.
    """
    try:
        with db.engine.begin() as connection:
            adoptions = (
                connection.execute(
                    sqlalchemy.text(
                        """
                    SELECT 
                        name, stage
                    FROM user_creature_connection u
                    LEFT JOIN creatures c ON u.creature_id = c.id
                    WHERE user_id = :id
                        AND u.is_adopted = True
                """
                    ),
                    {"id": user_id},
                )
                .mappings()
                .fetchall()
            )

        print(f"Adoptions: {adoptions}")

        return adoptions

    except Exception as e:
        print(f"An unexpected error has occurred: {e}")
        return {"success": False, "error": str(e)}
