import copy


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


def event_runner(character_stats, quest_data):
    results = []

    for check in quest_data.get("checks", []):
        results.append(run_stat_check(character_stats, check))

    success = all(result["passed"] for result in results)
    rewards = quest_data.get("rewards", {}) if success else {}

    return {
        "quest_name": quest_data["name"],
        "character_name": character_stats["name"],
        "success": success,
        "results": results,
        "rewards": rewards
    }

def apply_quest_rewards(event_result, character, guild, items):
    if not event_result["success"]:
        return

    rewards = event_result["rewards"]

    guild.inventory["gold"] += rewards.get("gold", 0)
    character.experience += rewards.get("experience", 0)

    for item_key in rewards.get("items", []):
        guild.inventory["items"].append(copy.deepcopy(items[item_key]))


def print_event_result(event_result):
    print(f"{event_result['character_name']} attempts: {event_result['quest_name']}")

    for result in event_result["results"]:
        print(result["description"])
        print(f"  {result['stat']}: {result['character_value']} / {result['required_value']}")

        if result["passed"]:
            print(f"  Success: {result['success_text']}")
        else:
            print(f"  Failure: {result['failure_text']}")

    if event_result["success"]:
        print("Quest complete.")
        print(f"Rewards: {event_result['rewards']}")
    else:
        print("Quest failed.")
