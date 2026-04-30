# main.py

import time
from main.functions import global_tick

#TODO - Tick Rate will need to be remade once the event_handler() is implemented. This is just a placeholder for testing purposes.
TICK_RATE = 1.0  # seconds per tick

player = {
    "gold": 0,
    "gold_per_tick": 1,
    "xp": 0,
    "xp_per_tick": 2,
    "quest_cooldown": 10,
}

def main():
    last_tick = time.time()

    while True:
        now = time.time()

        if now - last_tick >= TICK_RATE:
            ticks_to_process = int((now - last_tick) // TICK_RATE)

            for _ in range(ticks_to_process):
                global_tick(player)

            last_tick += ticks_to_process * TICK_RATE

            print(
                f"Gold: {player['gold']} | "
                f"XP: {player['xp']} | "
                f"Quest CD: {player['quest_cooldown']}"
            )

        time.sleep(0.05)


if __name__ == "__main__":
    main()
