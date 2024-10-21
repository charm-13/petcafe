import sqlalchemy
from fastapi import APIRouter
from src import database as db
import re

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Each unique item combination must have only a single price.
    """
    with db.engine.begin() as connection:
        pass
    # return [
    #     {"sku": "string", "name": "string", "quantity": 0, "price": 0, "satiety": 0}
    # ]
