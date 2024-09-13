import json

rewards = {
    "hydrate": {
        "price": 10,
        "description": "We all stop to take a drink."
    },
    "tierlist": {
        "price": 1000,
        "description": "I make a tier list. Category is up to you!"
    }
}


def is_valid_reward(reward_name):
    return reward_name in rewards


def rewards_to_string():
    # Convert the rewards dictionary to a JSON string
    json_string = json.dumps(rewards)
    # print(json_string)

    # Return the JSON string as it is
    return json_string

