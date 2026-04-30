import classes
import event_runner
import functions


characters = functions.load_characters()
items = functions.load_items()
quests = functions.load_quests()

fighter = characters["fighter_0001"]
iron_sword = items["item_0001_iron_sword"]
ghost_item = items["item_0000_blank"]

test_guild = classes.Guild(
    name="Test Guild",
    members=[fighter],
    inventory={
        "gold": 500,
        "items": [iron_sword, ghost_item]
    }
)

functions.equip_item(fighter, test_guild, iron_sword)
functions.equip_item(fighter, test_guild, ghost_item)

functions.rest(fighter)
fighter.show_stats()
print()
print("Guild Inventory:")
for item in test_guild.inventory["items"]:
    print(f"  {item.name}")

print(f"Guild Gold: {test_guild.inventory['gold']}")

print()
quest_result = event_runner.event_runner(
    fighter.get_stats(),
    quests["quest_0001_locked_cellar"]
)
event_runner.print_event_result(quest_result)
event_runner.apply_quest_rewards(quest_result, fighter, test_guild, items)

print()
print("After Quest Rewards:")
print(f"Guild Gold: {test_guild.inventory['gold']}")
print(f"Fighter XP: {fighter.experience}")
print("Guild Inventory:")
for item in test_guild.inventory["items"]:
    print(f"  {item.name}")
