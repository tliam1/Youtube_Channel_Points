from profanity_check import predict, predict_prob


def check_string_for_swears(msg: [str]) -> bool:
    swear_odd = predict_prob(msg)
    if swear_odd[0] > 0.8:
        return False
    return True


