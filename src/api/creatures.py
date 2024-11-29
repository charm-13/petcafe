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


@router.get("/")
def get_creatures(user_id: int):
    """
    Retrieves the list of creatures available to interact with in the cafe
    as well as the affinity the requesting user has with each creature.
    """
    try:
        with db.engine.begin() as connection:
            result = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT creatures.name, creatures.type, creatures.id, creatures.stage,
                        COALESCE(user_creature_connection.is_adopted, false) AS status,
                        COALESCE(user_creature_connection.affinity, 0) AS affinity
                    FROM creatures
                    LEFT JOIN user_creature_connection 
                        ON creatures.id = user_creature_connection.creature_id
                        AND user_id = :user_id
                    ORDER BY creatures.name
                """
                ),
                {"user_id": user_id},
            ).mappings()

        creatures = []

        for creature in result:
            creatures.append(
                {
                    "name": creature["name"],
                    "id": creature["id"],
                    "type": creature["type"],
                    "affinity": creature["affinity"],
                    "is_adopted": creature["status"],
                    "stage": creature["stage"],
                }
            )

        return creatures

    except Exception as e:
        print(f"An unexpected error has occurred: {e}")
        return {"success": False, "error": str(e)}


@router.get("/{creature_id}/stats")
def get_creature_stats(user_id: int, creature_id: int):
    """
    Retrieves the stats of the specified creature, including their current hunger and happiness levels,
    and their affinity with the user.
    """
    try:
        with db.engine.begin() as connection:
            c_stats = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT name, type, happiness, hunger, stage,
                        COALESCE(connections.affinity, 0) AS affinity
                    FROM creatures
                    LEFT JOIN user_creature_connection AS connections
                        ON connections.creature_id = creatures.id
                        AND connections.user_id = :u_id
                    WHERE creatures.id = :c_id
                """
                ),
                {"u_id": user_id, "c_id": creature_id},
            ).one()

        info = {
            "name": c_stats.name,
            "type": c_stats.type,
            "hunger": c_stats.hunger,
            "happiness": c_stats.happiness,
            "affinity": c_stats.affinity,
            "stage": c_stats.stage,
        }

        print(f"Creature {creature_id} info for user {user_id}:", info)
        return info

    except Exception as e:
        print(f"An unexpected error has occurred: {e}")
        return {"success": False, "error": str(e)}


