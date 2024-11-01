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
        id = connection.execute(
            sqlalchemy.text("""INSERT INTO carts (user_id, time_created)
                            SELECT :user_id, CURRENT_TIMESTAMP AT TIME ZONE 'America/Los_Angeles'
                            RETURNING id"""),
            {"user_id": new_cart.user_id}
        ).mappings().fetchone()
        
    cart_id = id["id"]
        
    print(f"cart id: {cart_id}, new cart for: {new_cart}")
    return { "cart_id": cart_id }


class CartItem(BaseModel):
    quantity: int


@router.put("/{cart_id}/items/{item_sku}")
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    """ 
    Updates the quantity of a specific item in a cart.
    """
    print(f"Finding cart {cart_id}...")
    
    try:
        with db.engine.begin() as connection:
            ids = connection.execute(
                sqlalchemy.text("""SELECT id 
                                FROM carts 
                                WHERE id = :cart_id"""), 
                {"cart_id": cart_id}
            ).fetchone()
            
            if ids is None:
                print(f"cart {cart_id} doesn't exist")
                return {"success": False} 
        
            connection.execute(
                sqlalchemy.text("""INSERT INTO carts_items (cart_id, item_sku, quantity) 
                                VALUES (:id, :sku, :amt)"""), 
                {"id": cart_id, "sku": item_sku, "amt": cart_item.quantity}
            )

        print(f"Added {cart_item.quantity} {item_sku} to cart {cart_id}")
        return {"success": True}
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"success": False, "error": str(e)}


@router.post("/{cart_id}/checkout")
def checkout(cart_id: int):
    """ 
    Handles the checkout process for a specific cart.
    """
    print(f"Starting checkout for cart {cart_id}...")
    total_bought = 0
    total_paid = 0
    
    try:
        with db.engine.begin() as connection:
            items = connection.execute(
                sqlalchemy.text("""SELECT carts_items.cart_id, carts_items.item_sku, carts_items.quantity, treats.price
                                FROM carts_items 
                                JOIN treats ON treats.sku = carts_items.item_sku
                                WHERE cart_id = :cart_id"""), 
                {"cart_id": cart_id}
            ).mappings()
            
            if not items:
                print(f"cart {cart_id} is empty or doesn't exist")
                return {"error": "Cart is empty or doesn't exist"}
            
            purchases = []
            for item in items:
                sku = item["item_sku"]
                quantity = item["quantity"]
                price = item["price"]
                total_bought += quantity
                total_paid += quantity*price
                
                purchases.append({"sku": sku, "quantity": quantity, "price per item": price})
                
            connection.execute(
                sqlalchemy.text("""WITH user AS (
                                    SELECT user_id
                                    FROM carts
                                    WHERE cart_id = :cart_id
                                    LIMIT 1
                                )
                                UPDATE users 
                                SET gold = gold + :total_paid
                                WHERE user_id = user"""),
                {"total_paid": total_paid})
                
            print(f"""cart {cart_id} bought {purchases} \n 
                  cart {cart_id} bought {total_bought} potions and paid {total_paid} gold""") 
            
        return {"total_treats_bought": total_bought,
                "total_gold_paid": total_paid}
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return {"error": str(e)}
