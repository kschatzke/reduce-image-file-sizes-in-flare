# Reduce Output Image File Sizes in Flare
# Version 1.0 - July 10, 2025
# (C) 2025 Ken Schatzke

# Import the necessary modules, including Tinify
import argparse
import os
import logging
import json
from datetime import datetime

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("reduce_file_sizes_in_outputs")

# Import Tinify or install if it doesn't already exist
try:
    import tinify
except ImportError:
    logger.error("The Tinify Python package is not installed. To install it, open a command prompt and enter pip install --upgrade tinify.")

# Parse the arguments from the post-build command in the target file
parser = argparse.ArgumentParser()
parser.add_argument("--key", default="default_value")
parser.add_argument("--output", default="default_value")
parser.add_argument("--exclude", default="default_value")
parser.add_argument("--minsize", default="default_value")

args = parser.parse_args()

# Set the Tinify API key (or log an error if the key isn't provided)
if args.key != "default_value":
    tinify.key = args.key
else:
    logger.error("Include --key {Key} in the post-build event command line, where {Key} is your Tinify API key.")

# Set the output folder path (or log an error if the output folder path isn't provided)
if args.output != "default_value":
    directory = args.output
else:
    logger.error("Include --output $(OutputDirectory) in the post-build event command line.")

# Set file extensions for images
extensions = (".jpg", ".jpeg", ".png")

# Set folders to exclude
exclude = ["Skins", "skins"]

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

if args.key != "default_value" and args.output != "default_value":
    try:
        # Crawl through the output directory, identify all JPEG and PNG images
        # not in the excluded sub-directories and greater than the min file size (if provided)
        for root, dirs, files in os.walk(directory, topdown=True):
            dirs[:] = [d for d in dirs if d not in exclude]
            for file in files:
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path) / (1024 * 1024.0)
                
                if (file.endswith(extensions) and filter_by_size == False) or (file.endswith(extensions) and filter_by_size == True and file_size >= min_size):
                    found_files.append(file_path)

        # Use Tinify to reduce the found files' sizes
        for found_file in found_files:
            source = tinify.from_file(found_file)
            source.to_file(found_file)

        # Create the reduce-file-sizes-log.json log file
        data = {
            "datetime": current_datetime,
            "type": "output",
            "files": found_files
        }

        with open("reduce-file-sizes-log.json", "w") as json_file:
            json.dump(data, json_file, indent=4)

        # If no images in found_files, log an error
        if found_files == []:
            logger.error("No image files were found in the output that match the criteria in the command line. Make sure JPEG images in the project have .jpg or .jpeg extensions, PNG images in the project have .png extensions, and the --output parameter in the command line is set to $(OutputDirectory).")
    except:
        # If an error occurs in the above code, likely cause is invalid API key
        logger.error("Verify that your Tinify API key is valid and that the post-build event command line follows the conventions in read-me.htm.")