# RPG Game

A text-based RPG game prototype written in Python.
The project focuses on building a modular RPG combat system with party-based battles, body-part targeting, skills, attributes, pain mechanics, guard behavior, and a temporary Pygame UI for demonstration.

## Project Overview

This project is an RPG combat prototype designed for learning and experimentation.
The main goal is to separate game behavior from game calculations so the system is easier to expand later.

Current features include:

* Party-based combat
* Enemy body-part targeting
* Attribute system
* Level-up and attribute point upgrading
* HP, MP, pain, and unconscious mechanics
* Skill system based on MP
* Enemy intent system
* Analyze action to reveal enemy weak points and vital parts
* Instant death when vital body parts are destroyed
* Simplified guard system
* Temporary Pygame combat UI for demo

## Current Combat Design

The combat system is designed with separation of responsibility:

```text
combat.py
```

Handles combat behavior and flow, such as:

* Resolving player actions
* Resolving enemy attacks
* Applying damage
* Handling combat logs
* Handling victory, defeat, and escape results

```text
combat_calculator.py
```

Handles combat-related calculations, such as:

* Damage calculation
* Dodge check
* Turn priority
* Guard damage reduction
* Skill damage calculation
* Pain gain calculation

```text
character.py
```

Handles character behavior and state, such as:

* Gaining EXP
* Leveling up
* Upgrading attributes
* Spending and restoring MP
* Learning skills
* Delegating pain behavior to the pain system

```text
character_calculator.py
```

Handles character-related calculations, such as:

* Attack from Strength
* Defense from Strength
* HP from Endurance
* MP from Intelligence
* Speed and dodge from Agility
* Status resistance
* Pain resistance
* EXP requirement scaling

## Guard System

The old guard stance system has been replaced with a simpler guard system.

There is now only one Guard action.

Guard behavior:

* If the guarding character acts before the enemy and gets attacked, it becomes a perfect guard.
* If the enemy acts first and attacks the guarding character, it becomes a partial guard.
* If the enemy attacks another party member, the guard has no effect.

This makes guard easier to understand and better suited for the current turn-priority system.

## Temporary UI Demo

A temporary Pygame UI is included for demonstration.

The UI allows the player to:

* Select a party member
* Select an enemy body part
* Use Attack
* Use Guard
* Use Analyze
* Use Run
* View combat logs
* View party and enemy status

The UI is only a prototype and is mainly used to demonstrate the combat system visually.

## Requirements

* Python 3.10 or newer
* Pygame

Install dependencies:

```bash
pip install pygame
```

## How to Run

Run the demo combat UI:

```bash
python demo_combat_ui.py
```

If your system uses `python3`, run:

```bash
python3 demo_combat_ui.py
```

## Basic Gameplay Flow

1. Select a party member.
2. Select an enemy body part.
3. Choose an action:

   * Attack
   * Skill
   * Guard
   * Analyze
   * Run
4. Read the combat result in the log panel.
5. Repeat until the party wins, loses, or escapes.

## Project Structure

Example structure:

```text
RPG-game/
│
├── demo_combat_ui.py
│
├── game/
│   ├── combat/
│   │   ├── combat.py
│   │   ├── combat_calculator.py
│   │   └── combat_session.py
│   │
│   ├── characters/
│   │   ├── character.py
│   │   ├── character_calculator.py
│   │   ├── character_factory.py
│   │   └── pain_system.py
│   │
│   ├── enemies/
│   │   ├── enemy.py
│   │   └── enemy_factory.py
│   │
│   ├── skills/
│   │   └── skill_manager.py
│   │
│   ├── ui/
│   │   └── pygame_combat_ui.py
│   │
│   └── data/
│       ├── character_presets.json
│       ├── pain_profiles.json
│       ├── enemies.json
│       └── skills.json
│
└── README.md
```

## Main Systems

### Attribute System

Characters have four main attributes:

| Attribute    | Effect                                           |
| ------------ | ------------------------------------------------ |
| Strength     | Increases attack, defense, and pain resistance   |
| Endurance    | Increases HP, status resistance, and max pain    |
| Agility      | Increases speed and dodge chance                 |
| Intelligence | Increases MP and may later increase skill damage |

When a character levels up, they gain attribute points that can be used to improve these attributes.

### Pain System

Pain increases when a character takes damage.

Pain can reduce combat performance through pain stages.
At high pain, a character may become unconscious and temporarily unable to act.

### Skill System

Skills use MP.

Current skill support includes:

* MP cost
* Attack skills
* Damage multiplier
* Attribute scaling
* Optional body-part targeting
* Accuracy check

More skill types can be added later.

### Body-Part Combat

Enemies have body parts that can be targeted individually.

Attacking body parts can:

* Damage the part
* Deal HP damage to the enemy
* Disable the part
* Trigger instant death if the part is vital

For example, an enemy may be instantly defeated if its head is destroyed.

### Analyze System

Analyze reveals information about an enemy, such as:

* Vital parts
* Weak points
* Important combat hints

This replaces the old system where the player already knew enemy attacks in advance.

## Development Notes

This project is currently a prototype.
The current focus is on building clean combat architecture before expanding the game world.

Planned improvements:

* Better Pygame UI
* Skill selection UI
* Inventory system
* Equipment system
* More enemies
* More character presets
* Party management
* Status effects
* Save/load system
* Map or exploration system
* Dialogue system

## Git Usage

Common commands:

```bash
git add .
git commit -m "Update RPG combat system"
git push
```

## Repository

GitHub repository:

```text
https://github.com/AtomTNB2202/RPG-game
```

## Status

This project is still in early development.

Current goal:

```text
Build a playable RPG combat demo with clean and expandable architecture.
```
