#!/usr/bin/python3
import time
import argparse
import requests
from urllib.parse import quote
from colorama import Fore, Style

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Automate GitHub dorks recon.")
    parser.add_argument(
        "--file", "-f",
        type=str,
        required=True,
        help="File containing dorks to use as part of the query string."
    )
    parser.add_argument(
        "--target", "-t",
        type=str,
        required=True,
        help="Target to include in the search query."
    )
    parser.add_argument(
        "--api-key", "-k",
        type=str,
        required=True,
        help="GitHub API key for authorization."
    )
    parser.add_argument(
        "--sleep", "-s",
        type=float,
        required=False,
        default=3.0,
        help="Default time in seconds to sleep between requests (default: 3.0)."
    )
    parser.add_argument(
        "--retries", "-r",
        type=int,
        required=False,
        default=5,
        help="Maximum number of retries for rate-limited requests (default: 5)."
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        required=False,
        help="File to write the output to in addition to printing."
    )
    args = parser.parse_args()

    # Extract arguments
    file_path = args.file
    target = args.target
    api_key = args.api_key
    default_sleep = args.sleep
    max_retries = args.retries
    output_file = args.output

    # Open the output file if specified
    output_fp = None
    if output_file:
        try:
            output_fp = open(output_file, "w")
        except Exception as e:
            print(f"Error opening output file '{output_file}': {e}")
            return

    def log_output(message, error=False):
        """Helper function to print and write output to the file if specified."""
        if error:
            print(f"{Fore.RED}[ERROR]{Style.RESET_ALL}: {message}")
            return

        print(f"{Fore.GREEN}[DORK]{Style.RESET_ALL}: {message}")
        if output_fp:
            if error:
                output_fp.write(f"{Fore.RED}[ERROR]{Style.RESET_ALL}: {message}" + "\n")
                return
            output_fp.write(f"{Fore.GREEN}[DORK]{Style.RESET_ALL}: {message}" + "\n")

    # Read the file and process dorks
    try:
        with open(file_path, "r") as f:
            dorks = f.read().split()
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {api_key}"
    }

    for dork in dorks:
        # URL encode the dork and target
        encoded_dork = quote(dork)
        encoded_target = quote(target)

        # Construct the API URL
        query_url = f"https://api.github.com/search/code?q=%22{encoded_target}%22%20{encoded_dork}"
        public_url = f"https://github.com/search?q=%22{encoded_target}%22%20{encoded_dork}&type=code"

        success = False
        retries = 0

        while not success:
            try:
                # Make the API request
                response = requests.get(query_url, headers=headers)

                if response.status_code == 403:
                    # Handle rate limit
                    retry_after = response.headers.get("Retry-After")
                    reset_time = response.headers.get("X-RateLimit-Reset")
                    if retry_after:
                        sleep_time = float(retry_after)
                        print(f"[!] Rate limit hit. Retrying after {sleep_time} seconds...")
                    elif reset_time:
                        reset_epoch = int(reset_time)
                        current_time = int(time.time())
                        sleep_time = max(reset_epoch - current_time, 1)
                        print(f"[!] Rate limit hit. Retrying at {reset_time} (in {sleep_time} seconds)...")
                    else:
                        sleep_time = default_sleep
                        print(f"[!] Rate limit hit. Retrying with default sleep of {sleep_time} seconds...")

                    time.sleep(sleep_time)
                    retries += 1
                    if retries >= max_retries:
                        print(f"[!] Maximum retries ({max_retries}) reached for dork '{dork}'. Moving to the next dork...")
                        break
                    continue

                response.raise_for_status()
                data = response.json()

                # Extract result count
                result_count = data.get("total_count", 0)

                # Print and write the output
                if int(result_count) > 0:
                    log_output(f"{dork}, Results: {result_count}\n{public_url}\n")
                    success = True

            except requests.exceptions.RequestException as e:
                log_output(f"Error querying for dork '{dork}': {e}", True)
                retries += 1
                if retries >= max_retries:
                    print(f"[!] Maximum retries ({max_retries}) reached for dork '{dork}'. Moving to the next dork...")
                    break
                sleep_time = default_sleep * (2 ** retries)  # Exponential backoff
                print(f"[!] Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)

    # Close the output file if opened
    if output_fp:
        output_fp.close()

if __name__ == "__main__":
    main()
