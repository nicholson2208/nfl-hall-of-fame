class Player:
    def __init__(self, name, website, positions, starting, ending, hall_of_fame):
        self.name = name
        self.website = "https://www.pro-football-reference.com" + website
        self.id = None
        self.hall_of_famer = hall_of_fame
        self.starting_year = starting
        self.ending_year = ending
        self.positions = positions.split("-")
        self.passing = None
        self.rushing = None
        self.receiving = None



    def __str__(self) -> str:
        s = "{0} at {1}, {2}".format(self.name, self.latitude, self.longitude)
        return s