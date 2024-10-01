#!/usr/bin/env python3
import argparse
import requests
import urllib.parse
from time import sleep
from os import environ
from sys import exit, argv

def main() -> None:
    parser = argparse.ArgumentParser(description="Automate GitHub Dorking")
    parser.add_argument('-f', '--file', required=True, help="Path to the file containing dorks (Will be appended to query)")
    parser.add_argument('-q', '--query', help="Query e.g example.com (Batch queries are not allowed via GitHub API)")
    parser.add_argument('-o', '--output', help="Path to the output file (optional)")
    parser.add_argument('-s', '--sleep', help="Time to wait between GitHub requests in seconds (Default is 10.0 seconds)", default=10.0)
    args = parser.parse_args()

    token = environ.get("GH_TOKEN")
    if token == None:
        print("[ERROR] Please set GitHub token using environment variable GH_TOKEN")
        exit(1)

    github_api_url = "https://api.github.com/search/code?q="
    query = args.query

    headers = {
        "Authorization": f"token {token}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.6613.120 Safari/537.36"
    }

    try:
        while True:
            dork_file = args.file
            with open(dork_file, "r") as f:
                lines = f.readlines()
                for line in lines:
                    dork = line.strip()
                    github_url = f"{github_api_url}{urllib.parse.quote(query)}%20{urllib.parse.quote(dork)}"
                    r = requests.get(github_url, headers=headers)
                    code = r.status_code
                    sleep(args.sleep)

                    if code != 200:
                        while code != 200:
                            print(f"[ERROR] An error occurred. Recieved HTTP status code {code}. Sleeping for 30 seconds and then trying again...")
                            sleep(30)
                            r = requests.get(github_url, headers=headers)
                            code = r.status_code
                            if code == 200:
                                break

                    result_count = int(r.json().get("total_count"))
                    if result_count > 0:
                        result_string = f"[FOUND RESULTS] https://github.com/search?q={urllib.parse.quote(query)}%20{urllib.parse.quote(dork)}&type=code [Results: {result_count}] [Dork: {dork}] [Query: {query}]"
                        print(result_string)
                        if args.output:
                            with open(args.output, "a") as o:
                                o.write(f"{result_string}\n")

                    # TODO:
                    # This will be for verbose output only
                    # because if there's a massive amount of results
                    # we don't want to go through 8k etc. manually
                    # It's better to find if there's results and if
                    # there is then we go manually

                    #for item in r.json().get("items"):
                    #    print(f"{item.get('html_url')} [{dork}] [{query}]")

                    if len(lines) - 1 == lines.index(line):
                        return

    except Exception as e:
        print(f"[ERROR] An error occurred with your request: {e}")

    return

if __name__ == "__main__":
    main()
