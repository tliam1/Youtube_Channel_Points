import json

rewards = {
    "hydrate": {
        "price": 10,
        "description": "We all stop to take a drink."
    },
    "tierlist": {
        "price": 1000,
        "description": "I make a tier list. Category is up to you!"
    },
    "say": {
        "price": 200,
        "description": "TTS message based on what is written after \"say\" in the redeem msg."
    }
}

reward_callables = {
    "say": {
        "callable": lambda message: call_TTS(message)
    }
}


def call_TTS(msg):
    pass


def handle_reward(reward_name, *args):
    if is_valid_reward(reward_name):
        if reward_name in reward_callables and 'callable' in reward_callables[reward_name]:
            reward_callables[reward_name]['callable'](*args)
        else:
            print(f"Reward '{reward_name}' does not have a callable action.")
    else:
        print(f"Invalid reward: {reward_name}")


def is_valid_reward(reward_name):
    return reward_name in rewards


def rewards_to_string():
    # Convert the rewards dictionary to a JSON string
    json_string = json.dumps(rewards)
    # print(json_string)

    # Return the JSON string as it is
    return json_string
