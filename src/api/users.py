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
def get_inventory():
    # with db.engine.begin() as connection:
    #     connection.execute(
    #         sqlalchemy.text()
    #     )
    # return "OK"
    