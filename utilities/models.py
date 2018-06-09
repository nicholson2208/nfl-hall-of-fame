class Player:
    def __init__(self, name, website, positions, starting, ending, hall_of_fame):
        self.name = name
        self.website = website
        self.id = None
        self.hall_of_famer = hall_of_fame
        self.starting_year = starting
        self.ending_year = ending
        self.positions = positions
        self.passing = None
        self.rushing = None
        self.receiving = None
        self.checked_pro_accolades = [False]*(int(self.ending_year) -  int(self.starting_year))

    def __str__(self) -> str:
        s = "{0} is {1}".format(self.name, "a Hall of Famer" if self.hall_of_famer else "is a scrub")
        return s


class PlayerYear:
    def __init__(self, name, age, hall_of_fame, all_pro, pro_bowl, games_played, games_started):
        self.name = name
        self.age = age
        self.hof = hall_of_fame
        self.all_pro = all_pro
        self.pro_bowl = pro_bowl
        self.games = games_played
        self.gs = games_started

        self.career_length = None

        self.career_all_pro = None
        self.career_pro_bowl = None
        self.career_games = None
        self.career_gs = None

        self.remaining_all_pro = None
        self.remaining_pro_bowl = None
        self.remaining_games = None
        self.remaining_gs = None
