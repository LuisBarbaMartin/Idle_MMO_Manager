from flask import Flask, jsonify, render_template, request

import classes
import event_runner
import functions


app = Flask(__name__)
TEST_STATE_FILE = "data/test-file.JSON"

characters = functions.load_characters()
items = functions.load_items()
quests = functions.load_quests()
guild = None
event_log = []


def get_character_key(character):
    for character_key, loaded_character in characters.items():
        if loaded_character is character:
            return character_key

    return None


def serialize_item(item):
    return {
        "instance_id": getattr(item, "instance_id", None),
        "template_id": getattr(item, "template_id", None),
        "name": item.name,
        "slot": item.slot,
        "rarity": item.rarity,
        "hands": item.hands,
        "level_requirement": item.level_requirement,
        "job_restriction": item.job_restriction,
        "strength_bonus": item.strength_bonus,
        "intelligence_bonus": item.intelligence_bonus,
        "agility_bonus": item.agility_bonus,
        "wisdom_bonus": item.wisdom_bonus,
        "health_bonus": item.health_bonus,
        "mana_bonus": item.mana_bonus,
        "flavor_text": item.flavor_text
    }


def serialize_character(character):
    return {
        **character.get_stats(),
        "equipment": {
            slot: serialize_item(item) if item is not None else None
            for slot, item in character.equipment.items()
        },
        "busy": event_runner.character_has_active_quest(guild, character)
    }


def serialize_quest(quest_key, quest_data):
    return {
        "key": quest_key,
        "name": quest_data["name"],
        "time_to_complete_seconds": quest_data.get("time_to_complete_seconds", 0),
        "check_count": len(quest_data.get("checks", [])),
        "rewards": quest_data.get("rewards", {})
    }


def serialize_active_quest(active_quest):
    progress = event_runner.get_active_quest_progress(active_quest)
    duration = progress["time_to_complete_seconds"]
    elapsed = progress["time_elapsed_seconds"]
    progress_percent = 100 if duration == 0 else (elapsed / duration) * 100

    return {
        "quest_name": active_quest["quest_name"],
        "character_name": active_quest["character_name"],
        "time_elapsed_seconds": elapsed,
        "time_to_complete_seconds": duration,
        "progress_percent": max(0, min(progress_percent, 100)),
        "checks": [
            {
                "description": scheduled_check["check"]["description"],
                "complete": scheduled_check["complete"],
                "passed": (
                    scheduled_check["result"]["passed"]
                    if scheduled_check["result"] is not None
                    else None
                )
            }
            for scheduled_check in active_quest["check_schedule"]
        ]
    }


def update_game_state():
    completed_quests = event_runner.update_guild_quests(
        guild,
        items,
        print_updates=False
    )

    for active_quest in completed_quests:
        result = active_quest["result"]
        outcome = "completed" if result["success"] else "failed"
        event_log.append(
            f"{result['character_name']} {outcome} {result['quest_name']}."
        )


def load_test_state():
    global guild

    for character in characters.values():
        character.equipment = {
            "weapon1": None,
            "weapon2": None,
            "helm": None,
            "chest": None,
            "legs": None,
            "boots": None,
            "amulet": None,
            "ring1": None,
            "ring2": None,
        }
        character.max_health = character.calculate_max_health()
        character.health = character.max_health
        character.max_mana = character.calculate_max_mana()
        character.mana = character.max_mana
        character.experience = 0

    guild = functions.load_guild_state(TEST_STATE_FILE, characters, items)
    event_log.clear()
    event_log.append("Loaded test file.")


def load_empty_state():
    global guild

    for character in characters.values():
        character.equipment = {
            "weapon1": None,
            "weapon2": None,
            "helm": None,
            "chest": None,
            "legs": None,
            "boots": None,
            "amulet": None,
            "ring1": None,
            "ring2": None,
        }
        character.max_health = character.calculate_max_health()
        character.health = character.max_health
        character.max_mana = character.calculate_max_mana()
        character.mana = character.max_mana
        character.experience = 0

    guild = classes.Guild(
        name="No Guild Loaded",
        members=[],
        inventory={
            "gold": 0,
            "items": []
        }
    )
    event_log.clear()
    event_log.append("No test file loaded.")


load_empty_state()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/quests")
def quest_screen():
    return render_template("quests.html")


@app.route("/inventory")
def inventory_screen():
    return render_template("inventory.html")


@app.route("/api/state")
def get_state():
    update_game_state()

    return jsonify({
        "guild": {
            "name": guild.name,
            "gold": guild.inventory["gold"],
            "inventory": [serialize_item(item) for item in guild.inventory["items"]],
            "active_quests": [
                serialize_active_quest(active_quest)
                for active_quest in guild.active_quests
            ]
        },
        "characters": [
            {
                "key": get_character_key(character),
                **serialize_character(character)
            }
            for character in guild.members
        ],
        "quests": [
            serialize_quest(quest_key, quest_data)
            for quest_key, quest_data in quests.items()
        ],
        "event_log": event_log[-20:]
    })


@app.route("/api/load-test-file", methods=["POST"])
def load_test_file():
    load_test_state()
    return jsonify({"ok": True})


@app.route("/api/start-quest", methods=["POST"])
def start_quest():
    data = request.get_json()
    quest_key = data["quest_key"]
    character_key = data["character_key"]
    character = characters[character_key]

    if character not in guild.members:
        return jsonify({
            "ok": False,
            "message": f"{character.name} is not a member of the loaded guild."
        }), 400

    active_quest = event_runner.start_guild_quest(
        guild=guild,
        character=character,
        quest_data=quests[quest_key]
    )

    if active_quest is None:
        return jsonify({
            "ok": False,
            "message": f"{character.name} is already on a quest."
        }), 400

    event_log.append(f"{character.name} started {quests[quest_key]['name']}.")

    return jsonify({"ok": True})


@app.route("/api/equip-item", methods=["POST"])
def equip_item():
    data = request.get_json()
    character_key = data["character_key"]
    instance_id = data["instance_id"]
    character = characters[character_key]

    if character not in guild.members:
        return jsonify({
            "ok": False,
            "message": f"{character.name} is not a member of the loaded guild."
        }), 400

    if event_runner.character_has_active_quest(guild, character):
        return jsonify({
            "ok": False,
            "message": f"{character.name} cannot change equipment while questing."
        }), 400

    item = functions.find_inventory_item_by_instance_id(guild, instance_id)

    if item is None:
        return jsonify({
            "ok": False,
            "message": "That item is not in guild inventory."
        }), 400

    can_equip, reason = functions.can_equip_item(character, item)
    if not can_equip:
        return jsonify({
            "ok": False,
            "message": reason
        }), 400

    functions.equip_item(character, guild, item)
    event_log.append(f"{character.name} equipped {item.name}.")

    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