@router.post("/{creature_id}/feed/{treat_sku}")
def feed_creature(user_id: int, creature_id: int, treat_sku: str):
    """
    Feeds the specified creature a treat of the specified id. Response returns the gold earned
    and changes in stats of the creature affected by the action, which are dependent on the treat
    used to feed the creature. If the creature has max hunger level at the time of the call,
    Feeds the specified creature a treat of the specified id. Response returns the gold earned
    and changes in stats of the creature affected by the action, which are dependent on the treat
    used to feed the creature. If the creature has max hunger level at the time of the call,
    the treat is not decremented from the user's inventory.
    """

    feed_success = (
        False  # If the creature ate the treat (only false if hunger maxed out)
    )
    gold_earned = 0  # 5 if favourite, 3 if normal, 0 if hated
    change_in_hunger = 0  # 0 if treat is hated; else dependent on treat satiety
    change_in_happiness = 0  # 10 if favorite, 5 if normal, -5 if hated
    change_in_affinity = 0  # 5 if favorite, 2 if normal, -2 if hated
    message = "Cannot feed this creature right now"

    try:
        with db.engine.begin() as connection:
            inventory = (
                connection.execute(
                    sqlalchemy.text(
                        """
                    SELECT 
                        u.id,
                        treat_sku,
                        satiety
                    FROM users u
                    JOIN (
                        SELECT user_id, treat_sku, satiety, quantity
                        FROM user_inventory_view
                        JOIN treats 
                            ON sku = treat_sku 
                        ) AS inventory
                        ON user_id = u.id
                        AND treat_sku = :sku
                        AND quantity > 0
                    WHERE u.id = :id
                """
                    ),
                    {"sku": treat_sku, "id": user_id},
                )
                .mappings()
                .fetchone()
            )

            print(f"Inventory: {inventory}")

            if not inventory:
                message = "This treat is not in your inventory"

            stats = (
                connection.execute(
                    sqlalchemy.text(
                        """
                    SELECT 
                        fav_treat, 
                        hated_treat, 
                        name,
                        happiness,
                        max_happiness, 
                        max_hunger, 
                        hunger,
                        COALESCE(user_creature_connection.affinity, 0) AS affinity
                    FROM creatures 
                    JOIN creature_types 
                        ON creatures.type = creature_types.type 
                        AND creatures.id = :creature
                    JOIN evolution_stages e
                        ON creatures.stage = e.stage
                    LEFT JOIN user_creature_connection
                        ON creatures.id = user_creature_connection.creature_id 
                    AND user_id = :user_id
                """
                    ),
                    {"creature": creature_id, "user_id": user_id},
                )
                .mappings()
                .fetchone()
            )

            if stats["hunger"] < stats["max_hunger"] and inventory:
                feed_success = True
                hunger = stats["hunger"]
                happiness = stats["happiness"]
                affinity = stats["affinity"]
                remaining_hunger = stats["max_hunger"] - hunger
                remaining_happiness = stats["max_happiness"] - happiness
                remaining_affinity = 100 - affinity
                change_in_hunger = (
                    inventory["satiety"]
                    if remaining_hunger >= inventory["satiety"]
                    else remaining_hunger
                )

                if treat_sku == stats["fav_treat"]:
                    gold_earned = 5
                    change_in_happiness = min(10, remaining_happiness)
                    change_in_affinity = min(5, remaining_affinity)
                    message = f"{stats['name']} devoured the treat!"

                elif treat_sku == stats["hated_treat"]:
                    change_in_happiness = max(-5, -1 * happiness)
                    change_in_affinity = max(-2, -1 * affinity)
                    change_in_hunger = 0
                    message = f"{stats['name']} spat out the treat!"

                else:
                    gold_earned = 3
                    change_in_happiness = min(2, remaining_happiness)
                    change_in_affinity = min(2, remaining_affinity)
                    message = f"{stats['name']} ate the treat"

                connection.execute(
                    sqlalchemy.text(
                        """
                        INSERT INTO user_creature_connection (user_id, creature_id, affinity)
                        VALUES (:user, :creature, :affinity)
                        ON CONFLICT(user_id, creature_id)
                        DO UPDATE 
                        SET affinity = user_creature_connection.affinity + :affinity
                    """
                    ),
                    {
                        "user": user_id,
                        "creature": creature_id,
                        "affinity": change_in_affinity,
                    },
                )

                connection.execute(
                    sqlalchemy.text(
                        """
                            UPDATE creatures 
                            SET happiness = happiness + :happiness,
                            hunger = hunger + :hunger 
                            WHERE id = :creature
                        """
                    ),
                    {
                        "happiness": change_in_happiness,
                        "hunger": change_in_hunger,
                        "creature": creature_id,
                    },
                )

                connection.execute(
                    sqlalchemy.text(
                        """
                            INSERT INTO user_gold (user_id, amount)
                            VALUES (:user, :gold_earned)
                        """
                    ),
                    {"gold_earned": gold_earned, "user": user_id},
                )

                connection.execute(
                    sqlalchemy.text(
                        """
                            INSERT INTO users_treat_inventory (user_id, treat_sku, quantity)
                            VALUES (:user, :sku, -1)
                        """
                    ),
                    {"user": user_id, "sku": treat_sku},
                )

        return {
            "feed_success": feed_success,
            "message": message,
            "gold_earned": gold_earned,
            "change_in_hunger": change_in_hunger,
            "change_in_happiness": change_in_happiness,
            "change_in_affinity": change_in_affinity,
        }

    except Exception as e:
        print(f"An unexpected error has occurred: {e}")
        return {"success": False, "error": str(e)}


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

    try:
        with db.engine.begin() as connection:
            stats = (
                connection.execute(
                    sqlalchemy.text(
                        """
                    SELECT 
                        happiness, e.max_happiness,
                        COALESCE(user_creature_connection.affinity, 0) AS affinity
                    FROM creatures 
                    JOIN creature_types 
                        ON creatures.type = creature_types.type AND creatures.id = :creature
                    JOIN evolution_stages e
                        ON creatures.stage = e.stage
                    LEFT JOIN user_creature_connection 
                        ON creatures.id = user_creature_connection.creature_id AND user_id = :user_id
                """
                    ),
                    {"creature": creature_id, "user_id": user_id},
                )
                .mappings()
                .fetchone()
            )

            print(f"Stats: {stats}")

            if stats["happiness"] <= stats["max_happiness"] - 1:
                happiness_change = 1
                played = True
                gold_earned = 2
                affinity_change = 1

                connection.execute(
                    sqlalchemy.text(
                        """
                        INSERT INTO user_creature_connection (user_id, creature_id, affinity)
                        VALUES (:user, :creature, :affinity)
                        ON CONFLICT(user_id, creature_id)
                        DO UPDATE 
                        SET affinity = user_creature_connection.affinity + :affinity
                    """
                    ),
                    {
                        "user": user_id,
                        "creature": creature_id,
                        "affinity": affinity_change,
                    },
                )

                connection.execute(
                    sqlalchemy.text(
                        """
                        UPDATE creatures 
                        SET happiness = happiness + :happiness_change 
                        WHERE id = :creature
                    """
                    ),
                    {"happiness_change": happiness_change, "creature": creature_id},
                )

                connection.execute(
                    sqlalchemy.text(
                        """
                        INSERT INTO user_gold (user_id, amount)
                        VALUES (:user, :gold_earned) 
                    """
                    ),
                    {"gold_earned": gold_earned, "user": user_id},
                )

        return {
            "play_success": played,
            "gold_earned": gold_earned,
            "change_in_affinity": affinity_change,
            "change_in_happiness": happiness_change,
        }

    except Exception as e:
        print(f"An unexpected error has occurred: {e}")
        return {"success": False, "error": str(e)}


