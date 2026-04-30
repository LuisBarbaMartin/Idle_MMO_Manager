# Character Class
    charactername = classes.character(
        name="Test_Char"
        base_strength=12,
        base_intelligence=3,
        base_agility=6,
        base_wisdom=4
    )

Must enter in this order, (name, base strength, base intelligence, base agility, base wisdom)

# Equipment Class
    equipment_name = classes.Equipment(
        name="Iron Sword",
        slot="weapon1",
        rarity="common",
        hands="1",
        strength_bonus=4
    )