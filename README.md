# RPG Game

A Python text-based RPG prototype focused on building a modular and expandable combat system.

This project is currently in early development. The main goal is to experiment with RPG mechanics such as party-based combat, body-part targeting, character attributes, MP-based skills, pain management, enemy intent, inventory rewards, and clean separation between game behavior and calculation logic.

## Overview

RPG Game is a console-based RPG combat prototype written in Python.

The project focuses on creating a maintainable RPG architecture where:

* Game behavior and flow are handled by gameplay modules.
* Mathematical formulas are separated into calculator modules.
* Characters and enemies are created from data-driven factories.
* Combat, encounter, inventory, leveling, and attribute systems can be expanded step by step.

## Current Features

* Text-based combat system
* Party-based battle structure
* Enemy body-part targeting
* HP and MP system
* Pain system with unconscious state
* Attribute system
* Level-up and attribute point allocation
* MP-based skill system
* Enemy intent system
* Analyze action for enemy information
* Instant death rules based on vital body parts
* Simplified guard system
* Encounter reward system
* Inventory test system
* Data-driven character and enemy creation
* Main test menu through `main.py`

## Combat System

The combat system is designed around party members fighting enemies with body parts.

Players can currently perform actions such as:

* Attack
* Skill
* Guard
* Analyze
* Run

Combat supports enemy intent, turn priority, dodge chance, body-part damage, HP damage, pain gain, unconscious state, and victory/defeat/escape outcomes.

## Guard System

The guard system has been simplified.

There is only one Guard action.

Guard behavior:

* If a character uses Guard and acts before the enemy, the guard becomes a perfect guard.
* If the enemy acts before the guarding character, the guard becomes a partial guard.
* If the enemy attacks another party member, the guard does not activate.

This makes the system easier to understand and works better with the current speed-based turn priority system.

## Attribute System

Characters have four main attributes:

| Attribute    | Effect                                               |
| ------------ | ---------------------------------------------------- |
| Strength     | Increases attack, defense, and pain resistance       |
| Endurance    | Increases max HP, status resistance, and max pain    |
| Agility      | Increases speed and dodge chance                     |
| Intelligence | Increases max MP and can later support skill scaling |

When a character levels up, they gain attribute points. These points can be spent to upgrade attributes.

## Pain System

Pain increases when a character takes damage.

Pain affects combat performance through different pain stages. At high pain, a character can become unconscious and temporarily lose the ability to act.

The pain system is separated from the main character class so it can be expanded later.

## Skill System

Skills are based on MP.

Current skill support includes:

* MP cost
* Attack skills
* Damage multipliers
* Attribute scaling
* Optional body-part targeting
* Accuracy checks

The system is designed so new skills can be added through data instead of hardcoding every skill directly into combat logic.

## Body-Part Combat

Enemies can have multiple body parts, such as head, body, arms, and legs.

Attacking body parts can:

* Damage the selected part
* Deal HP damage to the enemy
* Disable that body part
* Trigger instant death if the disabled part is vital

For example, some enemies can be defeated instantly if a vital body part is destroyed.

## Analyze System

Analyze reveals useful enemy information, such as:

* Vital body parts
* Weak points
* Important enemy traits

This gives the player a reason to gather information instead of knowing everything about the enemy immediately.

## Encounter System

The encounter system wraps combat and handles post-combat results.

It can process:

* Victory
* Escape
* Defeat
* EXP rewards
* Gold rewards
* Loot rewards
* Party state after combat

This separates raw combat results from reward calculation and player progression.

## Inventory System

The inventory system is currently testable through `main.py`.

It supports basic item operations such as:

* Adding items
* Removing items
* Checking whether an item exists
* Showing inventory contents
* Calculating total inventory value

## Project Architecture

The project is being refactored to separate behavior from calculations.

### Combat Modules

```text
combat.py
```

Handles combat behavior and flow, such as:

* Resolving player and party actions
* Resolving enemy attacks
* Applying damage
* Applying pain
* Returning combat logs
* Creating combat results

```text
combat_calculator.py
```

Handles combat calculations, such as:

* Damage calculation
* Dodge checks
* Turn priority
* Guard damage reduction
* Skill damage calculation
* Pain gain calculation

### Character Modules

```text
character.py
```

Handles character behavior and state, such as:

* Gaining EXP
* Leveling up
* Upgrading attributes
* Spending MP
* Restoring MP
* Learning skills
* Delegating pain behavior

