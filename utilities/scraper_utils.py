import requests
import time
import csv
import os
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup


from utilities.models import Player


def get_players():
    """
    A utility function to get a list of players and the links to their pages
    :return:
    """
    players = []

    for ii in range(ord('A'), ord('A')+26):
        url = "https://www.pro-football-reference.com/players/" + chr(ii)+"/"
        print(url)
        r = requests.get(url)
        time.sleep(.04)
        soup = BeautifulSoup(r.content, "lxml")
        player_div = soup.find_all("div", {"id": "div_players"})

        for player_anchor_tag in player_div[0].children:
            try:
                player_anchor_tag = str(player_anchor_tag)
                name = player_anchor_tag.split(".htm\">")[1].split("</a>")[0]
                # print(name)
                website = player_anchor_tag.split("href=\"")[1].split('"')[0]
                # print(website)
                position = player_anchor_tag.split("</a>")[1].split("(")[1].split(")")[0].split("-")
                # print(position)
                starting = player_anchor_tag[-13:-9]
                ending = player_anchor_tag[-8:-4]
                if "+" in player_anchor_tag:
                    hof = 1
                else:
                    hof = 0

                website = "https://www.pro-football-reference.com" + website
                players.append(Player(name, website, position, starting, ending, hof))

            except IndexError:
                print("Something weird with {0}".format(player_anchor_tag))

    print(len(players))

    write_playerlist_to_csv(players)
    print("hi")


def write_playerlist_to_csv(players, filename="../data/player_list.csv"):
    """
    Once we have scraped the initial list, store it as a csv
    :param players:
    :param filename:
    :return:
    """
    with open(filename, "w", newline='') as outfile:
        filewriter = csv.writer(outfile)
        filewriter.writerow(["Player Name", "Positions" "Link", "Starting Year", "Ending Year", "Hall of Fame"])

        for player in players:
            row = [player.name, player.positions, player.website, player.starting_year, player.ending_year, player.hall_of_famer]
            filewriter.writerow(row)


def read_playerlist_from_csv(starting_range=1985, ending_range=2005, path="../data/player_list.csv"):
    """

    :param starting_range:
    :param ending_range:
    :param path:
    :return:
    """
    if not os.path.exists(path):
        os.makedirs(path)

    with open(path, "r") as infile:
            csv_reader = csv.reader(infile)
            header = next(csv_reader)  # do we need to do anything with this?
            players = []
            for line in csv_reader:
                name = line[0]
                position = eval(line[1])
                website = line[2]
                start = int(line[3])
                end = int(line[4])
                hof = int(line[5])

                # TODO: check the weird thing with Rabih Abdullah
                if start >= starting_range and end <= ending_range:  # filter the player that we actually want
                    player = Player(name, website, position, start, end, hof)
                    players.append(player)
            print("There are {0} players that had" 
                  " their whole careers between {1} and {2}".format(len(players), starting_range, ending_range))

            return players


def scrape_players(starting_range=1985, ending_range=2005):
    """

    :return:
    """

    if os.path.exists("../data/player_list.csv"):
        players = read_playerlist_from_csv(starting_range=starting_range, ending_range=ending_range)
    else:
        get_players()
        players = read_playerlist_from_csv(starting_range=starting_range, ending_range=ending_range)

    all_player_data = pd.DataFrame()

    for player in players:
        df = scrape_player(player)
        df["name"] = player.name.replace("'","")
        df["HOF"] = player.hall_of_famer
        #df = df.drop(["pos_0", "pos_1", "pos_2", "pos_3"], axis=1, errors="ignore")

        all_player_data = pd.concat([all_player_data, df])

    write_player_data_to_csv(all_player_data, path="../data/year_player_data{0}-{1}.csv".format(starting_range, ending_range))


