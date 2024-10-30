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

@router.post("/{creature_id}/stats")
def get_creature_stats(user_id: int, creature_id: int):
    """ 
    Retrieves the stats of the specified creature, including their current hunger and happiness levels, 
    and their affinity with the user.
    """
        
    with db.engine.begin() as connection:
        pass
    
    # return
    
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
    
    played = False
    gold_earned = 0
    affinity_change = 0
    happiness_change = 0
    with db.engine.begin() as connection:
        happiness = connection.execute(sqlalchemy.text("""SELECT happiness 
                                                       FROM creatures 
                                                       WHERE id = :creature"""),
                                                       {"creature": creature_id}).mappings().fetchone()
        
        if happiness["happiness"] < 100:
            happiness_change = 1
            played = True
            gold_earned = 2

        affinity = connection.execute(sqlalchemy.text("""SELECT affinity
                                                      FROM user_creature_connection
                                                      WHERE user_id = :user AND creature_id = :creature"""),
                                                      {"user": user_id, "creature": creature_id}).mappings().fetchone()
        
        print(f"Affinity: {affinity}")
        
        if affinity and happiness_change:
            if affinity["affinity"] < 100:
                affinity_change = 1 

        connection.execute(sqlalchemy.text("""INSERT INTO user_creature_connection (user_id, creature_id, affinity)
                                               VALUES (:user, :creature, :affinity)
                                           ON CONFLICT(user_id, creature_id)
                                           DO UPDATE 
                                           SET affinity = user_creature_connection.affinity + :affinity"""),
                           {"user": user_id, "creature": creature_id, "affinity": affinity_change})
        

        connection.execute(sqlalchemy.text("""UPDATE creatures 
                                           SET happiness = happiness + :happiness_change 
                                           WHERE id = :creature"""),
                           {"happiness_change": happiness_change, "creature": creature_id})
        
        connection.execute(sqlalchemy.text("""UPDATE users 
                                           SET gold = gold + :gold_earned 
                                           WHERE id = :user"""),
                           {"gold_earned": gold_earned, "user": user_id})
    
    return{
        "play_success": played,
        "gold_earned": gold_earned, 
        "change_in_affinity": affinity_change, 
        "change_in_happiness": happiness_change 
        }

@router.post("/{creature_id}/adopt")
def adopt_creature(user_id: int, creature_id: int):
    """ 
    Adopts a creature. User's affinity level with the specified creature must be 100.
    """
        
    with db.engine.begin() as connection:
        pass
    
    # return 
    