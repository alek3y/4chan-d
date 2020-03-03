#!/usr/bin/python3

"""
4chan thread downloader tool by AleK3y :P

Download all the files and json from a given thread.
"""

import os, sys
import requests
import json		# Prettify json

# Project info
DESCRIPTION = "Download threads from 4chan."
ARGUMENTS = {
	# Option: [Description, Obligatory]
	"-u": ["4chan thread url", True],
	"-o": ["output parent directory", False],
	"-f": ["if enabled the file names will be the uploaded ones", False],
}
SINGLE_ARGUMENTS = [
	"-f",
]
USAGE = "[OPTIONS]"

# Constants
SEP = ' '*4
FILE_SERVER = "http://i.4cdn.org"
JSON_SERVER = "http://a.4cdn.org"
PRETTIFY_JSON = True
DEFAULT_JSON_INDENT = 2

# Print usage
def usage():
	print(f"Usage: {sys.argv[0]} {USAGE}")
	print(f"{SEP}{DESCRIPTION}\n")
	print(f"{SEP}Options:")
	for arg in ARGUMENTS:
		print(f" {SEP}{arg}{SEP*2}{ARGUMENTS[arg][0]}")
	sys.exit()

# Check if all arguments are present
for arg in ARGUMENTS:
	if arg not in sys.argv and ARGUMENTS[arg][1]:
		usage()
	elif arg in sys.argv and arg not in SINGLE_ARGUMENTS:
		if sys.argv[sys.argv.index(arg)+1][0] == "-":
			usage()

# Check if there are wrong arguments on sys.argv
for arg in sys.argv:
	if arg[0] == "-" and arg not in ARGUMENTS:
		usage()

# Setup arguments
arguments_dict = {}
for arg in ARGUMENTS:
	if arg in sys.argv and arg not in SINGLE_ARGUMENTS:
		arguments_dict[arg] = sys.argv[sys.argv.index(arg)+1]

## Main code ##

# Set up data from arguments
download_url = arguments_dict["-u"]
output_dir = "." if "-o" not in arguments_dict else arguments_dict["-o"]
original_name = "-f" in sys.argv

# Set up data from url
server_dir = download_url.replace("https://", "").replace("http://", "").split("#p")[0].split("/")[1:]
thread_number = download_url.split("/thread/")[1].split("#p")[0]

# Get the json of the thread
thread_json = requests.get(f"{JSON_SERVER}/{server_dir[0]}/thread/{server_dir[2]}.json", stream=True).content

# Change to working directory where the file will be downloaded
os.makedirs(f"{output_dir}/{server_dir[0]}/{server_dir[2]}", exist_ok=True)
os.chdir(f"{output_dir}/{server_dir[0]}/{server_dir[2]}")
files_in_folder = sorted(os.listdir())

# Download the .json
thread_json = requests.get(f"{JSON_SERVER}/{server_dir[0]}/thread/{server_dir[2]}.json", stream=True).content

if PRETTIFY_JSON:
	open("thread.json", "w").write(json.dumps(json.loads(thread_json), indent=DEFAULT_JSON_INDENT, sort_keys=False))
else:
	open("thread.json", "wb").write(thread_json)

# Get the thread infos like posts by opening the downloaded .json
thread = eval(open("thread.json", "r").read())

# Count the images to print progress
image_number = 0
for post in thread["posts"]:
	if "filename" in post:
		image_number += 1

# Download images using the .json
print("Downloading..")
current_image = 0		# Counter for progress
for post in thread["posts"]:

	# Check if post has file and if so download it
	if "filename" in post:
		output_name = f"{post['tim']}{post['ext']}" if not original_name else f"{post['filename']}{post['ext']}"		# Evaluate file name

		# Download only if not on folder
		if output_name not in files_in_folder:
			image = requests.get(f"{FILE_SERVER}/{server_dir[0]}/{post['tim']}{post['ext']}")		# Get the image with requests
			open(output_name, "wb").write(image.content)		# Save image

		current_image += 1
		print(f"[{current_image}/{image_number}]", end="\r")		# Print progress

print("Finished downloading!")
print(f"The thread is located in {os.getcwd()}")
