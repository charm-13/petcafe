from enum import Enum

import sqlalchemy
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel
from src import database as db
from src.api import auth

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)


class User(BaseModel):
    user_id: int
    username: str


@router.post("/")
def create_cart(new_cart: User) -> dict[str, int]:
    """
    Creates a new cart for a specific user.
    """
    with db.engine.begin() as connection:
        pass
    # return {"cart_id": 0}


class CartItem(BaseModel):
    quantity: int


@router.put("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ 
    Updates the quantity of a specific item in a cart.
    """
    with db.engine.begin() as connection:
        pass
    # return "OK"


@router.post("/{cart_id}/checkout")
def checkout(cart_id: int):
    """ 
    Handles the checkout process for a specific cart.
    """
    with db.engine.begin() as connection:
        pass
    # return {"total_treats_bought": 0, "total_gold_paid": 0}
