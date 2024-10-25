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
                            JOIN users_inventory ON users.id users_inventory.id
                            WHERE users.id = :id"""),
                            {"id": user_id}).mappings().fetchone()
    return {
        "name": inventory["username"],
        "treats": inventory["treat_sku"],
        "gold": inventory["gold"], 
        "pets": inventory["creatures"]
    }
    