def scrape_player(player, years="ALL"):
    """
    a function that add the the players
    :param years:
    :param player:
    :return:
    """

    print(player.website)
    r = requests.get(player.website)
    time.sleep(.04)
    soup = BeautifulSoup(r.content, "lxml")

    df = pd.DataFrame()
    temp_df = pd.DataFrame()

    if years == "ALL":
        for year_num in range(player.ending_year - player.starting_year):
            temp_df = get_passing(player, years, soup, temp_df, individual_year=year_num)
            # print(df.shape)
            temp_df = get_rush_rec(player, years, soup, temp_df, individual_year=year_num)
            # print(df.shape)
            temp_df = get_returns(player, years, soup, temp_df, individual_year=year_num)
            #print(df.shape)
            temp_df = get_kick_punt(player, years, soup, temp_df, individual_year=year_num)
            #print(df.shape)
            temp_df = get_defense(player, years, soup, temp_df, individual_year=year_num)

            df = pd.concat([df, temp_df], axis=0)
    else:
        df = get_passing(player, years, soup, df)
        print(df.shape)
        df = get_rush_rec(player, years, soup, df)
        print(df.shape)
        df = get_returns(player, years, soup, df)
        print(df.shape)
        df = get_kick_punt(player, years, soup, df)
        print(df.shape)
        df = get_defense(player, years, soup, df)

    print(df.shape)

    return df


def get_passing(player, years, soup, df, individual_year=None):
    """
    Jayden
    :param years
    :param player:
    :param soup:
    :param df:
    :param individual_year
    :return:
    """
    passing_table_list = soup.find_all("div", {"id": "div_passing"})
    passing_table = None

    if not passing_table_list or len(passing_table_list) == 0:
        print("{0} had no passing stats".format(player.name))
    else: # there should only be one
        passing_table = passing_table_list[0]

    if passing_table:
        start_yr = player.starting_year

        passing_table = passing_table_list[0]

        if years == "ALL" or "all":
            year_num = individual_year
            this_year_stats = passing_table.find("tr", {"id": "passing." + str(start_yr + year_num)})

            if not this_year_stats:
                print("{0} has no passing stats in {1}".format(player.name, start_yr + year_num))
            else:
                for datum in this_year_stats.find_all("td"):
                    shorter = str(datum).split("data-stat")[1]
                    stat_name = shorter.split('"')[1]

                    try:
                        # get value of attribute
                        if stat_name == "team" and shorter.split(">")[1].split("<")[0] != "2TM":
                            data = shorter.split('title="')[1].split('"')[0]
                        elif stat_name == "qb_rec":
                            data = shorter.split('csk="')[1].split('"')[0]
                        else:
                            data = shorter.split(">")[1].split("<")[0]

                        # format value of attribute
                        if stat_name == "team" or stat_name == "pos":
                            data = data.upper()
                        else:
                            data = float(data)

                        df[stat_name] = [data]
                    except:
                        df[stat_name] = np.NaN

                # ProBowl/AllPro Info
                if not player.checked_pro_accolades[year_num]:
                    df = get_pro_accolades(this_year_stats, year_num, df, player, method="ALL")


        else:

            for year_num in range(years):
                this_year_stats = passing_table.find("tr", {"id": "passing." + str(start_yr + year_num)})

                if not this_year_stats:
                    print("{0} has no passing stats in {1}".format(player.name, start_yr + year_num))
                    continue

                for datum in this_year_stats.find_all("td"):
                    shorter = str(datum).split("data-stat")[1]
                    stat_name = shorter.split('"')[1]

                    try:
                        # get value of attribute
                        if stat_name == "team" and shorter.split(">")[1].split("<")[0] != "2TM":
                            data = shorter.split('title="')[1].split('"')[0]
                        elif stat_name == "qb_rec":
                            data = shorter.split('csk="')[1].split('"')[0]
                        else:
                            data = shorter.split(">")[1].split("<")[0]

                        # format value of attribute
                        if stat_name == "team" or stat_name == "pos":
                            data = data.upper()
                        else:
                            data = float(data)

                        df[stat_name + "_" + str(year_num)] = [data]
                    except:
                        df[stat_name + "_" + str(year_num)] = np.NaN

                # ProBowl/AllPro Info
                if not player.checked_pro_accolades[year_num]:
                    df = get_pro_accolades(this_year_stats, year_num, df, player)

    return df


