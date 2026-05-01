import copy
import time

import functions

# def run_stat_check(character_stats, check):
    #gets character stats
# def resolve_quest(character_stats, quest_data):
# def start_event(character_stats, quest_data):
# def tick_event(event_state, seconds=1):
# def event_runner(character_stats, quest_data, tick_size=1):
# def apply_quest_rewards(event_result, character, guild, items):
# def print_event_result(event_result):

def run_stat_check(character_stats, check):
    stat_name = check["stat"]
    required_value = check["difficulty"]
    character_value = character_stats.get(stat_name, 0)
    passed = character_value >= required_value

    return {
        "description": check["description"],
        "stat": stat_name,
        "character_value": character_value,
        "required_value": required_value,
        "passed": passed,
        "success_text": check.get("success_text", ""),
        "failure_text": check.get("failure_text", "")
    }


def resolve_quest(character_stats, quest_data):
    results = []

    for check in quest_data.get("checks", []):
        results.append(run_stat_check(character_stats, check))

    return build_event_result(character_stats, quest_data, results)


def build_event_result(character_stats, quest_data, results):
    success = all(result["passed"] for result in results)
    rewards = quest_data.get("rewards", {}) if success else {}

    return {
        "quest_name": quest_data["name"],
        "character_name": character_stats["name"],
        "time_to_complete_seconds": quest_data.get("time_to_complete_seconds", 0),
        "time_elapsed_seconds": quest_data.get("time_to_complete_seconds", 0),
        "complete": True,
        "success": success,
        "results": results,
        "rewards": rewards,
        "checks_printed_realtime": False
    }


def start_event(character_stats, quest_data):
    return {
        "quest_name": quest_data["name"],
        "character_name": character_stats["name"],
        "character_stats": character_stats,
        "quest_data": quest_data,
        "time_to_complete_seconds": quest_data.get("time_to_complete_seconds", 0),
        "time_elapsed_seconds": 0,
        "complete": False,
        "result": None
    }


def tick_event(event_state, seconds=1):
    if event_state["complete"]:
        return event_state

    event_state["time_elapsed_seconds"] += seconds

    if event_state["time_elapsed_seconds"] >= event_state["time_to_complete_seconds"]:
        event_state["time_elapsed_seconds"] = event_state["time_to_complete_seconds"]
        event_state["complete"] = True
        event_state["result"] = resolve_quest(
            event_state["character_stats"],
            event_state["quest_data"]
        )

    return event_state


def event_runner(character_stats, quest_data, tick_size=1):
    event_state = start_event(character_stats, quest_data)
    timeline = []

    while not event_state["complete"]:
        tick_event(event_state, tick_size)
        timeline.append({
            "time_elapsed_seconds": event_state["time_elapsed_seconds"],
            "time_to_complete_seconds": event_state["time_to_complete_seconds"],
            "complete": event_state["complete"]
        })

    event_result = event_state["result"]
    event_result["timeline"] = timeline
    return event_result


def event_runner_realtime(character_stats, quest_data, tick_size=1):
    event_state = start_event(character_stats, quest_data)
    timeline = []
    check_results = []
    checks = quest_data.get("checks", [])
    check_interval = event_state["time_to_complete_seconds"] / (len(checks) + 1)
    next_check_index = 0

    while not event_state["complete"]:
        time.sleep(tick_size)
        tick_event(event_state, tick_size)
        timeline.append({
            "time_elapsed_seconds": event_state["time_elapsed_seconds"],
            "time_to_complete_seconds": event_state["time_to_complete_seconds"],
            "complete": event_state["complete"]
        })

        print(
            f"Quest progress: {event_state['time_elapsed_seconds']} / "
            f"{event_state['time_to_complete_seconds']} seconds"
        )

        while (
            next_check_index < len(checks)
            and event_state["time_elapsed_seconds"] >= check_interval * (next_check_index + 1)
        ):
            check_result = run_stat_check(character_stats, checks[next_check_index])
            check_results.append(check_result)
            print_check_result(check_result)
            next_check_index += 1

    event_result = build_event_result(character_stats, quest_data, check_results)
    event_result["checks_printed_realtime"] = True
    event_result["timeline"] = timeline
    return event_result


def get_check_schedule(quest_data, started_at):
    checks = quest_data.get("checks", [])
    time_to_complete = quest_data.get("time_to_complete_seconds", 0)
    check_interval = time_to_complete / (len(checks) + 1) if checks else 0

    return [
        {
            "due_at": started_at + (check_interval * (index + 1)),
            "check": check,
            "complete": False,
            "result": None
        }
        for index, check in enumerate(checks)
    ]


