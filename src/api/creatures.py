from discord import HTTPException
import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src import database as db
from src.api import auth

router = APIRouter(
    prefix="/users/{user_id}/creatures",
    tags=["creatures"],
    dependencies=[Depends(auth.get_api_key)],
)


class NewCreature(BaseModel):
    creature_id_1: int
    creature_id_2: int
    name: str


@router.get("/")
def get_creatures(user_id: int):
    """
    Retrieves the list of creatures available to interact with in the cafe
    as well as the affinity the requesting user has with each creature.
    """
    try:
        with db.engine.begin() as connection:
            creatures = (
                connection.execute(
                    sqlalchemy.text(
                        """
                        SELECT
                            name,
                            creatures.id,
                            type,
                            COALESCE(conn.affinity, 0) AS affinity,
                            COALESCE(conn.is_adopted, false) AS is_adopted,
                            stage
                        FROM creatures
                        JOIN users
                            ON users.id = :user_id
                        LEFT JOIN user_creature_connection AS conn
                            ON conn.creature_id = creatures.id
                            AND conn.user_id = users.id
                        ORDER BY creatures.name
                        """
                    ),
                    {"user_id": user_id},
                )
                .mappings()
                .all()
            )

        if not creatures:
            raise HTTPException(
                status_code=404, details=f"User {user_id} does not exist."
            )

        print(f"[get_creatures] User {user_id}'s creature list:", creatures)
        return creatures

    except Exception as e:
        print("[get_creatures] An unexpected error has occurred:", e)
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve creatures. Error: {e}"
        )


@router.get("/{creature_id}/stats")
def get_creature_stats(user_id: int, creature_id: int):
    """
    Retrieves the stats of the specified creature, including their current hunger and happiness levels,
    and their affinity with the user.
    """
    try:
        with db.engine.begin() as connection:
            c_stats = (
                connection.execute(
                    sqlalchemy.text(
                        """
                        SELECT
                            name,
                            type,
                            hunger,
                            happiness,
                            COALESCE(conn.affinity, 0) AS affinity,
                            stage
                        FROM creatures
                        JOIN users
                            ON users.id = :u_id
                            AND creatures.id = :c_id
                        LEFT JOIN user_creature_connection AS conn
                            ON conn.creature_id = creatures.id
                            AND conn.user_id = users.id
                        """
                    ),
                    {"u_id": user_id, "c_id": creature_id},
                )
                .mappings()
                .one_or_none()
            )

        if not c_stats:
            raise HTTPException(
                status_code=404,
                detail=f"User {user_id} and/or creature {creature_id} does not exist.",
            )

        print(
            f"[get_creature_stats] Creature {creature_id} info for user {user_id}:",
            c_stats,
        )
        return c_stats

    except Exception as e:
        print("[get_creature_stats] An unexpected error has occurred:", e)
        raise HTTPException(
            status_code=500, detail=f"Failed to retrieve creature stats. Error: {e}"
        )