def get_rush_rec(player, years, soup, df,  individual_year=None):
    """
    Matt
    :param player:
    :param soup:
    :param df:
    :return:
    """
    rush_rec_table_list = soup.find_all("div", {"id": "div_rushing_and_receiving"})
    rush_rec_table = None

    if rush_rec_table_list:
        rush_rec_table = rush_rec_table_list[0]

    if not rush_rec_table_list or len(rush_rec_table_list) == 0:
        # they might be a WR and have the same table but stored differently
        rush_rec_table_list = soup.find_all("div", {"id": "div_receiving_and_rushing"})
        if not rush_rec_table_list or len(rush_rec_table_list) == 0:  # either make a bunch of 0s or
            print("{0} had no rushing and receiving stats".format(player.name))
            return df
        else: # there should only be one
            rush_rec_table = rush_rec_table_list[0]

    if rush_rec_table:
        start_yr = player.starting_year

        if years == "ALL" or "all":
            year_num = individual_year
            this_year_stats = rush_rec_table.find("tr", {"id": "rushing_and_receiving." + str(start_yr + year_num)})

            if not this_year_stats:
                print("{0} has no rush or rec stats in {1}".format(player.name, start_yr + year_num))
            else:
                for datum in this_year_stats.find_all("td"):
                    shorter = str(datum).split("data-stat")[1]
                    stat_name = shorter.split('"')[1]

                    try:
                        if stat_name == "team" and shorter.split(">")[1].split("<")[0] != "2TM":
                            data = shorter.split('title="')[1].split('"')[0]
                        else:
                            data = shorter.split(">")[1].split("<")[0]

                        if stat_name == "team" or stat_name == "pos":
                            df[stat_name] = [data.upper()]
                        else:
                            if stat_name == "catch_pct":
                                data = data.split("%")[0]

                            df[stat_name] = [float(data)]
                    except:
                        df[stat_name] = np.NaN

                if not player.checked_pro_accolades[year_num]:
                    df = get_pro_accolades(this_year_stats, year_num, df, player, method="ALL")

        else:

            for year_num in range(4):
                this_year_stats = rush_rec_table.find("tr", {"id": "rushing_and_receiving." + str(start_yr + year_num)})

                if not this_year_stats:
                    print("{0} has no rush or rec stats in {1}".format(player.name,start_yr + year_num))
                    continue

                for datum in this_year_stats.find_all("td"):
                    shorter = str(datum).split("data-stat")[1]
                    stat_name = shorter.split('"')[1]

                    try:
                        if stat_name == "team" and shorter.split(">")[1].split("<")[0] != "2TM":
                            data = shorter.split('title="')[1].split('"')[0]
                        else:
                            data = shorter.split(">")[1].split("<")[0]

                        if stat_name == "team" or stat_name == "pos":
                            df[stat_name + "_" + str(year_num)] = [data.upper()]
                        else:
                            if stat_name == "catch_pct":
                                data = data.split("%")[0]

                            df[stat_name + "_" + str(year_num)] = [float(data)]
                    except:
                        df[stat_name + "_" + str(year_num)] = np.NaN

                if not player.checked_pro_accolades[year_num]:
                    df = get_pro_accolades(this_year_stats, year_num, df, player)

    return df


def get_returns(player, years, soup, df,  individual_year=None):
    """
    Matt
    :param player:
    :param soup:
    :param df:
    :return:
    """
    # TODO: av is PFR's metric to compare all players, so its not average and we might want to exclude it?

    returns_table_list = soup.find_all("div", {"id": "div_returns"})
    returns_table = None

    if returns_table_list:
        returns_table = returns_table_list[0]

    if not returns_table_list or len(returns_table_list) == 0:
        print("{0} had no return stats".format(player.name))
    else: # there should only be one
        returns_table = returns_table_list[0]

    if returns_table:
        start_yr = player.starting_year

        if years == "ALL" or years == "all":
            year_num = individual_year
            this_year_stats = returns_table.find("tr", {"id": "returns." + str(start_yr + year_num)})

            if not this_year_stats:
                print("{0} has no rush or rec stats in {1}".format(player.name, start_yr + year_num))
            else:

                for datum in this_year_stats.find_all("td"):
                    shorter = str(datum).split("data-stat")[1]
                    stat_name = shorter.split('"')[1]

                    try:
                        if stat_name == "team" and shorter.split(">")[1].split("<")[0] != "2TM":
                            data = shorter.split('title="')[1].split('"')[0]
                        else:
                            data = shorter.split(">")[1].split("<")[0]

                        if stat_name == "team" or stat_name == "pos":
                            df[stat_name] = [data.upper()]
                        else:
                            if stat_name == "catch_pct":
                                data = data.split("%")[0]

                            df[stat_name] = [float(data)]
                    except:
                        df[stat_name] = np.NaN

                if not player.checked_pro_accolades[year_num]:
                    df = get_pro_accolades(this_year_stats, year_num, df, player, method="ALL")

        else:

            for year_num in range(4):
                this_year_stats = returns_table.find("tr", {"id": "returns." + str(start_yr + year_num)})

                if not this_year_stats:
                    print("{0} has no rush or rec stats in {1}".format(player.name, start_yr + year_num))
                    continue

                for datum in this_year_stats.find_all("td"):
                    shorter = str(datum).split("data-stat")[1]
                    stat_name = shorter.split('"')[1]

                    try:
                        if stat_name == "team" and shorter.split(">")[1].split("<")[0] != "2TM":
                            data = shorter.split('title="')[1].split('"')[0]
                        else:
                            data = shorter.split(">")[1].split("<")[0]

                        if stat_name == "team" or stat_name == "pos":
                            df[stat_name + "_" + str(year_num)] = [data.upper()]
                        else:
                            if stat_name == "catch_pct":
                                data = data.split("%")[0]

                            df[stat_name + "_" + str(year_num)] = [float(data)]
                    except:
                        df[stat_name + "_" + str(year_num)] = np.NaN

                if not player.checked_pro_accolades[year_num]:
                    df = get_pro_accolades(this_year_stats, year_num, df, player)

    return df


