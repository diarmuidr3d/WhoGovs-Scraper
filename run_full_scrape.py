import sys

import datetime

from MembersScraper import MembersScraper
import DebatesScraper
from Objects import export_graph
import traceback


def scrape_all_members():
    # MembersScraper().scrape_details(6)
    rep_id = 1
    scraper = MembersScraper()
    false_count = 0
    while false_count < 5:
        return_value = scraper.scrape_details(rep_id)
        if return_value:
            false_count = 0
        else:
            false_count += 1
        rep_id += 1


def scrape_all_debates():
    dail = "dail"
    seanad = "seanad"
    earliest_year = 1919
    current_year = datetime.datetime.now().year
    while current_year >= earliest_year:
        DebatesScraper.get_debate_urls_for_year(dail, current_year)
        DebatesScraper.get_debate_urls_for_year(seanad, current_year)
        current_year -= 1


if __name__ == "__main__":
    try:
        # scrape_all_members()
        scrape_all_debates()
    except (KeyboardInterrupt, SystemExit, Exception) as err:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("*** print exception: ***")
        traceback.print_exception(exc_type, exc_value, exc_traceback, file=sys.stdout)
        print("*** Exception over ***")
        export_graph("whogovs.n3")
    export_graph("whogovs.n3")