def start_active_quest(character_stats, quest_data, started_at=None):
    started_at = time.time() if started_at is None else started_at
    time_to_complete = quest_data.get("time_to_complete_seconds", 0)

    return {
        "quest_name": quest_data["name"],
        "character_name": character_stats["name"],
        "character_stats": character_stats,
        "quest_data": quest_data,
        "started_at": started_at,
        "ends_at": started_at + time_to_complete,
        "time_to_complete_seconds": time_to_complete,
        "complete": False,
        "check_schedule": get_check_schedule(quest_data, started_at),
        "result": None
    }


def update_active_quest(active_quest, current_time=None):
    current_time = time.time() if current_time is None else current_time

    if active_quest["complete"]:
        return []

    new_check_results = []

    for scheduled_check in active_quest["check_schedule"]:
        if scheduled_check["complete"]:
            continue

        if current_time >= scheduled_check["due_at"]:
            check_result = run_stat_check(
                active_quest["character_stats"],
                scheduled_check["check"]
            )
            scheduled_check["complete"] = True
            scheduled_check["result"] = check_result
            new_check_results.append(check_result)

    if current_time >= active_quest["ends_at"]:
        active_quest["complete"] = True
        active_quest["result"] = build_event_result(
            active_quest["character_stats"],
            active_quest["quest_data"],
            [
                scheduled_check["result"]
                for scheduled_check in active_quest["check_schedule"]
                if scheduled_check["result"] is not None
            ]
        )
        active_quest["result"]["time_elapsed_seconds"] = active_quest["time_to_complete_seconds"]
        active_quest["result"]["checks_printed_realtime"] = True

    return new_check_results

def character_has_active_quest(guild, character):
    for active_quest in guild.active_quests:
        if active_quest["character"] is character:
            return True

    return False


def get_active_quest_progress(active_quest, current_time=None):
    current_time = time.time() if current_time is None else current_time
    elapsed = current_time - active_quest["started_at"]
    elapsed = max(0, min(elapsed, active_quest["time_to_complete_seconds"]))

    return {
        "time_elapsed_seconds": elapsed,
        "time_to_complete_seconds": active_quest["time_to_complete_seconds"],
        "complete": active_quest["complete"]
    }


def start_guild_quest(guild, character, quest_data, started_at=None):
    if character_has_active_quest(guild, character):
        print(f"{character.name} is already on a quest.")
        return None

    active_quest = start_active_quest(
        character.get_stats(),
        quest_data,
        started_at=started_at
    )
    active_quest["character"] = character
    guild.active_quests.append(active_quest)
    return active_quest



def update_guild_quests(guild, items, current_time=None, print_updates=True):
    completed_quests = []

    for active_quest in guild.active_quests[:]:
        new_check_results = update_active_quest(active_quest, current_time)
        progress = get_active_quest_progress(active_quest, current_time)

        if print_updates:
            print(
                f"{active_quest['character_name']} - {active_quest['quest_name']}: "
                f"{int(progress['time_elapsed_seconds'])} / "
                f"{progress['time_to_complete_seconds']} seconds"
            )

            for check_result in new_check_results:
                print_check_result(check_result)

        if active_quest["complete"]:
            quest_result = active_quest["result"]
            character = active_quest["character"]

            if print_updates:
                print_event_result(quest_result)

            apply_quest_rewards(quest_result, character, guild, items)
            guild.active_quests.remove(active_quest)
            completed_quests.append(active_quest)

    return completed_quests


def run_active_quest(character, quest_data, guild, items, tick_size=1):
    active_quest = start_guild_quest(guild, character, quest_data)

    while active_quest in guild.active_quests:
        time.sleep(tick_size)
        update_guild_quests(guild, items)

    return active_quest["result"]


def apply_quest_rewards(event_result, character, guild, items):
    if not event_result["success"]:
        return

    rewards = event_result["rewards"]

    guild.inventory["gold"] += rewards.get("gold", 0)
    character.experience += rewards.get("experience", 0)

    for item_key in rewards.get("items", []):
        guild.inventory["items"].append(functions.create_owned_item(item_key, items))


def print_event_result(event_result):
    print(f"{event_result['character_name']} attempts: {event_result['quest_name']}")
    print(
        f"Time elapsed: {event_result['time_elapsed_seconds']} / "
        f"{event_result['time_to_complete_seconds']} seconds"
    )

    if not event_result.get("checks_printed_realtime", False):
        for result in event_result["results"]:
            print_check_result(result)

    if event_result["success"]:
        print("Quest complete.")
        print(f"Rewards: {event_result['rewards']}")
    else:
        print("Quest failed.")


def print_check_result(result):
    print(result["description"])
    print(f"  {result['stat']}: {result['character_value']} / {result['required_value']}")

    if result["passed"]:
        print(f"  Success: {result['success_text']}")
    else:
        print(f"  Failure: {result['failure_text']}")
