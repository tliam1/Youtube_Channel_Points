class Pot:
    def __init__(self, random_number: int):
        self.pot_players = []  # List of dictionaries to store player data
        self.pot_value = 0.0
        self.pot_duration = 5 * 60  # minutes
        self.winning_number = random_number

    def add_player(self, player: str, guess_number: int, contribution: float):
        self.pot_players.append({
            'player': player,
            'guess': guess_number,
            'contribution': contribution
        })

    def add_value(self, val: float):
        self.pot_value += val

    def get_value(self) -> float:
        return self.pot_value

    def reset(self, random_number: int):
        self.pot_players.clear()
        self.pot_value = 0.0
        self.pot_duration = 5 * 60
        self.winning_number = random_number

    def payout(self):
        # total closeness to the winning number
        total_closeness = sum(1 / (abs(player['guess'] - self.winning_number) + 1) for player in self.pot_players)

        # total contribution
        total_contribution = sum(player['contribution'] for player in self.pot_players)

        payouts = {}

        for player in self.pot_players:
            # Closeness factor: higher if the guess is closer to the winning number
            closeness_factor = 1 / (abs(player['guess'] - self.winning_number) + 1)

            # Contribution factor: percentage of the total contribution
            contribution_factor = player['contribution'] / total_contribution if total_contribution > 0 else 0

            # Proportional payout: based on closeness and contribution
            payout_percentage = (closeness_factor / total_closeness) * 0.7 + (contribution_factor * 0.3)

            payout_amount = self.pot_value * payout_percentage

            payouts[player['player']] = payout_amount

        return payouts

    def decrease_pot_duration(self):
        self.pot_duration -= 1

    def get_players(self) -> list:
        return self.pot_players

    def get_duration(self) -> float:
        return self.pot_duration