def get_kick_punt(player, years, soup, df,  individual_year=None):
    """
    Jayden
    :param player:
    :param soup:
    :param df:
    :return:
    """
    kicking_table_list = soup.find_all("div", {"id": "div_kicking"})
    kicking_table = None

    if not kicking_table_list or len(kicking_table_list) == 0:
        print("{0} had no kicking and punting stats".format(player.name))
    else:  # there should only be one
        kicking_table = kicking_table_list[0]

    if kicking_table:
        start_yr = player.starting_year
        kicking_table = kicking_table_list[0]

        if years == "ALL" or years == "all":
            year_num = individual_year

            this_year_stats = kicking_table.find("tr", {"id": "kicking." + str(start_yr + year_num)})

            if not this_year_stats:
                print("{0} has no kicking and punting stats in {1}".format(player.name, start_yr + year_num))
            else:
                for datum in this_year_stats.find_all("td"):
                    shorter = str(datum).split("data-stat")[1]
                    stat_name = shorter.split('"')[1]

                    try:
                        # get value of attribute
                        if stat_name == "team" and shorter.split(">")[1].split("<")[0] != "2TM":
                            data = shorter.split('title="')[1].split('"')[0]
                        else:
                            data = shorter.split(">")[1].split("<")[0]

                        # format value of attribute
                        if stat_name == "team" or stat_name == "pos":
                            data = data.upper()
                        elif stat_name == "fg_per" or "xp_per":
                            data = float(data.split("%")[0])
                        else:
                            data = float(data)

                        df[stat_name] = [data]
                    except:
                        df[stat_name] = np.NaN

                    if not player.checked_pro_accolades[year_num]:
                        df = get_pro_accolades(this_year_stats, year_num, df, player, method="ALL")
        else:

            for year_num in range(4):
                this_year_stats = kicking_table.find("tr", {"id": "kicking." + str(start_yr + year_num)})

                if not this_year_stats:
                    print("{0} has no kicking and punting stats in {1}".format(player.name, start_yr + year_num))
                    continue

                for datum in this_year_stats.find_all("td"):
                    shorter = str(datum).split("data-stat")[1]
                    stat_name = shorter.split('"')[1]

                    try:
                        # get value of attribute
                        if stat_name == "team" and shorter.split(">")[1].split("<")[0] != "2TM":
                            data = shorter.split('title="')[1].split('"')[0]
                        else:
                            data = shorter.split(">")[1].split("<")[0]

                        # format value of attribute
                        if stat_name == "team" or stat_name == "pos":
                            data = data.upper()
                        elif stat_name == "fg_per" or "xp_per":
                            data = float(data.split("%")[0])
                        else:
                            data = float(data)

                        df[stat_name + "_" + str(year_num)] = [data]
                    except:
                        df[stat_name + "_" + str(year_num)] = np.NaN

                # ProBowl/AllPro Info
                if not player.checked_pro_accolades[year_num]:
                    df = get_pro_accolades(this_year_stats, year_num, df, player)

    return df


