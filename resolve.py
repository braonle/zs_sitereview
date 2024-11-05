#!/usr/bin/env python3
import logging
import argparse
import glob
import os
import json

from datetime import datetime
from src.lookup import ZSRQuerier
from src.cache import DEFAULT_CACHE_FILE

if __name__ == '__main__':

    logging.basicConfig(format="{asctime} [{module}:{lineno}] [{levelname}] {message}", style="{",
                        datefmt="%d/%m/%Y %H:%M:%S", level=logging.INFO)

    if __name__ == '__main__':
        parser = argparse.ArgumentParser(description="Lookup URLs with Zscaler Site Review and mark threats")

        parser.add_argument('-l', '--list', type=str, nargs="?", dest="url_list_filename",
                            const="", metavar="FILE", default=None,
                            help='filename for the list of URLs; latest .txt used by default')
        parser.add_argument('-c', '--cache', type=str, dest="cache_filename",
                            metavar="FILE", default=DEFAULT_CACHE_FILE,
                            help=f"cache filename; '{DEFAULT_CACHE_FILE}' is used by default")
        parser.add_argument('-x', '--excel', type=str, nargs="?", dest="excel_filename",
                            const="", metavar="FILE", default=None,
                            help="CSE SSL Excel filename; by default latest .xlsx is used")
        parser.add_argument('--excel-export', nargs="?", dest="excel_export",
                            const="out.xlsx", metavar="FILE", default=None,
                            help='Export data to Excel')
        parser.add_argument('--json-export', nargs="?", dest="json_export",
                            const="out.json", metavar="FILE", default=None,
                            help='Export data to JSON')
        args = parser.parse_args()

        if args.url_list_filename is None:
            url_list_filename = None
        elif args.url_list_filename == "":
            files = glob.glob("*.txt")
            files.remove("requirements.txt")
            if not files:
                logging.info("No .txt file was found in the directory of the application. "
                             "URL list search is not used.")
                url_list_filename = None
            else:
                url_list_filename = max(files, key=os.path.getmtime)
        else:
            url_list_filename = args.url_list_filename

        if args.excel_filename is None:
            excel_filename = None
        elif args.excel_filename == "":
            files = glob.glob("*.xlsx")
            if not files:
                logging.info("No .xlsx file was found in the directory of the application. "
                             "CSE SSL spreadsheet search is not used.")
                excel_filename = None
            else:
                excel_filename = max(files, key=os.path.getmtime)
        else:
            excel_filename = args.excel_filename

        st = datetime.now()

        querier = ZSRQuerier()

        if url_list_filename is not None:
            logging.info("Resolving URLs from text file %s", url_list_filename)
            querier.load_file(filename=url_list_filename)
            querier.lookup_urls()

            if args.json_export is not None:
                logging.info("Saving URLs from text file to JSON %s", args.json_export)

                with open(args.json_export, "w", encoding="utf-8") as f:
                    json.dump(querier.processed_urls, f, indent=4, default=list)

            if args.excel_export is not None:
                logging.info("Saving URLs from text file to Excel %s", args.excel_export)
                querier.to_excel(args.excel_export)

        if excel_filename is not None:
            logging.info("Resolving URLs from CSE SSL spreadsheet %s", excel_filename)
            querier.search_excel(excel_filename, ["SSL Dest Groups", "SSL Custom Categories"])

        et = datetime.now()
        logging.info("Script ran for %s seconds.", et - st)
