from picamera2 import Picamera2
from picamera2.encoders import Quality
import datetime
import time
import RPi.GPIO as GPIO
from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Initialize variables
recording = False
start_time = 0

# Debounce time
debounce_time = 50  # milliseconds

# Video recording length
record_length = 10 * (1000 * 60)  # 10 minutes in milliseconds

# Set up GPIO pins
button_pin = 16
led_pin = 26

# Define the directory to save the files to
save_directory = "/media/pi/0123-4567/recordings/"

GPIO.setmode(GPIO.BCM)
GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(led_pin, GPIO.OUT)

# Initialize the camera and set the resolution to 1280x720
picam2 = Picamera2()
camera_config = picam2.create_video_configuration(main={"size": (1280, 720)})
picam2.configure(camera_config)

# Start the camera
picam2.start()
print("Camera started, press button to begin recording")

# Function to generate the filename
def get_filename():
    return f"census_tool_{datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.mp4"

# Function to get current time in milliseconds
def millis():
    return round(time.time() * 1000)

last_update = millis()
last_state = GPIO.input(button_pin)

# Main loop to handle recording and button press events
@app.before_first_request
def initialize_camera_status():
    global recording, start_time
    recording = False
    start_time = 0

@app.route('/')
def index():
    global recording, start_time
    context = {
        'recording': recording,
        'duration': int(time.time() - start_time) if recording else 0
    }
    return render_template('index.html', **context)

@app.route('/start_recording')
def start_recording():
    global recording, start_time
    recording = True
    start_time = time.time()
    return jsonify({'status': 'Recording started'})

@app.route('/stop_recording')
def stop_recording():
    global recording, start_time
    recording = False
    start_time = 0
    return jsonify({'status': 'Recording stopped'})

app.run(debug=True, host='0.0.0.0', port=8080)

while True:
    input_state = GPIO.input(button_pin)
    if input_state != last_state:
        if (millis() - last_update) >= debounce_time:
            last_state = input_state
            last_update = millis()
        else:
            continue
    if input_state == True:
        handled = False
    elif input_state == False and handled == False:
        handled = True
        if recording:
            # Stop recording
            picam2.stop_recording()
            recording = False
            # Blink LED quickly
            for _ in range(5):
                GPIO.output(led_pin, GPIO.LOW)
                time.sleep(0.1)
                GPIO.output(led_pin, GPIO.HIGH)
                time.sleep(0.1)
            led_state = GPIO.LOW
            # Update camera recording status
            app.config['camera_recording'] = False
            app.config['camera_duration'] = 0
            app.config.commit()
            # Print saved file path
            print(f"Saved recording to {filename}")
        else:
            # Start recording
            filename = save_directory + get_filename()
            picam2.start_and_record_video(output=filename, config=camera_config, quality=Quality.HIGH)
            record_time = millis()
            # Update camera recording status
            app.config['camera_recording'] = True
            app.config['camera_duration'] = 0
            app.config.commit()
            # Print saved file path
            print(f"Recording to {filename}")
            recording = True
            # Blink LED quickly
            for _ in range(5):
                GPIO.output(led_pin, GPIO.HIGH)
                time.sleep(0.1)
                GPIO.output(led_pin, GPIO.LOW)
                time.sleep(0.1)
            led_state = GPIO.HIGH
        GPIO.output(led_pin, led_state)

    if recording:
        # Slow blink LED
        if (millis() - led_time) >= 1000:
            if led_state == GPIO.HIGH:
                led_state = GPIO.LOW
            else:
                led_state = GPIO.HIGH
            GPIO.output(led_pin, led_state)
            led_time = millis()
        if (millis() - record_time) >= record_length:
            print(f"Recorded for {(millis() - record_time)/(1000*60)} minutes, starting new segment")
            # Stop recording
            picam2.stop_recording()
            filename = save_directory + get_filename()
            # Start recording
            picam2.start_and_record_video(output=filename, config=camera_config, quality=Quality.HIGH)
            record_time = millis()
            # Update camera recording status
            app.config['camera_duration'] += record_length / 60
            app.config.commit()

    # Sleep for a short time to reduce CPU usage
    time.sleep(0.1)

# Clean up GPIO settings when script exits
GPIO.cleanup()