def get_defense(player, years, soup, df, individual_year=None):
    """
    Jayden
    :param player:
    :param soup:
    :param df:
    :return:
    """
    def_table_list = soup.find_all("div", {"id": "div_defense"})
    def_table = None

    if not def_table_list or len(def_table_list) == 0:
        print("{0} had no defense stats".format(player.name))
    else:  # there should only be one
        def_table = def_table_list[0]

    if def_table:
        start_yr = player.starting_year

        if years == "ALL" or years == "all":
            year_num = individual_year
            this_year_stats = def_table.find("tr", {"id": "defense." + str(start_yr + year_num)})

            if not this_year_stats:
                print("{0} has no defense stats in {1}".format(player.name, start_yr + year_num))

            else:
                for datum in this_year_stats.find_all("td"):
                    shorter = str(datum).split("data-stat")[1]
                    stat_name = shorter.split('"')[1]

                    try:
                        # get value of attribute
                        if stat_name == "team" and shorter.split(">")[1].split("<")[0] != "2TM":
                            data = shorter.split('title="')[1].split('"')[0]
                        else:
                            data = shorter.split(">")[1].split("<")[0]

                        # format value of attribute
                        if stat_name == "team" or stat_name == "pos":
                            data = data.upper()
                        else:
                            data = float(data)

                        df[stat_name] = [data]
                    except:
                        df[stat_name] = np.NaN

                    if not player.checked_pro_accolades[year_num]:
                        df = get_pro_accolades(this_year_stats, year_num, df, player, method="ALL")

        else:
            for year_num in range(4):
                this_year_stats = def_table.find("tr", {"id": "defense." + str(start_yr + year_num)})

                if not this_year_stats:
                    print("{0} has no defense stats in {1}".format(player.name, start_yr + year_num))
                    continue

                for datum in this_year_stats.find_all("td"):
                    shorter = str(datum).split("data-stat")[1]
                    stat_name = shorter.split('"')[1]

                    try:
                        # get value of attribute
                        if stat_name == "team" and shorter.split(">")[1].split("<")[0] != "2TM":
                            data = shorter.split('title="')[1].split('"')[0]
                        else:
                            data = shorter.split(">")[1].split("<")[0]

                        # format value of attribute
                        if stat_name == "team" or stat_name == "pos":
                            data = data.upper()
                        else:
                            data = float(data)

                        df[stat_name + "_" + str(year_num)] = [data]
                    except:
                        df[stat_name + "_" + str(year_num)] = np.NaN

                # ProBowl/AllPro Info
                if not player.checked_pro_accolades[year_num]:
                    df = get_pro_accolades(this_year_stats, year_num, df, player)

    return df


def get_pro_accolades(this_year_stats, year_num, df, player, method=None):
    year_label = this_year_stats.find("th")
    # data = str(year_label).split("</a>")[1].split("</th>")[0]
    #print(data)
    if "Troy" in player.name:
        print()

    if "*" in year_label:
        pro_bowl = 1
    else:
        pro_bowl = 0

    if "+" in year_label:
        all_pro = 1
    else:
        all_pro = 0

    player.checked_pro_accolades[year_num] = 1

    if method != "ALL":
        df["pro_bowl_" + str(year_num)] = [pro_bowl]
        df["all_pro_" + str(year_num)] = [all_pro]
    else:
        df["pro_bowl"] = [pro_bowl]
        df["all_pro"] = [all_pro]

    return df


def write_player_data_to_csv(df, path="../data/player_data.csv"):
    df = df.replace(np.NaN, 0)
    df.to_csv(path, index=False)


def summarize_positions(players):
    players_by_positions = {}
    hof_by_positions = {}
    count = 0
    hof_count = 0

    for player in players:
        count += 1
        if player.hall_of_famer:
            hof_count += 1
        for pos in player.positions:
            if pos in hof_by_positions.keys():
                hof_by_positions[pos][1] += 1
                if player.hall_of_famer:
                    hof_by_positions[pos][0] += 1

                players_by_positions[pos].append(player)

            else:
                players_by_positions[pos] = [player]
                hof_by_positions[pos] = [0,0]
                hof_by_positions[pos][1] = 1  # the total num of players in this position
                if player.hall_of_famer:  #
                    hof_by_positions[pos][0] = 1  # the number of hof players in this position

        for k,v in hof_by_positions.items():
            print("There are {0} {1}s".format(v[1],k))
            print("{0}% of {1}s are in the HOF".format(100*v[0]/v[1], k))

    print("There are {0} players and {1} HOFers, which is {2}%".format(count, hof_count, 100*hof_count/count) )

    return players_by_positions, hof_by_positions


if __name__ == "__main__":
    get_players()
    players = read_playerlist_from_csv(starting_range=1985, ending_range=2005)
    scrape_players()
    summarize_positions(players)

