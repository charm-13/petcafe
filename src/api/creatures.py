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
    info = {
        "name": c_stats.name,
        "type": c_stats.type,
        "hunger": c_stats.hunger,
        "happiness": c_stats.happiness,
        "affinity": c_stats.affinity
    }
    print(f"Creature info ({creature_id}) for user {user_id}:", info)
    return info


@router.post("/{creature_id}/feed/{treat_sku}")
def feed_creature(user_id: int, creature_id: int, treat_sku: str):
    """
    Feeds the specified creature a treat of the specified id. Response returns the gold earned 
    and changes in stats of the creature affected by the action, which are dependent on the treat 
    used to feed the creature. If the creature has max hunger level at the time of the call, 
    the treat is not decremented from the user's inventory.
    """    
        
    feed_success = False    # If the creature ate the treat (only false if hunger maxed out) 
    gold_earned = 0         # 5 if favourite, 3 if normal, 0 if hated
    change_in_hunger = 0    # 0 if treat is hated; else dependent on treat satiety 
    change_in_happiness = 0 # 10 if favorite, 5 if normal, -5 if hated 
    change_in_affinity = 0  # 5 if favorite, 2 if normal, -2 if hated 
    
    with db.engine.begin() as connection:
        stats = connection.execute(sqlalchemy.text(""" SELECT (100-happiness) AS remaining_happiness, 
                                                   (100-hunger) AS remaining_hunger, 
                                                   fav_treat, hated_treat, 
                                                   COALESCE(user_creature_connection.affinity, 0) AS affinity
                                                   FROM creatures 
                                                   JOIN creature_types ON creatures.type = creature_types.type AND creatures.id = :creature
                                                   LEFT JOIN user_creature_connection ON creatures.id = user_creature_connection.creature_id 
                                                   AND user_id = :user_id"""),
                                                {"creature": creature_id, "user_id":user_id}).mappings().fetchone()
        
        inventory = connection.execute(sqlalchemy.text("""SELECT treat_sku, satiety 
                                                       FROM users_treat_inventory
                                                       JOIN treats ON sku = treat_sku
                                                       WHERE treat_sku = :sku
                                                       AND quantity > 0"""),
                                                       {"sku": treat_sku}).mappings().fetchone()
                
        print(f"Creature stats: {stats}")
        print(f"Inventory: {inventory}")

        if stats["remaining_hunger"] and inventory:                    
            feed_success = True
            remaining_hunger = stats["remaining_hunger"]
            remaining_happiness = stats["remaining_happiness"]
            remaining_affinity = 100 - stats["affinity"]
            change_in_hunger = inventory["satiety"] if remaining_hunger >= inventory["satiety"] else remaining_hunger           
            
            if treat_sku == stats["fav_treat"]:
                gold_earned = 5
                change_in_happiness = 10 if remaining_happiness >= 10 else remaining_happiness
                change_in_affinity = 5 if remaining_affinity >= 5 else remaining_affinity

            elif treat_sku == stats["hated_treat"]:
                change_in_happiness = -5 if remaining_happiness <= 95 else 0
                change_in_affinity = -2 if remaining_affinity <= 98 else 0
                change_in_hunger = 0 
            
            else:
                gold_earned = 3
                change_in_happiness = 2 if remaining_happiness >= 2 else remaining_happiness
                change_in_affinity = 2 if remaining_affinity >= 2 else remaining_affinity
                
            connection.execute(sqlalchemy.text("""INSERT INTO user_creature_connection (user_id, creature_id, affinity)
                                                VALUES (:user, :creature, :affinity)
                                            ON CONFLICT(user_id, creature_id)
                                            DO UPDATE 
                                            SET affinity = user_creature_connection.affinity + :affinity"""),
                            {"user": user_id, "creature": creature_id, "affinity": change_in_affinity})
                

            connection.execute(sqlalchemy.text("""UPDATE creatures 
                                            SET happiness = happiness + :happiness,
                                               hunger = hunger + :hunger 
                                            WHERE id = :creature"""),
                            {"happiness": change_in_happiness, "hunger": change_in_hunger, "creature": creature_id})
            
            connection.execute(sqlalchemy.text("""UPDATE users 
                                            SET gold = gold + :gold_earned 
                                            WHERE id = :user"""),
                            {"gold_earned": gold_earned, "user": user_id})
            
            connection.execute(sqlalchemy.text("""UPDATE users_treat_inventory 
                                            SET quantity = quantity - 1
                                            WHERE user_id = :user
                                               AND treat_sku = :sku"""),
                            {"user": user_id, "sku": treat_sku})

            
    return{
        "feed_success": feed_success, 
        "gold_earned": gold_earned,
        "change_in_hunger": change_in_hunger, 
        "change_in_happiness": change_in_happiness, 
        "change_in_affinity": change_in_affinity 
        }
    
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
        stats = connection.execute(sqlalchemy.text(""" SELECT happiness, COALESCE(user_creature_connection.affinity, 0) AS affinity
                                                   FROM creatures 
                                                   JOIN creature_types ON creatures.type = creature_types.type AND creatures.id = :creature
                                                   LEFT JOIN user_creature_connection ON creatures.id = user_creature_connection.creature_id AND user_id = :user_id"""),
                                                {"creature": creature_id, "user_id":user_id}).mappings().fetchone()

        print(f"Stats: {stats}")
        
        if stats["happiness"] < 100:
            happiness_change = 1
            played = True
            gold_earned = 2
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
        result = connection.execute(
            sqlalchemy.text(
                """
                  UPDATE user_creature_connection
                     SET is_adopted = true
                   WHERE user_id = :u_id
                     AND creature_id = :c_id
                     AND affinity = 100
                  RETURNING is_adopted
                """
            ),
            {"u_id": user_id, "c_id": creature_id}
        ).one_or_none()
    if result:
        print(f"Success. User {user_id} has adopted creature w/ id {creature_id}!")
        return {"success": True}
    print(f"Failure. User {user_id}'s affinity with creature id {creature_id} is not high enough for adoption.")
    return {"success": False}