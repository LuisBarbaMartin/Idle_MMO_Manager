# Idle MMO Manager Project Notes

## Current Architecture

- `app.py` is the Flask web backend and current app entrypoint.
- Docker runs the app with `python app.py` on port `5000`.
- GUI pages:
  - `/` dashboard
  - `/quests` quest screen
- Shared frontend logic lives in `static/app.js`.
- Shared styling lives in `static/style.css`.
- Flask templates:
  - `templates/base.html`
  - `templates/index.html`
  - `templates/quests.html`

## API Endpoints

- `GET /api/state`
  - Returns current guild state, members, available quests, active quests, inventory, and event log.
- `POST /api/start-quest`
  - Body: `{ "quest_key": "...", "character_key": "..." }`
  - Starts a quest for the selected guild member.
- `POST /api/load-test-file`
  - Reloads the test state from `data/test-file.JSON`.

## Data Files

- `data/characters.JSON`
  - Character templates/data.
- `data/items.JSON`
  - Item templates only.
  - These are not owned inventory items.
- `data/quests.JSON`
  - Quest definitions.
  - Uses `time_to_complete_seconds`.
- `data/test-file.JSON`
  - Test guild state used by the dashboard Load Test File button.
  - Defines guild name, gold, members, owned inventory instances, and equipped item instances.

## Item Model

- `items.JSON` contains item templates.
- Guild inventory contains owned item instances.
- Owned items have:
  - `instance_id`: unique ID for that owned copy.
  - `template_id`: ID of the item template it was created from.
- This is important because two copies of the same template item, like two Ghost Items, need separate identities.
- Quest rewards use `functions.create_owned_item(...)` so each reward becomes a fresh owned instance.
- Equipment should use `instance_id`, not `template_id`.

## Guild State

- `Guild` has:
  - `name`
  - `members`
  - `inventory`
  - `active_quests`
- The app starts with an empty guild:
  - `No Guild Loaded`
  - no members
  - no inventory
  - 0 gold
- Pressing Load Test File calls `/api/load-test-file` and loads `data/test-file.JSON`.
- The UI should only show characters in `guild.members`, not every character in `characters.JSON`.

## Quest System

- Active quests live in `guild.active_quests`.
- A character cannot start a second quest while already on one.
- `event_runner.character_has_active_quest(guild, character)` enforces this.
- Quest progress is based on timestamps:
  - `started_at`
  - `ends_at`
  - check `due_at` times
- The GUI updates quest progress by polling `/api/state`.
- `update_guild_quests(...)` applies completed quest rewards and removes completed quests from `guild.active_quests`.

## Frontend Data Hooks

The current `static/app.js` expects these element IDs when present:

- `#guild-name`
- `#guild-gold`
- `#character-list`
- `#character-select`
- `#quest-list`
- `#active-quest-list`
- `#inventory-list`
- `#event-log`
- `#load-test-file-button`

Render functions safely return if a panel is not on the current page.

## Current GUI Behavior

- Dashboard shows:
  - members
  - inventory
  - active quests
  - event log
  - Load Test File button
- Quest page shows:
  - available quests
  - assign-character dropdown
  - members
  - active quests
  - event log
- Busy characters are removed from the assignment dropdown.
- Busy characters show `Questing` in the member display.

## Known Test/Development Behavior

- `data/test-file.JSON` is the current test-state source.
- App state is in memory only.
- Refreshing/restarting the Docker app resets in-memory state.
- There is not yet a persistent save system.
- Docker may need restart after backend changes:
  - `docker compose restart idle-rpg`
- Full rebuild if dependencies change:
  - `docker compose up --build`

## Next Priorities

1. Inventory/equipment page
   - Show owned item instances.
   - Equip by `instance_id`.
   - Add backend endpoint like `POST /api/equip-item`.

2. Recruitment page
   - Add `/recruitment`.
   - Add recruit pool data file.
   - Add backend endpoint like `POST /api/recruit-character`.
   - Add recruited character to `guild.members`.

3. Rotating quest availability
   - Add availability metadata to `quests.JSON`.
   - Return only currently available quests from `/api/state`.
   - Consider cooldowns, rotation groups, rarity, level requirements, and refresh timers.

4. Save/load system
   - Persist guild state, members, inventory instances, equipment, active quests, gold, and XP.
   - Save active quest timestamps so offline progress can resolve correctly.

5. Cleanup/refactor
   - Consider moving app state setup out of `app.py`.
   - Consider an `OwnedItem` class later if item instances gain durability, enchantments, upgrades, or rolled stats.
   - Remove or repurpose old terminal-only functions once GUI flow is mature.
