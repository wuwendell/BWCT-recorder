"""
Short script to merge all video files in the current directory into a
single video file using ffmpeg. The videos will be merged in alphabetical
order by filename, so that video files starting with 'a' will be at the
beginning of the output video, and those with 'z' will be at the end.

Essentially, this script will run the following ffmpeg command:
`ffmpeg -f concat -safe 0 -i videoList.txt -c copy output.mp4`
where videoList.txt is a text file containing the list of video files to merge.

Prerequisites:
- ffmpeg must be installed and in the system PATH.
- Output video file name must not already exist in the current directory.
- Input video files must be in the same directory as this script, and must 
  have the file extension '.mp4'.

Usage:
- Run the script using python 3: `python videoMerge.py`

Authors: Wendell Wu, Andrei Gerashchenko, Raif Olson

Last Updated: 2024-02-15
"""

import os			# check if files exist
import subprocess   # run shell commands

# Check if ffmpeg is installed
try:
	subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
except FileNotFoundError:
	print("Error: ffmpeg is not installed or not in the system PATH.")
	exit(1)
except subprocess.CalledProcessError:
	print("Error: An issue occurred while checking ffmpeg version.")
	exit(1)

# Get name of desired output video file
outputVideoFile = input("Enter name of output video file ('example.mp4'): ")

# Check if output file already exists
if os.path.exists(outputVideoFile):
	print("Error: Output file already exists.\
 This script will not overwrite an existing video file.")
	exit(1)

# Get list of video files in the current directory
videoFiles = [f for f in os.listdir() if os.path.isfile(f) and f.endswith(".mp4")]

# Check if there are any video files in the current directory
if len(videoFiles) == 0:
	print("Error: No video files found in the current directory.")
	exit(1)

# Sort the video files in alphabetical order
videoFiles.sort()

# Create a text file to store the list of video files
videoListFile = "videoList.txt"
with open(videoListFile, "w") as f:
	for videoFile in videoFiles:
		f.write(f"file '{videoFile}'\n")

# Run ffmpeg to merge the video files
ffmpeg_command = [
	"ffmpeg",
	"-f", "concat",
	"-safe", "0",
	"-i", videoListFile,
	"-c", "copy",
	outputVideoFile
]
subprocess.run(ffmpeg_command, check=True)

# Remove the video list file
os.remove(videoListFile)

# print success message with how many videos were merged and in what order
print(f"Successfully merged {len(videoFiles)} video files:")
for videoFile in videoFiles:
	print(f"- {videoFile}")
print(f"into {outputVideoFile}.")
