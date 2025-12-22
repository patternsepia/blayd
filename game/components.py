# game/components.py

class BodyComponent(Component):
    def __init__(self, body_plan_data):
        self.slots = {}     
        self.slot_tags = {} 
        self.slot_order = [] # <--- ADD THIS
        
        for part in body_plan_data:
            name = part.get("name", "unknown")
            tags = part.get("tags", [])
            self.slots[name] = None
            self.slot_tags[name] = tags
            self.slot_order.append(name) # <--- ADD THIS