from enum import Enum

import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from src import database as db
from src.api import auth

router = APIRouter(
    prefix="/shop",
    tags=["shop"],
    dependencies=[Depends(auth.get_current_user)],
)


class Purchase(BaseModel):
    order_id: int
    treat_sku: str
    quantity: int


@router.get("/catalog/")
def get_catalog():
    """
    Provides a list of each treat, its price, and how filling it is.
    Each item is mapped as a dictionary with keys being sku, name,
    price, and satiety.
    """
    with db.engine.begin() as connection:
        treats = (
            connection.execute(
                sqlalchemy.text(
                    """
                    SELECT
                        sku,
                        name,
                        price,
                        satiety
                    FROM treats
                    """
                )
            )
            .mappings()
            .all()
        )

    return treats


@router.post("/purchase")
def purchase(purchase: Purchase, user=Depends(auth.get_current_user)):
    """
    Handles user purchasing a treat from the cafe.
    """

    if purchase.order_id < 0:
        raise HTTPException(status_code=422, detail="order_id must be positive")

    if purchase.quantity < 1:
        raise HTTPException(status_code=422, detail="quantity must be at least 1")

    try:
        with db.engine.begin() as connection:
            request = (
                connection.execute(
                    sqlalchemy.text(
                        """
                        SELECT
                            u.id,
                            g.gold,
                            t.sku,
                            t.price
                        FROM users u
                        JOIN gold_view g
                            ON g.user_id = u.id
                        CROSS JOIN treats t
                        WHERE u.id = :user_id
                            AND t.sku = :treat_sku
                        """
                    ),
                    {"user_id": user.id, "treat_sku": purchase.treat_sku},
                )
                .mappings()
                .one_or_none()
            )

            if request is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"User {user.id} and/or treat '{purchase.treat_sku}' does not exist.",
                )

            cost = request["price"] * purchase.quantity

            if cost > request["gold"]:
                raise HTTPException(
                    status_code=403,
                    detail=f"You do not have enough gold to purchase the treat. Have: {request['gold']}, Needed: {cost}",
                )

            success = (
                connection.execute(
                    sqlalchemy.text(
                        """
                        INSERT INTO purchases (order_id, user_id, item_sku, quantity)
                        VALUES (:order_id, :user_id, :treat_sku, :quantity)
                        ON CONFLICT (order_id) DO NOTHING
                        RETURNING order_id
                        """
                    ),
                    {
                        "order_id": purchase.order_id,
                        "user_id": user.id,
                        "treat_sku": purchase.treat_sku,
                        "quantity": purchase.quantity,
                    },
                )
                .mappings()
                .one_or_none()
            )

            if not success:
                raise HTTPException(
                    status_code=409,
                    detail=f"Order {purchase.order_id} has already been completed.",
                )

            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO user_gold (user_id, amount)
                    VALUES (:user_id, -1 * :amount);

                    INSERT INTO users_treat_inventory (user_id, treat_sku, quantity)
                    VALUES (:user_id, :treat_sku, :quantity)
                    """
                ),
                {
                    "user_id": user.id,
                    "amount": cost,
                    "treat_sku": purchase.treat_sku,
                    "quantity": purchase.quantity,
                },
            )

            return {"message": "Order successfully completed"}

    except HTTPException as h:
        raise h

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to execute purchase. Error: {e}"
        )
