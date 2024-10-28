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
    