@router.post("/{creature_id}/feed/{treat_sku}")
def feed_creature(user_id: int, creature_id: int, treat_sku: str):
    """
    Feeds the specified creature a treat of the specified id. Response returns the gold earned
    and changes in stats of the creature affected by the action, which are dependent on the treat
    used to feed the creature. If the creature has max hunger level at the time of the call,
    the treat is not decremented from the user's inventory.
    """

    try:
        with db.engine.begin() as connection:
            inventory = (
                connection.execute(
                    sqlalchemy.text(
                        """
                        SELECT
                            sku,
                            satiety,
                            COALESCE(quantity, 0) AS qty
                        FROM treats
                        JOIN users
                            ON users.id = :id
                            AND sku = :sku
                        LEFT JOIN user_inventory_view AS inv
                            ON inv.treat_sku = sku
                            AND inv.user_id = users.id
                        """
                    ),
                    {"sku": treat_sku, "id": user_id},
                )
                .mappings()
                .one_or_none()
            )

            if not inventory:
                raise HTTPException(
                    status_code=404,
                    detail=f"User {user_id} and/or treat {treat_sku} does not exist.",
                )
            if inventory["qty"] == 0:
                raise HTTPException(
                    status_code=403,
                    detail=f"No '{treat_sku}'s found in inventory.",
                )

            print(f"[feed_creature] User {user_id}'s inventory:", inventory)

            stats = (
                connection.execute(
                    sqlalchemy.text(
                        """
                        SELECT
                            name,
                            fav_treat,
                            hated_treat,
                            happiness,
                            max_happiness,
                            max_hunger,
                            hunger,
                            COALESCE(conn.affinity, 0) AS affinity
                        FROM creatures
                        JOIN creature_types
                            ON creatures.type = creature_types.type
                            AND creatures.id = :creature
                        JOIN evolution_stages e
                            ON creatures.stage = e.stage
                        LEFT JOIN user_creature_connection AS conn
                            ON conn.creature_id = creatures.id
                            AND conn.user_id = :user_id
                        """
                    ),
                    {"creature": creature_id, "user_id": user_id},
                )
                .mappings()
                .one_or_none()
            )

            if not stats:
                raise HTTPException(
                    status_code=404,
                    detail=f"Creature {creature_id} does not exist.",
                )

            if stats["hunger"] == stats["max_hunger"]:
                raise HTTPException(
                    status_code=409,
                    detail=f"{stats['name']} is too full right now! Please try again later.",
                )

            hunger = stats["hunger"]
            happiness = stats["happiness"]
            affinity = stats["affinity"]
            remaining_hunger = stats["max_hunger"] - hunger
            remaining_happiness = stats["max_happiness"] - happiness
            remaining_affinity = 100 - affinity

            change_in_hunger = min(inventory["satiety"], remaining_hunger)

            if treat_sku == stats["fav_treat"]:
                gold_earned = 5
                change_in_happiness = min(10, remaining_happiness)
                change_in_affinity = min(5, remaining_affinity)
                message = f"{stats['name']} devoured the treat!"

            elif treat_sku == stats["hated_treat"]:
                gold_earned = 0
                change_in_hunger = 0
                change_in_happiness = max(-5, -1 * happiness)
                change_in_affinity = max(-2, -1 * affinity)
                message = f"{stats['name']} spat out the treat!"
            else:
                gold_earned = 3
                change_in_happiness = min(2, remaining_happiness)
                change_in_affinity = min(2, remaining_affinity)
                message = f"{stats['name']} ate the treat."

            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO user_creature_connection (user_id, creature_id, affinity)
                    VALUES (:user, :creature, :affinity)
                    ON CONFLICT (user_id, creature_id) DO UPDATE
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
            "message": message,
            "gold_earned": gold_earned,
            "change_in_hunger": change_in_hunger,
            "change_in_happiness": change_in_happiness,
            "change_in_affinity": change_in_affinity,
        }

    except Exception as e:
        print("[feed_creature] An unexpected error has occurred:", e)
        raise HTTPException(
            status_code=500, detail=f"Failed to feed creature. Error: {e}"
        )


