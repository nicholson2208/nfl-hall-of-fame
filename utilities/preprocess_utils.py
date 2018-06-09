import csv

from utilities.models import PlayerYear


def read_scraped_player_years_from_csv(path="../data/year_player_data1985-2005.csv"):
    with open(path, "r") as infile:
        csv_reader = csv.reader(infile)
        header = next(csv_reader)  # do we need to do anything with this?
        player_years = []
        for line in csv_reader:
            name = line[38]
            age = line[1]
            hof = line[0]
            all_pro = line[2]
            pro_bowl = line[60]
            games_played = line[30]
            games_started = line[31]

            player_year = PlayerYear(name, age, hof, all_pro, pro_bowl, games_played, games_started)
            player_years.append(player_year)

        return player_years


def preprocess_player_years(player_years):
    assign_career_lengths(player_years)
    update_career_stats(player_years)
    update_remaining_stats(player_years)


def assign_career_lengths(player_years):
    curr_player = "start"
    career_length = 0
    player_careers = {}
    for pyear in player_years:
        if curr_player != pyear.name:
            player_careers.update({curr_player: career_length})
            curr_player = pyear.name
            career_length = 0
        career_length += 1
    for pyear in player_years:
        pyear.career_length = player_careers[pyear.name]


def update_career_stats(player_years):
    return None


def update_remaining_stats(player_years):
    return None


if __name__ == "__main__":
    pyears = read_scraped_player_years_from_csv()
    preprocess_player_years(pyears)