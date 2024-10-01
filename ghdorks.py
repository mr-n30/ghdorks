#!/usr/bin/env python3
import re
import argparse
import urllib.parse
from time import sleep
from os import environ
from sys import exit, argv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Setup cmdline args
parser = argparse.ArgumentParser(description="Automate GitHub Dorking")
parser.add_argument('-f', '--file', required=True, help="Path to the file containing dorks (Will be appended to query)")
parser.add_argument('-q', '--query', help="Query or GitHub Batch Query Syntax e.g example.com OR testexample.com OR devexample ")
parser.add_argument('-o', '--output', help="Path to the output file (optional)")
parser.add_argument('-s', '--sleep', help="Time in seconds to wait between GitHub requests (Default is 10.0 seconds)", default=10.0, type=float)
parser.add_argument('--chrome-driver', help="Path to chromedriver (Default /usr/bin/chromedriver)", default="/usr/bin/chromedriver")
parser.add_argument('-c', '--cookie', help="Your GitHub user_session cookie", default="/usr/bin/chromedriver")
parser.add_argument('--chrome-wait', help="Time in seconds to tell Chrome to wait for the page to load (Deafult 10)", default=10)
args = parser.parse_args()

# Setup Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_service = Service(args.chrome_driver)
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
cookie = {"name": "user_session", "value": args.cookie}

def request_github(url: str) -> float:
    try:
        driver.get(url)
        driver.add_cookie(cookie)
        driver.refresh()
        wait = WebDriverWait(driver, int(args.chrome_wait))
        xpath = "/html/body/div[1]/div[5]/main/react-app/div/div/div[1]/div/div/div[1]/div[2]/div/div/div/div/ul/li[1]/ul/li[1]/a/div/div/span[2]/span[1]/span"
        element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
        element_value = element.text
        pattern = r"(\d+\.?\d*)[a-zA-Z]?"
        match = re.search(pattern, element_value)

        if match is None:
            print(f"[ERROR] No match found, check manually: {url}")
            return 0

        if float(match.group(1)) > 0:
            return match.group(0)

    except Exception as e:
        print(f"[ERROR] No match found, check manually: {url}")
        return 0.0

def main() -> None:
    github_url = "https://github.com/search?q="
    query = args.query
    try:
        while True:
            dork_file = args.file
            with open(dork_file, "r") as f:
                lines = f.readlines()
                for line in lines:
                    dork = line.strip()
                    url = f"{github_url}{urllib.parse.quote(query)}%20{urllib.parse.quote(dork)}&type=code"
                    print(f"[INFO] Trying: {url}")
                    result_string = f"[FOUND] {url} [Results: {request_github(url)}] [Dork: {dork}]"
                    print(result_string)
                    if args.output:
                        with open(args.output, "a") as o:
                            o.write(f"{result_string}\n")

                    if len(lines) - 1 == lines.index(line):
                        driver.quit()
                        return

                    sleep(args.sleep)
    except KeyboardInterrupt:
        print("Cancelled...")
        return
    except Exception as e:
        print(f"[ERROR] An error occurred with the request: {url}")
        pass

    return


if __name__ == "__main__":
    main()
