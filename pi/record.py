from picamera2 import Picamera2
import datetime
import time
import RPi.GPIO as GPIO

# Set up GPIO pins
button_pin = 10
led_pin = 26

# Constant to determine whether a preview is shown while recording
SHOW_PREVIEW = True

GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(led_pin, GPIO.OUT)

# Initialize the camera and set the resolution to 1080p
picam2 = Picamera2()
camera_config = picam2.create_video_configuration(main={"size": (1920, 1080)})
picam2.configure(camera_config)

# Function to generate the filename
def get_filename():
 return f"census_tool_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.h264"

# Main loop to handle recording and button press events
recording = False
while True:
 input_state = GPIO.input(button_pin)
 if input_state == False:
     if recording:
         # Stop recording
         picam2.stop_recording()
         recording = False
         # Turn off LED
         GPIO.output(led_pin, GPIO.LOW)
     else:
         # Start recording
         filename = get_filename()
         picam2.start_recording(filename, show_preview=SHOW_PREVIEW)
         recording = True
         # Blink LED quickly
         for _ in range(5):
             GPIO.output(led_pin, GPIO.HIGH)
             time.sleep(0.2)
             GPIO.output(led_pin, GPIO.LOW)
             time.sleep(0.2)
 elif recording:
     # Slow blink LED
     GPIO.output(led_pin, GPIO.HIGH)
     time.sleep(1)
     GPIO.output(led_pin, GPIO.LOW)
     time.sleep(1)
 else:
     # No recording, no button press
     time.sleep(0.1)

# Clean up GPIO settings when script exits
GPIO.cleanup()
