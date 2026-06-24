import os
import sys
import argparse
import traceback
import asyncio
from real_estate_scraper import RealEstateScraperJob

def main(args):
    """ Run task """
    try:
        scraper = RealEstateScraperJob()
        scraper.run(args.type, args.home_type, args.location, args.export_type, args.spreadsheet_id)
    except Exception as e:
        trace = traceback.format_exc()
        print("Error while parsing site: ")
        print(trace)
        sys.exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", required=True)
    parser.add_argument("--home_type")
    parser.add_argument("--location")
    parser.add_argument("--export_type")
    parser.add_argument("--spreadsheet_id")

    args = parser.parse_args()
    main(args)
