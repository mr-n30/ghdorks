#!/bin/bash

# Function to display usage
usage() {
    echo "Usage: $0 -f <dorks_file> -t <target>"
    echo "  -f  Path to the file containing dorks"
    echo "  -t  Target string to search for"
    exit 1
}

# Initialize variables
DORKS=""
TARGET=""

# Parse command-line arguments
while getopts "d:t:h" opt; do
    case $opt in
        f) DORKS="$OPTARG" ;;
        t) TARGET="$OPTARG" ;;
        h) usage ;;
        *) usage ;;
    esac
done

# Ensure required arguments are provided
if [[ -z "$DORKS" || -z "$TARGET" ]]; then
    echo "Error: Missing required arguments."
    usage
fi

# Main loop to iterate through dorks
if [[ -f "$DORKS" ]]; then
    for DORK in $(cat "$DORKS"); do
        echo "######### DORK: $DORK"
        echo "https://github.com/search?q=%22$TARGET%22%20$DORK&type=code"
        echo ""
    done
else
    echo "Error: Dorks file '$DORKS' not found."
    exit 1
fi