@router.post("/{creature_id}/play")
def play_with_creature(user_id: int, creature_id: int):
    """
    Plays with the specified creature. Increases a creature's happiness and affinity with user.
    Playing with a pet at max happiness does not earn the user any gold or affinity.
    """

    try:
        with db.engine.begin() as connection:
            stats = (
                connection.execute(
                    sqlalchemy.text(
                        """
                        SELECT
                            name,
                            happiness,
                            e.max_happiness
                        FROM creatures
                        JOIN creature_types
                            ON creature_types.type = creatures.type
                            AND creatures.id = :creature
                        JOIN evolution_stages e
                            ON creatures.stage = e.stage
                        JOIN users
                            ON users.id = :user_id
                        """
                    ),
                    {"creature": creature_id, "user_id": user_id},
                )
                .mappings()
                .one_or_none()
            )
            if not stats:
                raise HTTPException(
                    status_code=404,
                    detail=f"User {user_id} and/or creature {creature_id} does not exist.",
                )

            print(
                f"[play_with_creature] Creature {creature_id} info for user {user_id}:",
                stats,
            )

            if stats["happiness"] == stats["max_happiness"]:
                raise HTTPException(
                    status_code=409,
                    detail=f"{stats['name']} is very happy right now. Try playing with them again later.",
                )

            affinity = connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO user_creature_connection (user_id, creature_id, affinity)
                    VALUES (:user, :creature, 1)
                    ON CONFLICT (user_id, creature_id) DO UPDATE
                    SET affinity = LEAST(100, user_creature_connection.affinity + 1)
                    RETURNING affinity
                    """
                ),
                {"user": user_id, "creature": creature_id},
            ).scalar_one()

            happiness = connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE creatures
                    SET happiness = happiness + 1
                    WHERE id = :creature
                    RETURNING happiness
                    """
                ),
                {"creature": creature_id},
            ).scalar_one()

            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO user_gold (user_id, amount)
                    VALUES (:user, 2)
                    """
                ),
                {"user": user_id},
            )

        return {
            "gold_earned": 2,
            "affinity": affinity,
            "happiness": happiness,
        }

    except Exception as e:
        print("[play_with_creature] An unexpected error has occurred:", e)
        raise HTTPException(
            status_code=500, detail=f"Failed to play with creature. Error: {e}"
        )


@router.post("/{creature_id}/adopt")
def adopt_creature(user_id: int, creature_id: int):
    """
    Adopts a creature. User's affinity level with the specified creature must be 100.
    """
    try:
        with db.engine.begin() as connection:
            stats = (
                connection.execute(
                    sqlalchemy.text(
                        """
                        SELECT
                            name,
                            COALESCE(is_adopted, false) AS is_adopted,
                            COALESCE(affinity, 0) AS affinity
                        FROM creatures
                        JOIN USERS
                            ON users.id = :u_id
                            AND creatures.id = :c_id
                        LEFT JOIN user_creature_connection AS conn
                            ON conn.creature_id = creatures.id
                            AND conn.user_id = users.id
                        """
                    ),
                    {"u_id": user_id, "c_id": creature_id},
                )
                .mappings()
                .one_or_none()
            )

            if not stats:
                raise HTTPException(
                    status_code=404,
                    detail=f"User {user_id} and/or creature {creature_id} does not exist.",
                )
            if stats["is_adopted"]:
                raise HTTPException(
                    status_code=409,
                    detail=f"{stats['name']} has already been adopted by user {user_id}.",
                )
            if stats["affinity"] < 100:
                raise HTTPException(
                    status_code=403,
                    detail=f"Affinity with {stats['name']} is not high enough! Have: {stats['affinity']}, Needed: 100",
                )

            connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE user_creature_connection
                    SET is_adopted = true
                    WHERE users_id = :u_id
                    AND creatures_id = :c_id
                    """
                ),
                {"u_id": user_id, "c_id": creature_id},
            )

        print(f"User {user_id} has adopted {stats['name']}!")
        return "OK"

    except Exception as e:
        print("[adopt_creature] An unexpected error has occurred:", e)
        raise HTTPException(
            status_code=500, detail=f"Failed to adopt creature. Error: {e}"
        )


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
                        """
                        SELECT
                            name,
                            creatures.id,
                            creatures.type,
                            fav_treat,
                            hated_treat,
                            COALESCE(is_adopted, false) AS is_adopted
                        FROM creatures
                        JOIN creature_types
                            ON creatures.type = creature_types.type
                            AND (creatures.id = :cid1 OR creatures.id = :cid2)
                        JOIN users
                            ON users.id = :uid
                        LEFT JOIN user_creature_connection AS conn
                            ON conn.creature_id = creatures.id
                            AND conn.user_id = users.id
                        """
                    ),
                    {
                        "uid": user_id,
                        "cid1": new.creature_id_1,
                        "cid2": new.creature_id_2,
                    },
                )
                .mappings()
                .all()
            )

            if len(result) < 2:
                raise HTTPException(
                    status_code=404,
                    detail=f"User {user_id} and/or one or both creatures do not exist.",
                )
            else:
                for c in result:
                    if not c["is_adopted"]:
                        raise HTTPException(
                            status_code=403,
                            detail=f"{c['name']} (id {c['id']}) isn't adopted by user {user_id}!",
                        )

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
                    """
                    INSERT INTO creatures (name, type)
                    VALUES (:name, :type)
                    ON CONFLICT (name) DO NOTHING
                    RETURNING id
                    """
                ),
                {"name": new.name, "type": new_type},
            ).scalar_one_or_none()

            if not id:
                raise HTTPException(
                    status_code=409,
                    detail="A creature with the chosen name already exists!",
                )

            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO creature_types (type, fav_treat, hated_treat)
                    VALUES (:new_type, :fav, :hated)
                    ON CONFLICT (type) DO NOTHING
                    """
                ),
                {"new_type": new_type, "fav": fav, "hated": hated},
            )

            connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO user_creature_connection (user_id, creature_id, affinity, is_adopted)
                    VALUES (:u_id, :c_id, 100, true)
                    """
                ),
                {"u_id": user_id, "c_id": id},
            )

        return {
            "name": new.name,
            "id": id,
            "type": new_type,
            "fav_treat": fav,
            "hated_treat": hated,
        }

    except Exception as e:
        print("[breed_creatures] An unexpected error has occurred:", e)
        raise HTTPException(
            status_code=500, detail=f"Failed to breed creatures. Error: {e}"
        )


