import main.classes as classes
import main.functions as functions

# test characters

fighter = classes.character(
    name="Brakka",
    base_strength=12,
    base_intelligence=3,
    base_agility=6,
    base_wisdom=4
)

# test equipment

iron_sword = classes.Equipment(
    name="Iron Sword",
    slot="weapon1",
    rarity="common",
    strength_bonus=4
)

iron_helm = classes.Equipment(
    name="Iron Helm",
    slot="helm",
    rarity="uncommon",
    strength_bonus=1,
    health_bonus=25
)

ring_of_vigor = classes.Equipment(
    name="Ring of Vigor",
    slot="ring1",
    rarity="uncommon",
    health_bonus=35
)

chestplate = classes.Equipment(
    name="Soldier's Chestplate",
    slot="chest",
    rarity="uncommon",
    strength_bonus=2,
    health_bonus=50
)

# test guild obj
test_guild = classes.Guild(
    name="Test Guild",
    members=[fighter],
    inventory={"items": [iron_sword, iron_helm, ring_of_vigor, chestplate]}
)

functions.equip_item(fighter, test_guild, iron_sword)
functions.equip_item(fighter, test_guild, iron_helm)
functions.equip_item(fighter, test_guild, ring_of_vigor)
functions.equip_item(fighter, test_guild, chestplate)
# manually equip items for testing

#fighter.equipment["weapon1"] = iron_sword
#fighter.equipment["helm"] = iron_helm
#fighter.equipment["chest"] = chestplate
#fighter.equipment["ring1"] = ring_of_vigor

# recalculate stats after changing equipment

fighter.max_health = fighter.calculate_max_health()
fighter.health = fighter.max_health
fighter.max_mana = fighter.calculate_max_mana()
fighter.mana = fighter.max_mana


fighter.show_stats()
print()