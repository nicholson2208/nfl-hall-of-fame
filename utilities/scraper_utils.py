import requests
import time
import csv
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
                hof = "+" in player_anchor_tag

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
        filewriter.writerow(["Player Name", "Link", "Starting Year", "Ending Year", "Hall of Fame"])

        for player in players:
            row = [player.name, player.website, player.starting_year, player.ending_year, player.hall_of_famer]
            filewriter.writerow(row)


def read_playerlist_from_csv(starting_range=1985, ending_range=2005, path="../data/player_list.csv"):
    """

    :param starting_range:
    :param ending_range:
    :param path:
    :return:
    """
    with open(path, "r") as infile:
            csv_reader = csv.reader(infile)
            header = next(csv_reader)  # do we need to do anything with this?
            players = []
            for line in csv_reader:
                name = line[0]
                website = line[1]
                position = ["This is garbage"]  # TODO: oops, I forgot to put this in the csv
                start = int(line[2])
                end = int(line[3])
                hof = bool(line[4])

                if start >= starting_range and end <= ending_range:  # filter the player that we actually want
                    player = Player(name, website, position, start, end, hof)
                    players.append(player)
            print("There are {0} players that had" 
                  " their whole careers between {1} and {2}".format(len(players), starting_range, ending_range))

            return players

def scape_players():
    """

    :return:
    """
    starting_range = 1985
    ending_range = 2005
    players = read_playerlist_from_csv(starting_range=starting_range, ending_range=ending_range)

    for player in players:
        scrape_player(player)

    write_player_data_to_csv(players, path="../data/player_data{0}-{1}.csv".format(starting_range,ending_range))


def scrape_player(player):
    """
    a function that add the the players
    :param player:
    :return:
    """

    r = requests.get(player.website)
    time.sleep(.04)
    soup = BeautifulSoup(r.content, "lxml")

    # get the position(s)

    # get passing stats

    # get rushing stats

    # get receiving stats

    # get kicking and punting stats

    # get returning stats

    # get blocking stats?


def write_player_data_to_csv(players, path="../data/player_data.csv"):
    pass


if __name__ == "__main__":
    scape_players()
