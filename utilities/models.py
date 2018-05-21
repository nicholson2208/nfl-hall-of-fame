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
        self.checked_pro_accolades = [False, False, False, False]

    def __str__(self) -> str:
        s = "{0} is {1}".format(self.name, "a Hall of Famer" if self.hall_of_famer else "is a scrub")
        return s
