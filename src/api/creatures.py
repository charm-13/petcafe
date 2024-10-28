import sqlalchemy
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src import database as db
from src.api import auth

router = APIRouter(
    prefix="/users/{user_id}/creatures",
    tags=["creatures"],
    dependencies=[Depends(auth.get_api_key)],
)

@router.post("/")
def get_creatures(user_id: int):
    """Retrieves the list of creatures available to interact with in the cafe
        as well as the affinity the requesting user has with each creature."""
        
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text("""SELECT creatures.name, creatures.type, 
                                    COALESCE(user_creature_connection.affinity, 0) AS affinity
                                FROM creatures
                                LEFT JOIN user_creature_connection 
                                    ON creatures.id = user_creature_connection.creature_id
                                    AND user_id = :user_id"""),
            {"user_id": user_id}
            ).mappings()
        
    creatures = []
    
    for creature in result:
        creatures.append({
            "name": creature["name"],
            "type": creature["type"],
            "affinity": creature["affinity"]
        })
    
    return creatures
    