"""
Short script to trim a video file using ffmpeg.

Prerequisites:
- ffmpeg must be installed and in the system PATH.
- Input video file must be in the same directory as this script.

Usage:
- Run the script using python 3: `python videoTrim.py`

Authors: Wendell Wu, Andrei Gerashchenko

Last Updated: 2024-02-15
"""

import os			# check if files exist
import subprocess   # run shell commands
import re           # regex

# Check if ffmpeg is installed
try:
	subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
except FileNotFoundError:
	print("Error: ffmpeg is not installed or not in the system PATH.")
	exit(1)
except subprocess.CalledProcessError:
	print("Error: An issue occurred while checking ffmpeg version.")
	exit(1)

# Get input video file
inputVideoFile = input("Enter filename of video to trim: ")
if not os.path.exists(inputVideoFile):
	print("Error: Input video not found.")
	exit(1)

# Get name of desired output video file
outputVideoFile = input("Enter name of output video file ('example.mp4'): ")

# check if output file already exists
if os.path.exists(outputVideoFile):
	print("Error: Output file already exists.\
 This script will not overwrite an existing video file.")
	exit(1)

# Get user input for trim durations
trimStartTimestamp = input("Enter starting timestamp of input video (HH:MM:SS.mmm): ")
trimEndTimestamp = input("Enter ending timestamp of input video (HH:MM:SS.mmm): ")

# Check if timestamps are in the correct format using regex
timestampRegex = r"^\d{2}:\d{2}:\d{2}\.\d{3}$"
if not re.match(timestampRegex, trimStartTimestamp) or not re.match(timestampRegex, trimEndTimestamp):
	print("Error: Timestamps are not in the correct format.\
 They must be in the format HH:MM:SS.mmm.")
	exit(1)

# Run ffmpeg to trim the video
ffmpeg_command = [
	"ffmpeg",
	"-ss", trimStartTimestamp,
	"-to", trimEndTimestamp,
	"-i", inputVideoFile,
	"-c", "copy",
	outputVideoFile
]
subprocess.run(ffmpeg_command, check=True)

print("Video trimmed successfully.")