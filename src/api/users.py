import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException
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
            raise HTTPException(
                status_code=422,
                detail="Username must be between 5 and 20 characters long.",
            )

        with db.engine.begin() as connection:
            id = connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO users (username)
                    VALUES (:username)
                    ON CONFLICT (username) DO NOTHING
                    RETURNING id
                    """
                ),
                {"username": user.username},
            ).scalar_one_or_none()

        if not id:
            raise HTTPException(
                status_code=409,
                detail="That username already exists!",
            )

        return {"user_id": id}

    except HTTPException as h:
        raise h
    except Exception as e:
        print("[create_user] An unexpected error has occurred:", str(e))
        raise HTTPException(
            status_code=500, detail=f"Failed to create user. Error: {e}"
        )


@router.post("/{user_id}/delete")
def delete_user(user_id: int):
    """
    Deletes a user with the given id.
    """
    try:
        with db.engine.begin() as connection:
            id_found = connection.execute(
                sqlalchemy.text(
                    """
                    DELETE FROM users
                    WHERE id = :user_id
                    RETURNING 1
                    """
                ),
                {"user_id": user_id},
            ).scalar_one_or_none()

        if not id_found:
            raise HTTPException(
                status_code=404,
                detail=f"User {user_id} doesn't exist.",
            )

        return "OK"

    except HTTPException as h:
        raise h

    except Exception as e:
        print("[delete_user] An unexpected error has occurred:", e)
        raise HTTPException(
            status_code=500, detail=f"Failed to delete user. Error: {e}"
        )


@router.get("/{user_id}/inventory")
def get_inventory(user_id: int):
    """
    Provides the username, amount of gold, and treats in the inventory of the user
    with the given id.
    """
    try:
        with db.engine.begin() as connection:
            u_gold = (
                connection.execute(
                    sqlalchemy.text(
                        """
                        SELECT
                            username,
                            gold
                        FROM users AS u
                        JOIN gold_view AS g
                            ON g.user_id = u.id
                            AND u.id = :id
                        """
                    ),
                    {"id": user_id},
                )
                .mappings()
                .one_or_none()
            )

            if not u_gold:
                raise HTTPException(
                    status_code=404,
                    detail=f"User {user_id} doesn't exist.",
                )

            treats = (
                connection.execute(
                    sqlalchemy.text(
                        """
                        SELECT
                            treat_sku AS sku,
                            quantity
                        FROM user_inventory_view
                        WHERE user_id = :id
                            AND quantity > 0
                        """
                    ),
                    {"id": user_id},
                )
                .mappings()
                .all()
            )

        return {
            "name": u_gold["username"],
            "gold": u_gold["gold"],
            "treats": treats,
        }

    except HTTPException as h:
        raise h

    except Exception as e:
        print("[get_inventory] An unexpected error has occurred:", e)
        raise HTTPException(
            status_code=500, detail=f"Failed to get user's inventory. Error: {e}"
        )


@router.get("/{user_id}/adoptions")
def get_adoptions(user_id: int):
    """
    Provides the name and stage of each creature the user with the given id has adopted.
    """
    try:
        with db.engine.begin() as connection:
            user = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT 1
                    FROM users
                    WHERE users.id = :id
                    """
                ),
                {"id": user_id},
            ).scalar_one_or_none()

            if not user:
                raise HTTPException(
                    status_code=404,
                    detail=f"User {user_id} doesn't exist.",
                )

            adoptions = (
                connection.execute(
                    sqlalchemy.text(
                        """
                        SELECT
                            name,
                            stage
                        FROM user_creature_connection AS conn
                        JOIN creatures
                            ON conn.creature_id = creatures.id
                            AND conn.user_id = :id
                            AND conn.is_adopted = True
                        """
                    ),
                    {"id": user_id},
                )
                .mappings()
                .all()
            )

        print(f"[get_adoptions] User {user_id}'s adoptions:", adoptions)

        return adoptions

    except HTTPException as h:
        raise h

    except Exception as e:
        print("[get_adoptions] An unexpected error has occurred:", e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user's adopted creatures. Error: {e}",
        )
