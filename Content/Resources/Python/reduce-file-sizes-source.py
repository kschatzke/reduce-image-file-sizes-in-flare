# Reduce Source Image File Sizes in Flare
# Version 1.0 - July 10, 2025
# (C) 2025 Ken Schatzke

# Import pre-installed modules
import argparse
import os
import logging
import json
from datetime import datetime

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("reduce_file_sizes_in_source")

# Import Tinify or install if it doesn't already exist
try:
    import tinify
except ImportError:
    logger.error("The Tinify Python package is not installed. To install it, open a command prompt and enter pip install --upgrade tinify.")

# Parse the arguments from the pre-build command in the target file
parser = argparse.ArgumentParser()
parser.add_argument("--key", default="default_value")
parser.add_argument("--exclude", default="default_value")
parser.add_argument("--minsize", default="default_value")

args = parser.parse_args()

# Set the Tinify API key (or log an error if the key isn't provided)
if args.key != "default_value":
    tinify.key = args.key
else:
    logger.error("Include --key {Key} in the command line, where {Key} is your Tinify API key.")

# Set the location of the source files
current_directory = os.getcwd()
parent_directory = os.path.dirname(current_directory)
directory = os.path.dirname(parent_directory)

# Set file extensions for images
extensions = (".jpg", ".jpeg", ".png")

# Set folders to exclude
exclude = []

if args.exclude != "default_value":
    exclude_args = args.exclude.split(",")
    exclude += exclude_args

# Set minimum file size
filter_by_size = False

if args.minsize != "default_value":
    try:
        min_size = float(args.minsize)
        filter_by_size = True
    except:
        logger.error("For the --minsize parameter, provide a number (in megabytes) only. For example, 3 not 3MB.")

# Set other variables
found_files = []
current_datetime = str(datetime.now())

if args.key != "default_value":
    try:
        # Crawl through the Content directory, identify all JPEG and PNG images
        # not in the excluded sub-directories and greater than the min file size (if provided)
        for root, dirs, files in os.walk(directory, topdown=True):
            dirs[:] = [d for d in dirs if d not in exclude]
            for file in files:
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path) / (1024 * 1024.0)

                if (file.endswith(extensions) and filter_by_size == False) or (file.endswith(extensions) and filter_by_size == True and file_size >= min_size):
                    found_files.append(file_path)

        # Load reduce-file-sizes-log.json (if it exists) and compare to found files list
        try:
            with open('reduce-file-sizes-log.json', 'r') as file:
                previous_data = json.load(file)
            
            previous_files_set = set(previous_data["files"])
            found_files_set = set(found_files)
            filtered_files_set = found_files_set.difference(previous_files_set)
            filtered_files = list(filtered_files_set)
        except:
            filtered_files = found_files

        # Use Tinify to reduce the found files' sizes
        for filtered_file in filtered_files:
            source = tinify.from_file(filtered_file)
            source.to_file(filtered_file)

        # Create the reduce-file-sizes-log.json log file
        data = {
            "datetime": current_datetime,
            "type": "source",
            "files": found_files
        }

        with open("reduce-file-sizes-log.json", "w") as json_file:
            json.dump(data, json_file, indent=4)

        # If no images in found_files, log an error
        if found_files == []:
            logger.error("No image files were found in the Content folder that match the criteria in the command line. Make sure JPEG images in the project have .jpg or .jpeg extensions and PNG images in the project have .png extensions.")
    except:
        # If an error occurs in the above code, likely cause is invalid API key
        logger.error("Verify that your Tinify API key is valid and that the command line is set up as defined in read-me.htm.")