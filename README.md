# BWCT Recording Device

Repository to hold software and hardware designs for the Bike Walk census tool's
recording device.

## Hardware

Raspberry Pi Model 4B.

## Usage

### Concatenate and Trim Videos with ffmpeg

Ensure that `[mylist.txt]` is in chronological order.

`ffmpeg -f concat -safe 0 -i [mylist.txt] -c copy [output.mp4]`

See <https://stackoverflow.com/questions/7333232/how-to-concatenate-two-mp4-files-using-ffmpeg>.

### Video Output File Naming Convention

dunno. lol.

## Configuration

Default Pi OS on a 64 GB microSD.

Configure scripts to run on startup.
