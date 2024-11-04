import sqlalchemy
from fastapi import APIRouter
from src import database as db
import re

router = APIRouter()


@router.get("/catalog/", tags=["catalog"])
def get_catalog():
    """
    Provides a list of each treat, its price, and how filling it is.
    Each item is mapped as a dictionary with keys being sku, name, 
    price, and satiety.
    """
    with db.engine.begin() as connection:
        treats = connection.execute(sqlalchemy.text("""SELECT sku, name, price, satiety FROM treats""")).mappings().fetchall()
    
    return treats