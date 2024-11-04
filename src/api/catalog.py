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
        treats = connection.execute(sqlalchemy.text("""SELECT * FROM treats""")).mappings().fetchall()

    catalog = []
    for treat in treats:
        catalog.append({
            "sku": treat["sku"],
            "name": treat["name"],
            "price": treat["price"],
            "satiety": treat["satiety"]
        })
    
    return catalog