```text
character_calculator.py
```

Handles character calculations, such as:

* Attack from Strength
* Defense from Strength
* HP from Endurance
* MP from Intelligence
* Speed from Agility
* Dodge chance
* Status resistance
* Pain resistance
* EXP requirement scaling

## Example Project Structure

```text
RPG-game/
│
├── main.py
├── README.md
│
├── data/
│   ├── character_presets.json
│   ├── pain_profiles.json
│   ├── enemies.json
│   └── skills.json
│
├── game/
│   ├── combat/
│   │   ├── combat.py
│   │   ├── combat_calculator.py
│   │   ├── combat_session.py
│   │   └── encounter.py
│   │
│   ├── characters/
│   │   ├── character.py
│   │   ├── character_calculator.py
│   │   ├── character_factory.py
│   │   ├── party.py
│   │   ├── player.py
│   │   ├── pain_system.py
│   │   └── attribute_menu.py
│   │
│   ├── enemies/
│   │   ├── enemy.py
│   │   └── enemy_factory.py
│   │
│   ├── skills/
│   │   └── skill_manager.py
│   │
│   └── core/
│       └── actor.py
│
└── saves/
```

The exact structure may change as the project grows.

## Requirements

* Python 3.10 or newer

The current version is a console-based Python prototype.

## How to Run

Clone the project:

```bash
git clone <repository-url>
```

Go into the project folder:

```bash
cd RPG-game
```

Run the main test menu:

```bash
python main.py
```

If your system uses `python3`, run:

```bash
python3 main.py
```

## Testing Through `main.py`

The project is currently tested through a console menu inside `main.py`.

When running:

```bash
python main.py
```

The program shows a test menu:

```text
Choose test mode:
1. Test combat only
2. Test encounter system
3. Test both
4. Test inventory only
5. Test attribute points only
```

### Test Modes

| Option | Test Mode                  | Purpose                                                         |
| ------ | -------------------------- | --------------------------------------------------------------- |
| 1      | Test combat only           | Starts a direct combat test between the party and an enemy      |
| 2      | Test encounter system      | Tests combat with encounter rewards such as EXP, gold, and loot |
| 3      | Test both                  | Runs both combat-only and encounter tests                       |
| 4      | Test inventory only        | Tests adding, removing, showing, and checking inventory items   |
| 5      | Test attribute points only | Tests level-up and attribute upgrade behavior                   |

## Main Test Details

### 1. Test Combat Only

This mode creates a player party and an enemy, then starts combat directly.

It is useful for checking:

* Turn order
* Attack behavior
* Skill behavior
* Guard behavior
* Enemy intent
* Pain gain
* Unconscious state
* Victory and defeat conditions

### 2. Test Encounter System

This mode tests the full encounter flow.

It is useful for checking:

* Combat result processing
* EXP rewards
* Gold rewards
* Loot rewards
* Player inventory after combat
* Party state after combat
* Attribute upgrade phase after encounter

### 3. Test Both

This mode runs both:

* Combat-only test
* Encounter system test

It is useful when checking whether combat changes also work correctly inside the encounter system.

### 4. Test Inventory Only

This mode tests the inventory system without combat.

It is useful for checking:

* Adding items
* Removing items
* Showing inventory
* Checking item existence
* Calculating total inventory value

### 5. Test Attribute Points Only

This mode tests character progression and attribute upgrades.

It is useful for checking:

* Level-up behavior
* Attribute point gain
* Strength upgrade
* Endurance upgrade
* Agility upgrade
* Derived stat refresh
* HP, MP, dodge, resistance, and pain limit changes

## Development Status

This project is still a prototype.

Current focus:

* Cleaning combat architecture
* Separating calculations from behavior
* Improving party-based combat
* Expanding the skill system
* Making enemies and characters more data-driven
* Testing core systems through `main.py`

## Planned Improvements

Possible future improvements:

* Better party management
* More enemy types
* More character presets
* More skill types
* Status effects
* Inventory expansion
* Equipment system
* Save/load system
* Exploration system
* Dialogue system
* Graphical UI in the future

## Git Workflow

Common commands for updating the repository:

```bash
git add .
git commit -m "Update RPG game system"
git push
```

## Notes

This project is mainly for learning game architecture and RPG system design.

The codebase is being improved step by step, with a focus on making each system easier to maintain, test, and expand.
