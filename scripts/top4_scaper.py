import sys
import os
from paper_scraper import search

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print(
            "USAGE: python3 %s year_min year_max keyword1 [keyword2 ...]" % sys.argv[0])
        exit(1)

    venues = ['ndss', 'acm+computer+and+communications+security',
              'ieee+symposium+on+security+and+privacy', 'usenix+security']
    year_min = int(sys.argv[1])
    year_max = int(sys.argv[2])
    keywords = sys.argv[3:]
    for venue in venues:
        search(venue, year_min, year_max, keywords)
