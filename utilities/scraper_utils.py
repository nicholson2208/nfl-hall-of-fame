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

        #print(player_div.contents)
        for player_anchor_tag in player_div[0].children:
            try:
                player_anchor_tag = str(player_anchor_tag)
                name = player_anchor_tag.split(".htm\">")[1].split("</a>")[0]
                #print(name)
                website = player_anchor_tag.split("href=\"")[1].split('"')[0]
                #print(website)
                position = player_anchor_tag.split("</a>")[1].split("(")[1].split(")")[0]
                #print(position)
                starting = player_anchor_tag[-13:-9]
                ending = player_anchor_tag[-8:-4]
                HOF = "+" in player_anchor_tag

                players.append(Player(name, website, position, starting, ending, HOF))

            except:
                print("Something weird with {0}".format(player_anchor_tag))

    print(len(players))
    write_playerlist_to_csv(players)
    print("hi")


def write_playerlist_to_csv(players, filename="../data/player_list.csv"):
    """
    Once we have scraped the initial list, store it as a csv
    :param players:
    :return:
    """
    with open(filename, "w",newline='') as outfile:
        filewriter = csv.writer(outfile)
        filewriter.writerow(["Player Name", "Link", "Starting Year", "Ending Year", "Hall of Fame"])

        for player in players:
            row = [player.name, player.website, player.starting_year, player.ending_year, player.hall_of_famer]
            filewriter.writerow(row)





def read_playerlist_from_csv():
    pass

if __name__ == "__main__":
    get_players()

