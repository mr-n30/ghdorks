# ghdorks

Automate GitHub Dorks Recon

---

## About

`ghdorks` is a tool designed to streamline GitHub Dorking. It includes two versions:

1. **`ghdorks.sh`**: A simple shell script that prints dork URLs for manual exploration in your browser.
2. **`ghdorks.py`**: A Python script that automates dorking using the GitHub API, fetching results directly.

---

## Features

### `ghdorks.sh`
- Prints out GitHub dork URLs directly to the terminal.
- Ideal for manual exploration via browser.

### `ghdorks.py`
- Utilizes the GitHub API to automate dork searches.
- Retrieves the number of matches for each dork.
- Handles rate-limiting gracefully and supports retries.
- Saves results to a file if specified.
- Prints out GitHub dork URLs directly to the terminal.

---

## Usage

### `ghdorks.sh`
`ghdorks.sh` simply prints out the dork URL in the terminal so you can visit it in a browser.

#### Usage:
```sh
./ghdorks.sh -f dorks2.txt -t mytargetname
```

### `ghdorks.py`
`ghdorks.py` interacts with the GitHub API to automate dork queries and display results with more control, including rate limit handling and retries.

#### Usage:
```sh
python3 ghdorks.py -f dorks2.txt -t mytargetname -k your_github_api_key --output results.txt
```

---

## Thank You For Using!
```
This version should now be complete without any issues. Let me know if this works for you!
```
