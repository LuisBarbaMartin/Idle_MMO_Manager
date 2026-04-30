import json

class character:
    def __init__(self, char_ID, name, base_strength, base_intelligence, base_agility, base_wisdom, level=1):
        self.char_ID = char_ID
        self.name = name
        self.level = level
        self.experience = 0

        #STUB - Base stats
        self.base_health = 50
        self.base_mana = 50
        self.base_strength = base_strength
        self.base_intelligence = base_intelligence
        self.base_agility = base_agility
        self.base_wisdom = base_wisdom
        
        #STUB - Equipment List:
        self.equipment = {
            "weapon1": None,
            "weapon2": None,
            "helm": None,
            "shoulder": None,
            "chest": None,
            "legs": None,
            "boots": None,
            "ring": None,
            "amulet": None,
            "ring1": None,
            "ring2": None,
        }
        
        self.max_health = self.calculate_max_health()
        self.health = self.max_health
        self.max_mana = self.calculate_max_mana()
        self.mana = self.max_mana
        
        
    #Core stat methods
        # def level_up(self):
        # def calculate_max_health(self):
        # def calculate_max_mana(self):
    #secondary stat methods
        # def get_strength(self):
        # def get_intelligence(self):
        # def get_agility(self):
        # def get_wisdom(self):
        # def get_equipment_health_bonus(self):
        # def get_equipment_mana_bonus(self):
    # def show_stats(self):
    
    def calculate_max_health(self):
        return self.base_health + (self.get_strength() * 2) + (self.level * 5) + self.get_equipment_health_bonus()

    def calculate_max_mana(self):
        return self.base_mana + (self.get_intelligence() * 2) + (self.level * 5) + self.get_equipment_mana_bonus()

    #Secondary stat methods
    def get_strength(self):
        total_strength = self.base_strength

        for item in self.equipment.values():
            if item is not None:
                total_strength += item.strength_bonus

        return total_strength

    def get_intelligence(self):
        total_intelligence = self.base_intelligence

        for item in self.equipment.values():
            if item is not None:
                total_intelligence += item.intelligence_bonus

        return total_intelligence
    
    def get_agility(self):
        total_agility = self.base_agility

        for item in self.equipment.values():
            if item is not None:
                total_agility += item.agility_bonus

        return total_agility
    
    def get_wisdom(self):
        total_wisdom = self.base_wisdom

        for item in self.equipment.values():
            if item is not None:
                total_wisdom += item.wisdom_bonus

        return total_wisdom
    
    def get_equipment_health_bonus(self):
        total_health_bonus = 0

        for item in self.equipment.values():
            if item is not None:
                total_health_bonus += item.health_bonus

        return total_health_bonus
    
    def get_equipment_mana_bonus(self):
        total_mana_bonus = 0

        for item in self.equipment.values():
            if item is not None:
                total_mana_bonus += item.mana_bonus

        return total_mana_bonus
    
    
    def show_stats(self):
        print(f"Name: {self.name}")
        print(f"Level: {self.level}")
        print(f"STR: {self.get_strength()} ({self.base_strength} base)")
        print(f"INT: {self.get_intelligence()} ({self.base_intelligence} base)")
        print(f"AGI: {self.get_agility()} ({self.base_agility} base)")
        print(f"WIS: {self.get_wisdom()} ({self.base_wisdom} base)")
        print(f"HP: {self.health}/{self.max_health}")
        print(f"MP: {self.mana}/{self.max_mana}")
        print("Equipment:")

        for slot, item in self.equipment.items():
            if item is None:
                print(f"  {slot}: Empty")
            else:
                print(f"  {slot}: {item.name}")
    
        
class Equipment:
    def __init__(self, 
                 item_ID, 
                 name, 
                 slot, 
                 rarity, 
                 hands=0, 
                 strength_bonus=0, 
                 intelligence_bonus=0, 
                 agility_bonus=0, 
                 wisdom_bonus=0, 
                 health_bonus=0, 
                 mana_bonus=0, 
                 flavor_text=""):
        
        self.item_ID = item_ID
        self.name = name
        self.slot = slot
        self.rarity = rarity
        self.hands = hands # determines if equipment is one-handed or two-handed, affects how many weapons can be equipped

        self.strength_bonus = strength_bonus
        self.intelligence_bonus = intelligence_bonus
        self.agility_bonus = agility_bonus
        self.wisdom_bonus = wisdom_bonus
        self.health_bonus = health_bonus
        self.mana_bonus = mana_bonus
        
        self.flavor_text = flavor_text
        
    @classmethod
    def from_json(cls, data):
        return cls(
            name=data["name"],
            slot=data["slot"],
            rarity=data["rarity"],
            strength_bonus=data.get("strength_bonus", 0),
            intelligence_bonus=data.get("intelligence_bonus", 0),
            agility_bonus=data.get("agility_bonus", 0),
            wisdom_bonus=data.get("wisdom_bonus", 0),
            health_bonus=data.get("health_bonus", 0),
            mana_bonus=data.get("mana_bonus", 0)
        )
    
    #TODO - implement equip restrictions based on hands (one-handed vs two-handed weapons)    
    # def check_hands(self):
        # if self.hands == 1:
            #dual_weild_allowed = True
        # elif self.hands == 2:
            # dual_weild_allowed = False
        #else:
            #if self.hands == 0:
                #ignore, not a weapon

class Guild:
    def __init__(self, name, members=None, inventory=None):
        self.name = name
        self.members = members if members is not None else []
        self.inventory = inventory if inventory is not None else {"gold": 0, "items": []}
        self.inventory = inventory
