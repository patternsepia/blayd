# **Blayd — Design Bible (Draft 0.1)**

---

## **1. Vision Statement**
Blayd is a simulation-heavy medieval roguelike driven by systemic interactions rather than scripts. Every entity—creatures, objects, weather, institutions—follows coherent rules. Consequences persist, NPCs remember, factions evolve, and the world responds organically to the player’s actions.

Blayd emphasizes **interactivity**, **persistence**, **emergence**, and **simulation depth** while maintaining playability on 2015 upper-end hardware.

---

## **2. Core Pillars**
### **2.1 Systemic Consistency**
- All systems share unified logic (AI needs, legal responses, world simulation, crafting, survival).
- Player is never an exception.

### **2.2 Persistent World Simulation**
- NPCs act autonomously: farming, working, traveling, participating in social/legal events.
- Factions update territory, resources, relations.
- Injuries heal over time with medical care based on simulation.

### **2.3 Procedural Generation**
- Fully generated world maps, towns, NPC cultures, vegetation, fauna, economic conditions.
- Mix of large open areas and dungeon-like interiors.

### **2.4 Per-Part Injury Model**
- Each creature tracks per-part health, wounds, blood loss.
- Medical and survival mechanics integrate tightly.

### **2.5 Immersive Player Agency**
- Every object can be interacted with meaningfully.
- Actions change the world long-term.

---

## **3. Gameplay Overview**
### **3.1 Loop**
1. Explore and scavenge.
2. Manage hunger, thirst, injury, sleep.
3. Navigate dynamic factional politics.
4. Craft equipment and shelter.
5. Complete emergent goals.
6. Survive.

### **3.2 World Structure**
- Overland map with regions (forests, plains, mountains, swamps).
- Towns with legal systems, economies.
- Dungeons, ruins, castles with procedural room/corridor systems.
- Weather system may be fully deterministic based on date.

### **3.3 Interactions**
- Combat (melee, ranged, environmental hazards).
- Crafting, construction, farming.
- Social: persuasion, lying, assisting, trading.
- Crime: trespassing, arson, murder → legal consequences.

---

## **4. Stats and Skills**
### **4.1 Stats (10 sliders, 1–20)**
- Strength, Endurance, Agility, Dexterity, Perception, Intelligence, Willpower, Concentration, Charisma, Luck.

### **4.2 ASDF (Adaptive Skill Dynamics Framework)**
- Uses 10 human qualities + domain, complexity, skill level, context, duration, feedback.
- Powers all success/failure checks.

---

## **5. UI Systems**
### **5.1 Character Creation**
- Tabs: Stats, Identity, Appearance (31 parts), Equipment (inventory pool).
- Three-pane equipment UI + net-value indicator.

### **5.2 Crafting Menu**
- Fullscreen categorical tabs: Ammo, Weapons, Food, Drink, Clothes, Armor, Storage, Medical, Tools, Chemicals, Misc.
- Overflow tabs with visual ‘<’ and ‘>’.

### **5.3 Ranged Combat HUD (Aim Mode)**
- Triggered with **F**.
- WASD to choose tile.
- ‘<’ and ‘>’ cycle visible targets.
- Charge with `.`.
- Accuracy from Perception + charge (Concentration-modulated).
- Damage from bow + arrow.

---

## **6. NPC Simulation**
### **6.1 Needs**
- Hunger, thirst, rest.
- Safety, medical treatment.
- Social needs.

### **6.2 Behavior**
- Memory-driven reactions.
- Reputation and legal status matter.
- Faction allegiance determines cooperation or conflict.

### **6.3 Factions**
- Procedurally generated.
- Territory control.
- Resource trade.
- Relationships and feuds.

---

## **7. Legal System**
- NPCs accuse, testify, judge.
- Crimes generate bounties.
- Jails, work camps, executions.
- Corruption possible.

---

## **8. Survival Systems**
- Weather (deterministic optional).
- Temperature.
- Water sources.
- Fire and warmth.
- Food spoilage.

---

## **9. Combat**
### **9.1 Melee**
- Based on ASDF.
- Target specific body parts.
- Parry, block, grapple.

### **9.2 Ranged**
- Aim mode.
- Arrow physics simplified but consistent.

### **9.3 Injuries**
- Cuts, fractures, bleeding, infection.
- Treatment influences recovery.

---

## **10. Items & Crafting**
- Recursive material system: objects composed of components.
- Medieval tech level: 1066 baseline.
- Tools matter.

---

## **11. Performance Goals (Skiply Hardware)**
- 1080p @ 60fps target.
- Simulation budget: under 4ms/frame.
- ECS-heavy architecture.
- Lazy evaluation on distant regions.

---

# **Appendix A — Yinjun Game Engine Specifications**

## **A.1 Overview**
Yinjun is a modular, data-driven systemic engine supporting Blayd, Chyp, and Laysr.

Key traits:
- Extensible ECS.
- Unified simulation core.
- Part-based injury system.
- Procedural generation pipeline.
- Numerically stable long-run simulation.

---

## **A.2 Architecture**
### **A.2.1 ECS Core**
- Sparse-set optimized.
- Hot-path systems: physics-lite movement, combat resolution, per-part injury.
- Scheduled systems with priority queues.

### **A.2.2 Memory Model**
- Cache-linear component arrays.
- Chunk-based map storage.

---

## **A.3 Simulation Modules**
### **A.3.1 Injury Module**
- Per-part descriptors.
- Wound types: laceration, puncture, crush.
- Fluid dynamics simplified for bleeding.

### **A.3.2 Faction Module**
- Goal-selection trees.
- Diplomacy tables.

### **A.3.3 Worldgen Module**
- Biome maps.
- Settlement generation.
- Cultural generation.

### **A.3.4 Deterministic Weather Module**
- Optional: seed(date) → weather.

---

## **A.4 Extensibility**
- Content defined in JSON/TOML.
- Hot-reload for development.

---

# **Appendix B — Core Design Notes**

## **B.1 Simulation Philosophy**
- Prefer emergent systems over scripted outcomes.
- Player action should alter long-term world state.

## **B.2 Performance Philosophy**
- Defer simulation for regions outside player’s influence.
- Use deterministic systems for weather and long-term economy.

## **B.3 UI Philosophy**
- Fullscreen, high-density UIs that remain readable.
- Clear discoverability.

---

**End of Draft 0.1**

