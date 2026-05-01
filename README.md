# Idle MMO Manager

An idle RPG game manager built with Flask (Python backend) and vanilla JavaScript (frontend).

## Classes

### Character Class
```python
charactername = classes.character(
    name="Test_Char",
    base_strength=12,
    base_intelligence=3,
    base_agility=6,
    base_wisdom=4,
    char_ID=0001,
    level=1
)
```

Must enter in this order: (name, base_strength, base_intelligence, base_agility, base_wisdom)

### Equipment Class
```python
equipment_name = classes.Equipment(
    name="Iron Sword",
    slot="weapon1",
    rarity="common",
    item_ID=0001,
    hands=1,
    strength_bonus=4
)
```

### Guild Class
```python
guild_name = Guild(
    name="guild name",
    members=[],
    inventory=[]
)
```

## Codebase Architecture

This document outlines the structure of the codebase, showing dependencies and data flow between components.

### High-Level Architecture

```
Frontend (Browser)
├── HTML Templates (Jinja2)
├── JavaScript (app.js)
└── CSS (style.css)

Backend (Flask/Python)
├── app.py (Main app, routes, API)
├── functions.py (Data loading, utilities)
├── classes.py (Data models)
├── event_runner.py (Event processing)
└── data/ (JSON data files)
```

### Component Dependencies

#### Backend Dependencies

```
app.py
├── functions.py (load_characters, load_items, load_quests, load_guild_state)
├── classes.py (Guild, Character, Equipment, Quest, Item)
└── event_runner.py (for quest/event processing)

functions.py
├── classes.py (all classes for object creation)
└── data/*.JSON (raw data loading)

classes.py
└── (independent, defines data structures)

event_runner.py
├── classes.py (Guild, Character, Quest)
└── functions.py (utility functions)
```

#### Frontend Dependencies

```
app.js
└── Flask API (/api/state, /api/start-quest, /api/load-test-file, /api/equip-item)

Templates (base.html, index.html, quests.html, inventory.html)
├── base.html (shared layout)
└── static/style.css (styling)

style.css
└── (independent, styles all templates and JS-generated content)
```

### Data Flow

#### Application Startup
1. `app.py` starts Flask server
2. Loads data via `functions.py` on first request or API call
3. Serves static files (app.js, style.css) and templates

#### Page Load (e.g., Dashboard)
1. Browser requests `/` → Flask renders `index.html` (extends `base.html`)
2. `index.html` loads `app.js` and `style.css`
3. `app.js` calls `loadState()` → fetches `/api/state`
4. `app.py` handles `/api/state` → calls `functions.load_*()` → returns JSON
5. `app.js` renders UI components (characters, inventory, quests, log)

#### User Actions
- **Load Test File**: `app.js` → POST `/api/load-test-file` → `app.py` → `functions.load_guild_state('data/test-file.JSON')` → reloads global data
- **Start Quest**: `app.js` → POST `/api/start-quest` → `app.py` → updates guild state → returns updated state
- **Equip Item**: `app.js` → POST `/api/equip-item` → `app.py` → updates character equipment → returns updated state

### Key Data Structures

#### Global State (in app.py)
- `characters`: Dict of Character objects (loaded from data/characters.JSON)
- `items`: Dict of Item templates (loaded from data/items.JSON)
- `quests`: Dict of Quest objects (loaded from data/quests.JSON)
- `guild`: Guild object (loaded from data/test-file.JSON or created)

#### API Response (/api/state)
```json
{
  "guild": { "name": "...", "gold": 0 },
  "characters": [ { "key": "...", "name": "...", ... } ],
  "inventory": { "items": [ ... ] },
  "availableQuests": [ ... ],
  "activeQuests": [ ... ],
  "eventLog": [ ... ]
}
```

#### Serialization Flow
- `app.py` defines `serialize_*()` functions (serialize_item, serialize_character, serialize_quest, serialize_active_quest)
- `character.get_stats()` provides base character data
- `functions.py` handles data loading but not serialization
- `app.py` calls serialize functions to convert objects to JSON for API responses
- `app.js` receives serialized JSON and renders UI components

### File Purposes

- **app.py**: Web server, API endpoints, state management
- **classes.py**: Object-oriented models (Character, Item, Quest, Guild)
- **functions.py**: Data loading, serialization, utility functions
- **event_runner.py**: Background quest processing and events
- **app.js**: Frontend logic, API calls, DOM manipulation
- **style.css**: Visual styling for all components
- **templates/**: HTML structure with Jinja2 templating
- **data/**: Static JSON data for game content and test states

### Development Workflow

1. Modify data in `data/*.JSON`
2. Update models in `classes.py` if needed
3. Adjust loading logic in `functions.py`
4. Update API in `app.py`
5. Modify frontend rendering in `app.js`
6. Style changes in `style.css`
7. Template changes in `templates/*.html`