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
                                    COALESCE(user_creature_connection.is_adopted, false) AS status,
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
            "affinity": creature["affinity"],
            "is_adopted": creature["status"]
        })
    
    return creatures


@router.get("/{creature_id}/stats")
def get_creature_stats(user_id: int, creature_id: int):
    """
    Retrieves the stats of the specified creature, including their current hunger and happiness levels,
    and their affinity with the user.
    """

    with db.engine.begin() as connection:
        c_stats = connection.execute(
            sqlalchemy.text(
                """
                SELECT name, type, happiness, hunger,
                       COALESCE(connections.affinity, 0) AS affinity
                  FROM creatures LEFT JOIN user_creature_connection AS connections
                    ON connections.creature_id = creatures.id
                   AND connections.user_id = :u_id
                 WHERE creatures.id = :c_id
                """
            ),
            {"u_id": user_id, "c_id": creature_id}
        ).one()

    return {
        "name": c_stats.name,
        "type": c_stats.type,
        "hunger": c_stats.hunger,
        "happiness": c_stats.happiness,
        "affinity": c_stats.affinity
    }


@router.post("/{creature_id}/feed/{treat_id}")
def feed_creature(user_id: int, creature_id: int, treat_id: str):
    """
    Feeds the specified creature a treat of the specified id. Response returns the gold earned 
    and changes in stats of the creature affected by the action, which are dependent on the treat 
    used to feed the creature. If the creature has max hunger level at the time of the call, 
    the treat is not decremented from the user's inventory.
    """
        
    with db.engine.begin() as connection:
        pass
    
    # return 
    
@router.post("/{creature_id}/play")
def play_with_creature(user_id: int, creature_id: int):
    """ 
    Plays with the specified creature. Increases a creature's happiness and affinity with user. 
    Playing with a pet at max happiness does not earn the user any gold or affinity.
    """
        
    with db.engine.begin() as connection:
        pass
    
    # return 
    
@router.post("/{creature_id}/adopt")
def adopt_creature(user_id: int, creature_id: int):
    """ 
    Adopts a creature. User's affinity level with the specified creature must be 100.
    """

    with db.engine.begin() as connection:
        pass

    # return 
    