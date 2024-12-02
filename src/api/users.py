import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr

from src import database as db
from src.api import auth

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


class NewUser(BaseModel):
    email: EmailStr
    username: str
    password: str


class Login(BaseModel):
    email: EmailStr
    password: str


class PasswordUpdate(BaseModel):
    email: EmailStr
    username: str
    new_password: str


class UsernameUpdate(BaseModel):
    email: EmailStr
    password: str
    new_username: str


@router.post("/register")
async def register(user: NewUser):
    """
    Registers a new user with the given email, username, and password.
    Returns verification message and the user's id.
    """

    if not 5 <= len(user.username) <= 25:
        raise HTTPException(
            status_code=422,
            detail="Username must be between 5 and 25 characters.",
        )

    try:
        with db.engine.begin() as connection:
            existing = (
                connection.execute(
                    sqlalchemy.text(
                        """
                        SELECT username
                        FROM users
                        WHERE username = :username
                        """
                    ),
                    {"username": user.username},
                )
                .mappings()
                .one_or_none()
            )

            if existing:
                raise HTTPException(
                    status_code=409,
                    detail=f"Username '{user.username}' is already taken.",
                )

            auth_response = await auth.supabase.auth.sign_up(
                {"email": user.email, "password": user.password}
            )

            if not auth_response.user:
                print(f"Failed to create user in Supabase")
                raise HTTPException(
                    status_code=400, detail="Failed to create user in Supabase"
                )

            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO users (user_id, username)
                    VALUES (:user_id, :username)
                    """
                ),
                {"user_id": auth_response.user.id, "username": user.username},
            )

        return {
            "message": "Registration successful. Check your email for verification.",
            "user_id": auth_response.user.id,
            "access_token": auth_response.session.access_token,
        }

    except Exception as e:
        if "auth_response" in locals() and auth_response.user:
            try:
                auth.supabase.auth.admin.delete_user(auth_response.user.id)
            except Exception as cleanup_error:
                print(f"[register] Failed to clean up auth user: {cleanup_error}")

        raise HTTPException(
            status_code=500, detail=f"Failed to create user. Error: {e}"
        )


@router.post("/login")
async def login(credentials: Login):
    """
    Logs in user with the given email and password.
    """
    try:
        auth_response = auth.supabase.auth.sign_in_with_password(
            {"email": credentials.email, "password": credentials.password}
        )

        return {
            "user_id": auth_response.user.id,
            "access_token": auth_response.session.access_token,
        }

    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@router.delete("/remove")
def delete_user(user=Depends(auth.get_current_user)):
    """
    Deletes a user with the given username.
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
                {"user_id": user.id},
            ).scalar_one_or_none()

            if not id_found:
                raise HTTPException(
                    status_code=404,
                    detail=f"User '{user.id}' does not exist.",
                )

            try:
                auth.supabase.auth.admin.delete_user(user.id)
            except Exception as cleanup_error:
                print(f"[register] Failed to clean up auth user: {cleanup_error}")
                raise HTTPException(
                    status_code=500, detail=f"Failed to create user. Error: {cleanup_error}"
                )

        return {"message": "Successfully deleted."}

    except HTTPException as h:
        raise h

    except Exception as e:
        print("[delete_user] An unexpected error has occurred:", e)
        raise HTTPException(
            status_code=500, detail=f"Failed to delete user. Error: {e}"
        )


@router.get("/inventory")
def get_inventory(user=Depends(auth.get_current_user)):
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
                            AND u.id = :user_id
                        """
                    ),
                    {"user_id": user.id},
                )
                .mappings()
                .one_or_none()
            )

            if not u_gold:
                raise HTTPException(
                    status_code=404,
                    detail=f"User not found.",
                )

            treats = (
                connection.execute(
                    sqlalchemy.text(
                        """
                        SELECT
                            treat_sku AS sku,
                            quantity
                        FROM user_inventory_view
                        WHERE user_id = :user_id
                            AND quantity > 0
                        """
                    ),
                    {"user_id": user.id},
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


@router.get("/adoptions")
def get_adoptions(user=Depends(auth.get_current_user)):
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
                            name,
                            stage
                        FROM user_creature_connection AS conn
                        JOIN creatures
                            ON conn.creature_id = creatures.id
                            AND conn.user_id = :id
                            AND conn.is_adopted = True
                        """
                    ),
                    {"id": user.id},
                )
                .mappings()
                .all()
            )

        print(f"[get_adoptions] User {user.id}'s adoptions:", adoptions)

        return adoptions

    except HTTPException as h:
        raise h

    except Exception as e:
        print("[get_adoptions] An unexpected error has occurred:", e)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user's adopted creatures. Error: {e}",
        )
