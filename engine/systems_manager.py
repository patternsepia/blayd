from typing import List
from .old_ecs import World
from .old_comps import (
    Position, Locomotion, BodyAppearance, WornVisual, 
    Container, PartHost, Installable, RenderLayer, Name
)

class RenderSystem:
    def angle_to_index(self, degrees: float, offset: int = 0) -> int:
        norm = degrees % 360
        # Center the 22.5 degree slice on the axis
        index = int((norm + 11.25) // 22.5)
        return (index + offset) % 16

    def render_entity(self, world: World, entity_id: int):
        # 1. Orientation
        loco = world.get_component(entity_id, Locomotion)
        facing = loco.facing_angle if loco else 0.0
        dir_index = self.angle_to_index(facing)

        # 2. Collect Layers
        layers = []

        # Body
        body = world.get_component(entity_id, BodyAppearance)
        if body:
            layers.append({
                'sprite': body.base_sprite,
                'layer': RenderLayer.BODY,
                'note': "Body"
            })

        # Worn Items (Paper Doll)
        container = world.get_component(entity_id, Container)
        if container:
            for item_id in container.items:
                worn = world.get_component(item_id, WornVisual)
                if worn:
                    # Dynamic Z-Ordering (Check if item should go behind back)
                    layer_depth = worn.layer
                    if dir_index in worn.behind_indices:
                        layer_depth = RenderLayer.CLOAK_BACK 

                    layers.append({
                        'sprite': worn.sprite,
                        'layer': layer_depth,
                        'note': world.get_component(item_id, Name).text
                    })

        # 3. Sort & "Draw"
        layers.sort(key=lambda x: x['layer'])
        
        # (Replace print with your actual Blit/Draw code)
        print(f"Drawing Entity {entity_id} @ {facing}°:")
        for l in layers:
            print(f"  [{l['layer']}] {l['note']} (Frame: {dir_index})")

class MaintenanceSystem:
    def install_part(self, world: World, vehicle_id: int, part_id: int):
        host = world.get_component(vehicle_id, PartHost)
        part = world.get_component(part_id, Installable)
        
        if not host or not part: return

        slot = part.target_slot
        
        # Check slot existence and occupancy
        if slot not in host.slots:
            print(f"This vehicle doesn't have a '{slot}' slot.")
            return
            
        if host.slots[slot] is not None:
            print(f"Slot '{slot}' is already full.")
            return

        # Perform Install
        host.slots[slot] = part_id
        part.is_installed = True
        print(f"Success: Installed part into {slot}.")