@router.post("/{creature_id}/adopt")
def adopt_creature(user_id: int, creature_id: int):
    """
    Adopts a creature. User's affinity level with the specified creature must be 100.
    """
    try:
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
                {"u_id": user_id, "c_id": creature_id},
            ).one_or_none()

        if not result:
            print(
                f"Failure. User {user_id}'s affinity with creature id {creature_id} is not high enough for adoption."
            )
            return {"success": False}

        print(f"Success. User {user_id} has adopted creature with id {creature_id}!")
        return {"success": True}

    except Exception as e:
        print(f"An unexpected error has occurred: {e}")
        return {"success": False, "error": str(e)}


class NewCreature(BaseModel):
    creature_id_1: int
    creature_id_2: int
    name: str


@router.post("/breed")
def breed_creatures(user_id: int, new: NewCreature):
    """
    Breeds 2 creatures together. Creatures must be adopted by the user.
    """

    try:
        with db.engine.begin() as connection:
            result = (
                connection.execute(
                    sqlalchemy.text(
                        """SELECT creatures.type, fav_treat, hated_treat
                                    FROM creatures 
                                    JOIN user_creature_connection 
                                    ON creatures.id = creature_id 
                                    JOIN creature_types 
                                    ON creatures.type = creature_types.type
                                    WHERE user_id = :uid 
                                    AND (creatures.id = :cid1
                                    OR creatures.id = :cid2)
                                    AND is_adopted = TRUE"""
                    ),
                    {
                        "uid": user_id,
                        "cid1": new.creature_id_1,
                        "cid2": new.creature_id_2,
                    },
                )
                .mappings()
                .fetchall()
            )

            if not result or len(result) != 2:
                return {
                    "success": False,
                    "error": "One or both creatures are not adopted or do not exist",
                }

            # determine new type
            type1 = result[0]["type"].split("_")
            type2 = result[1]["type"].split("_")
            new_type = type1[0] + "_" + type2[1]

            # determine treat preferences
            fav_treat1 = result[0]["fav_treat"]
            fav_treat2 = result[1]["fav_treat"]
            hated_treat1 = result[0]["hated_treat"]
            hated_treat2 = result[1]["hated_treat"]

            if fav_treat1 != hated_treat2:
                fav, hated = fav_treat1, hated_treat2
            elif fav_treat2 != hated_treat1:
                fav, hated = fav_treat2, hated_treat1
            else:
                fav, hated = fav_treat1, hated_treat1

            id = connection.execute(
                sqlalchemy.text(
                    """INSERT INTO creatures(name, type)
                                                    VALUES (:name, :type) 
                                                    ON CONFLICT (name)
                                                    DO NOTHING
                                                    RETURNING id"""
                ),
                {"name": new.name, "type": new_type},
            ).scalar_one_or_none()

            if not id:
                return {"success": False, "error": "Name already exists"}

            connection.execute(
                sqlalchemy.text(
                    """INSERT INTO creature_types(type, fav_treat, hated_treat)
                                            VALUES (:new_type, :fav, :hated)
                                            ON CONFLICT (type)
                                            DO NOTHING"""
                ),
                {"new_type": new_type, "fav": fav, "hated": hated},
            )

            connection.execute(
                sqlalchemy.text(
                    """INSERT INTO user_creature_connection(user_id, creature_id, affinity, is_adopted)
                                            VALUES (:uid, :cid, 100, True)"""
                ),
                {"uid": user_id, "cid": id},
            )

    except Exception as e:
        print(f"An error occurred: {e}")
        return {"error": str(e)}

    return {
        "name": new.name,
        "id": id,
        "type": new_type,
        "fav_treat": fav,
        "hated_treat": hated,
    }


