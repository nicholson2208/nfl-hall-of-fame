import sys

import utilities.scraper_utils as scraper
import utilities.preprocess_utils as preproc

# TODO: Make running main work

def main(start=1985, end=2005):
    scraper.get_players()
    players = scraper.read_playerlist_from_csv(starting_range=start, ending_range=end)
    scraper.scrape_players()
    scraper.summarize_positions(players)

    pyears = preproc.read_scraped_player_years_from_csv()
    preproc.preprocess_player_years(pyears)
    preproc.make_final_table(pyears, target="remaining_all_pro")
    preproc.make_final_table(pyears, target="remaining_pro_bowl")
    preproc.make_final_table(pyears, target="remaining_games")
    preproc.make_final_table(pyears, target="remaining_gs")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        main()
    elif len(sys.argv) == 3:
        main(int(sys.argv[1]), int(sys.argv[2]))
    else:
        print("Please type 'python main.py <start year> <end year>")

