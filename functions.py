import json

from classes import Equipment, character


def load_json_file(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


def load_items(file_path="data/items.JSON"):
    items_data = load_json_file(file_path)
    return {
        item_key: Equipment.from_json(item_data)
        for item_key, item_data in items_data.items()
    }


def load_characters(file_path="data/characters.JSON"):
    characters_data = load_json_file(file_path)
    return {
        character_key: character.from_json(character_data)
        for character_key, character_data in characters_data.items()
    }


def load_quests(file_path="data/quests.JSON"):
    return load_json_file(file_path)


#TODO - Tick Rate will need to be remade once the event_handler() is implemented. This is just a placeholder for testing purposes.
def global_tick(player):
    """
    Runs once per game tick.
    Put all passive/idle updates here.
    """

    # Example: passive gold gain
    player["gold"] += player["gold_per_tick"]

    # Example: passive XP gain
    player["xp"] += player["xp_per_tick"]

    # Example: cooldown reduction
    if player["quest_cooldown"] > 0:
        player["quest_cooldown"] -= 1

def equip_item(character, guild, item):
    """
    equips an item from inventory.
    replaced equipment returns to inventory.
    stats are recalculated after equipping.
    """

    inventory_items = guild.inventory["items"]

    if item.slot not in character.equipment:
        print(f"Invalid equipment slot: {item.slot}")
        return

    if item not in inventory_items:
        print(f"{item.name} is not in {guild.name}'s inventory.")
        return

    replaced_item = character.equipment[item.slot]

    character.equipment[item.slot] = item
    inventory_items.remove(item)

    if replaced_item is not None:
        inventory_items.append(replaced_item)
        print(f"{character.name} equipped {item.name}, replacing {replaced_item.name}.")
    else:
        print(f"{character.name} equipped {item.name}.")

    character.max_health = character.calculate_max_health()
    character.health = min(character.health, character.max_health)

    character.max_mana = character.calculate_max_mana()
    character.mana = min(character.mana, character.max_mana)

def rest(character):
    """
    Restores health and mana to full.
    Can only be used outside of combat.
    """

    # Example implementation, adjust as needed
    character.health = character.max_health
    character.mana = character.max_mana
    print(f"{character.name} has rested and restored health and mana to full.")
