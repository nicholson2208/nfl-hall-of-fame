import csv
import pandas as pd

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
            all_pro = int(float(line[2]))
            pro_bowl = int(float(line[60]))
            games_played = int(float(line[30]))
            games_started = int(float(line[31]))

            player_year = PlayerYear(name, age, hof, all_pro, pro_bowl, games_played, games_started)
            player_years.append(player_year)

        return player_years


def preprocess_player_years(player_years):
    #assign_career_lengths(player_years)
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
    curr_player = "start"
    career_stats = [0,0,0,0]
    player_careers = {}
    for pyear in player_years:
        if curr_player != pyear.name:
            player_careers.update({curr_player: career_stats})
            curr_player = pyear.name
            career_stats = [0,0,0,0]
        career_stats[0] += pyear.all_pro
        career_stats[1] += pyear.pro_bowl
        career_stats[2] += pyear.games
        career_stats[3] += pyear.gs

    # catch chris zorich
    player_careers.update({curr_player: career_stats})

    for pyear in player_years:
        pyear.career_all_pro = player_careers[pyear.name][0]
        pyear.career_pro_bowl = player_careers[pyear.name][1]
        pyear.career_games = player_careers[pyear.name][2]
        pyear.career_gs = player_careers[pyear.name][3]


def update_remaining_stats(player_years):
    curr_player = "start"
    player_rems = {}
    for pyear in player_years:
        if curr_player != pyear.name:
            curr_player = pyear.name
            rem_stats = [pyear.career_all_pro, pyear.career_pro_bowl, pyear.career_games, pyear.career_gs]

        rem_stats[0] -= pyear.all_pro
        rem_stats[1] -= pyear.pro_bowl
        rem_stats[2] -= pyear.games
        rem_stats[3] -= pyear.gs

        pyear.remaining_all_pro = rem_stats[0]
        pyear.remaining_pro_bowl = rem_stats[1]
        pyear.remaining_games = rem_stats[2]
        pyear.remaining_gs = rem_stats[3]

    return player_years


def make_final_table(player_years,path="../data/", file="year_player_data1985-2005.csv", target="remaining_games"):
    """
    a helper function for concating relevant target vars into the csv with data

    :param player_years:
    :param path:
    :param file:
    :param target:
    :return:
    """

    data_df = pd.read_csv(path+file)
    # worry about making sure that we don't have cheater features in Weka

    target_df = pd.DataFrame(columns=[target])
    for player_year in player_years:
        target_df = target_df.append({target: getattr(player_year, target)}, ignore_index=True)
        print(getattr(player_year, target))
    out_df = pd.concat([data_df,target_df], axis=1)
    out_df.to_csv(path + target + "_" + file, index=False)


if __name__ == "__main__":
    pyears = read_scraped_player_years_from_csv()
    preprocess_player_years(pyears)
    make_final_table(pyears, target="remaining_all_pro")
    make_final_table(pyears, target="remaining_pro_bowl")
    make_final_table(pyears, target="remaining_games")
    make_final_table(pyears, target="remaining_gs")
