import main.classes as classes

# test characters

fighter = classes.character(
    name="Brakka",
    base_strength=12,
    base_intelligence=3,
    base_agility=6,
    base_wisdom=4
)

# test equipment

rusty_sword = classes.Equipment(
    name="Rusty Sword", 
    slot="weapon1",
    rarity="common",
    strength_bonus=2
)

iron_sword = classes.Equipment(
    name="Iron Sword",
    slot="weapon1",
    rarity="common",
    strength_bonus=4
)

apprentice_staff = classes.Equipment(
    name="Apprentice Staff",
    slot="weapon1",
    rarity="common",
    intelligence_bonus=3,
    mana_bonus=15
)

oak_wand = classes.Equipment(
    name="Oak Wand",
    slot="weapon2",
    rarity="common",
    intelligence_bonus=2,
    wisdom_bonus=1,
    mana_bonus=10
)

leather_helm = classes.Equipment(
    name="Leather Helm",
    slot="helm",
    rarity="common",
    health_bonus=10
)

iron_helm = classes.Equipment(
    name="Iron Helm",
    slot="helm",
    rarity="uncommon",
    strength_bonus=1,
    health_bonus=25
)

shadow_boots = classes.Equipment(
    name="Shadow Boots",
    slot="boots",
    rarity="rare",
    agility_bonus=5
)

ring_of_vigor = classes.Equipment(
    name="Ring of Vigor",
    slot="ring1",
    rarity="uncommon",
    health_bonus=35
)

ring_of_focus = classes.Equipment(
    name="Ring of Focus",
    slot="ring2",
    rarity="uncommon",
    intelligence_bonus=2,
    mana_bonus=25
)

amulet_of_wisdom = classes.Equipment(
    name="Amulet of Wisdom",
    slot="amulet",
    rarity="rare",
    wisdom_bonus=4,
    mana_bonus=20
)

chestplate = classes.Equipment(
    name="Soldier's Chestplate",
    slot="chest",
    rarity="uncommon",
    strength_bonus=2,
    health_bonus=50
)

hunter_legs = classes.  Equipment(
    name="Hunter's Leggings",
    slot="legs",
    rarity="common",
    agility_bonus=2,
    health_bonus=15
)

# manually equip items for testing

fighter.equipment["weapon1"] = iron_sword
fighter.equipment["helm"] = iron_helm
fighter.equipment["chest"] = chestplate
fighter.equipment["ring1"] = ring_of_vigor

mage.equipment["weapon1"] = apprentice_staff
mage.equipment["weapon2"] = oak_wand
mage.equipment["ring2"] = ring_of_focus
mage.equipment["amulet"] = amulet_of_wisdom

rogue.equipment["weapon1"] = rusty_sword
rogue.equipment["boots"] = shadow_boots
rogue.equipment["legs"] = hunter_legs

cleric.equipment["weapon1"] = apprentice_staff
cleric.equipment["helm"] = leather_helm
cleric.equipment["amulet"] = amulet_of_wisdom

# recalculate stats after changing equipment

fighter.max_health = fighter.calculate_max_health()
fighter.health = fighter.max_health
fighter.max_mana = fighter.calculate_max_mana()
fighter.mana = fighter.max_mana

mage.max_health = mage.calculate_max_health()
mage.health = mage.max_health
mage.max_mana = mage.calculate_max_mana()
mage.mana = mage.max_mana

rogue.max_health = rogue.calculate_max_health()
rogue.health = rogue.max_health
rogue.max_mana = rogue.calculate_max_mana()
rogue.mana = rogue.max_mana

cleric.max_health = cleric.calculate_max_health()
cleric.health = cleric.max_health
cleric.max_mana = cleric.calculate_max_mana()
cleric.mana = cleric.max_mana

fighter.show_stats()
print()

mage.show_stats()
print()

rogue.show_stats()
print()

cleric.show_stats()