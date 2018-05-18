import requests
import time
import csv
import os
import pandas as pd
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

            except:
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
                position = eval(line[1]) # TODO: oops, I forgot to put this in the csv
                website = line[2]
                start = int(line[3])
                end = int(line[4])
                hof = int(line[5])

                if start >= starting_range and end <= ending_range:  # filter the player that we actually want
                    player = Player(name, website, position, start, end, hof)
                    players.append(player)
            print("There are {0} players that had" 
                  " their whole careers between {1} and {2}".format(len(players), starting_range, ending_range))

            return players

def scrape_players():
    """

    :return:
    """
    starting_range = 1985
    ending_range = 2005

    # TODO: Add the thing with sys to see if the file exists. If yes, read it. Do the scrape again
    players = read_playerlist_from_csv(starting_range=starting_range, ending_range=ending_range)


    # TODO: change this next line back to player
    for player in players[:10]:
        scrape_player(player)

    write_player_data_to_csv(players, path="../data/player_data{0}-{1}.csv".format(starting_range,ending_range))


def scrape_player(player):
    """
    a function that add the the players
    :param player:
    :return:
    """

    print(player.website)
    r = requests.get(player.website)
    time.sleep(.04)
    soup = BeautifulSoup(r.content, "lxml")

    df = pd.DataFrame()

    get_passing(player,soup,df)

    get_rush_rec(player, soup, df)

    get_returns(player, soup, df)

    get_kick_punt(player, soup, df)

    get_defense(player, soup, df)

    # get passing stats
    # J

    # get rushing and rec stats
    rush_rec_table_list = soup.find_all("div", {"id": "div_rushing_and_receiving"})

    if len(rush_rec_table_list) == 0:
        # either make a bunch of 0s or TBD
        pass
    else:
        # there should only be one
        # now get all of the shit
        print()


def get_passing(player, soup, df):
    """
    Jayden
    :param player:
    :param soup:
    :param df:
    :return:
    """
    pass


def get_rush_rec(player, soup, df):
    """
    Matt
    :param player:
    :param soup:
    :param df:
    :return:
    """
    pass


def get_returns(player, soup, df):
    """
    Matt
    :param player:
    :param soup:
    :param df:
    :return:
    """
    pass


def get_kick_punt(player, soup, df):
    """
    Jayden
    :param player:
    :param soup:
    :param df:
    :return:
    """
    pass


def get_defense(player, soup, df):
    """
    Jayden
    :param player:
    :param soup:
    :param df:
    :return:
    """
    pass


def write_player_data_to_csv(players, path="../data/player_data.csv"):
    pass


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
    #get_players()
    #players = read_playerlist_from_csv(starting_range=1985, ending_range=2005)
    scrape_players()
    #summarize_positions(players)