@router.post("/{creature_id}/evolve")
def evolve_creature(user_id: int, creature_id: int):
    """
    Evolves a creature to the next stage.
    """
    try:
        with db.engine.begin() as connection:
            status = (
                connection.execute(
                    sqlalchemy.text(
                        """
                SELECT 
                    creatures.stage, hunger, happiness, max_hunger, max_happiness,
                    COALESCE(user_creature_connection.is_adopted, false) AS is_adopted
                FROM creatures
                LEFT JOIN user_creature_connection ON creature_id = creatures.id 
                    AND user_id = :u_id
                JOIN evolution_stages ON creatures.stage = evolution_stages.stage
                WHERE creatures.id = :c_id
            """
                    ),
                    {"u_id": user_id, "c_id": creature_id},
                )
                .mappings()
                .fetchone()
            )

            if not status:
                return {
                    "success": False,
                    "error": f"Creature {creature_id} does not exist.",
                }

            if not status["is_adopted"]:
                return {
                    "success": False,
                    "error": f"Creature {creature_id} must already be adopted before evolving.",
                }

            if status["stage"] == 3:
                return {
                    "success": False,
                    "error": f"Creature {creature_id} is already at the highest stage.",
                }

            if (
                status["hunger"] < status["max_hunger"]
                or status["happiness"] < status["max_happiness"]
            ):
                return {
                    "success": False,
                    "error": f"Creature {creature_id} must have maximum stats before evolving.",
                }

            stage = (
                connection.execute(
                    sqlalchemy.text(
                        """
                UPDATE creatures
                SET stage = stage + 1 
                WHERE id = :c_id
                RETURNING stage
            """
                    ),
                    {"c_id": creature_id},
                )
                .mappings()
                .fetchone()
            )

            if not stage:
                return {
                    "success": False,
                    "error": f"Unable to evolve creature {creature_id}",
                }

        return stage

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {"success": False, "error": str(e)}