@router.post("/{creature_id}/evolve")
def evolve_creature(user_id: int, creature_id: int):
    """
    Evolves a creature to the next stage.
    """
    try:
        with db.engine.begin() as connection:
            stats = (
                connection.execute(
                    sqlalchemy.text(
                        """
                        SELECT
                            name,
                            creatures.stage,
                            hunger = max_hunger AS is_full,
                            happiness = max_happiness AS is_happy,
                            COALESCE(conn.is_adopted, false) AS is_adopted
                        FROM creatures
                        JOIN users
                            ON users.id = :u_id
                            AND creatures.id = :c_id
                        JOIN evolution_stages
                            ON creatures.stage = evolution_stages.stage
                        LEFT JOIN user_creature_connection AS conn
                            ON conn.creature_id = creatures.id
                            AND conn.user_id = users.id
                        """
                    ),
                    {"u_id": user_id, "c_id": creature_id},
                )
                .mappings()
                .one_or_none()
            )

            if not stats:
                raise HTTPException(
                    status_code=404,
                    detail=f"User {user_id} and/or creature {creature_id} does not exist.",
                )
            if not stats["is_adopted"]:
                raise HTTPException(
                    status_code=403,
                    detail=f"{stats['name']} must already be adopted before evolving.",
                )
            if stats["stage"] == 3:
                raise HTTPException(
                    status_code=403,
                    detail=f"{stats['name']} is already at the highest stage of evolution.",
                )
            if not stats["is_full"] or not stats["is_happy"]:
                raise HTTPException(
                    status_code=403,
                    detail=f"{stats['name']} must be fully fed and satisfied before evolving!",
                )

            stage = connection.execute(
                sqlalchemy.text(
                    """
                        UPDATE creatures
                        SET stage = LEAST(3, stage + 1)
                        WHERE id = :c_id
                        RETURNING stage
                        """
                ),
                {"c_id": creature_id},
            ).scalar_one()

        return {"stage": stage}

    except Exception as e:
        print("[evolve_creature] An unexpected error has occurred:", e)
        raise HTTPException(
            status_code=500, detail=f"Failed to evolve creature. Error: {e}"
        )
