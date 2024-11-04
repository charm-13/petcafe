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
        treats = connection.execute(sqlalchemy.text("""SELECT sku, name, price, satiety FROM treats""")).mappings().fetchall()
    
    # treats is a list of dictionaries with sku, name, price and satiety for each treat
    return treats