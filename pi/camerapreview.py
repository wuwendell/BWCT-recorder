import io
import json
import RPi.GPIO as GPIO
import threading
import time
from datetime import datetime
from flask import Flask, render_template, Response
from picamera2 import Picamera2
from picamera2.encoders import Quality, H264Encoder, JpegEncoder
from picamera2.outputs import FileOutput, FfmpegOutput
from threading import Condition


app = Flask(__name__)

# Record file variables
recording_directory = "/media/pi/0123-4567/recordings"  # Replace with your recording directory
segment_length = 15 # in minutes

# Device variables
button_pin = 16
led_pin = 26
led_blink_period_fast = 0.1
led_blink_period_slow = 1
led_state = False

# Camera variables
camera = None
camera_cfg = None
recording = False
should_record = False
recording_start = None
encoder = None
output_preview = None
output_record = None

class StreamingOutput(io.BufferedIOBase):
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def write(self, buf):
        with self.condition:
            self.frame = buf
            self.condition.notify_all()

# Generate a filename based on the current time
def generate_filename():
    return f"{recording_directory}/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.mp4"

def preview_gen():
    global output_preview
    while True:
        with output_preview.condition:
                output_preview.condition.wait()
                frame = output_preview.frame
        
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# Thread for camera functions
def recording_thread():
    global recording, should_record, recording_start, segment_length, camera, camera_cfg, led_pin, led_blink_period_fast, led_blink_period_slow, led_state, output_record
    recording = False # Internal recording variable
    segment_start = None
    led_time = 0

    while True:
        if should_record:
            if recording is False:
                # Recording has just started
                camera.start_and_record_video(output=generate_filename(), config=camera_cfg, quality=Quality.HIGH)
                recording_start = time.time()
                segment_start = recording_start
                print("Recording started")
                recording = True
                for i in range(5):
                    GPIO.output(led_pin, GPIO.LOW)
                    time.sleep(led_blink_period_fast)
                    GPIO.output(led_pin, GPIO.HIGH)
                    time.sleep(led_blink_period_fast)

            # Check if it's time to start a new recording segment
            current_time = time.time()
            if (current_time - segment_start) >= (segment_length * 60):
                camera.stop_recording()
                camera.start_and_record_video(output=generate_filename(), config=camera_cfg, quality=Quality.HIGH)
                segment_start = current_time
                print("New recording segment started")
                camera.start_recording(JpegEncoder(), FileOutput(output_preview))
                print("Camera preview started")

            # LED blinking
            if recording and (current_time - led_time) >= led_blink_period_slow:
                led_state = not led_state
                GPIO.output(led_pin, GPIO.HIGH if led_state else GPIO.LOW)
                led_time = current_time
        else:
            if recording:
                # Recording has just stopped
                camera.stop_recording()
                recording = False
                print("Recording stopped")
                camera.start_recording(JpegEncoder(), FileOutput(output_preview))
                print("Camera preview started")
                for i in range(5):
                    GPIO.output(led_pin, GPIO.HIGH)
                    time.sleep(led_blink_period_fast)
                    GPIO.output(led_pin, GPIO.LOW)
                    time.sleep(led_blink_period_fast)

# Function to initialize recording device
def initialize_device():
    global button_pin, led_pin, camera, camera_cfg, output_preview, output_record, encoder
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(led_pin, GPIO.OUT)
    GPIO.output(led_pin, GPIO.LOW)
    print("GPIO initialized")
    camera = Picamera2()
    camera_cfg = camera.create_video_configuration(main={"size": (1280, 720)})
    output_preview = StreamingOutput()
    camera.configure(camera_cfg)
    print("Camera configured")
    camera.start()
    print("Camera started, ready to record")
    camera.start_recording(JpegEncoder(), FileOutput(output_preview))
    print("Camera preview started")

# Start the camera simulation in the background before the first request
@app.before_first_request
def start_camera_simulation():
    threading.Thread(target=recording_thread).start()

@app.route('/')
def index():
    global recording, recording_start
    recording_duration = 0
    if recording_start is not None:
        recording_duration = time.time() - recording_start
    # Render the template with camera and LED status
    return render_template('index.html', recording=recording, recording_duration=recording_duration)

@app.route('/start_record')
def start_record():
    global should_record
    should_record = True
    # Return status code 200 (OK) and current should_record status as JSON
    return json.dumps({'should_record': should_record}), 200, {'ContentType': 'application/json'}


@app.route('/stop_record')
def stop_record():
    global should_record
    should_record = False
    # Return status code 200 (OK) and current should_record status as JSON
    return json.dumps({'should_record': should_record}), 200, {'ContentType': 'application/json'}

@app.route('/status')
def status():
    global recording, recording_start, should_record, segment_length, led_state
    recording_duration = 0
    if recording_start is not None:
        recording_duration = time.time() - recording_start
    # Return device status as JSON
    return json.dumps({'recording': recording, 'recording_duration': recording_duration, 'should_record': should_record, 'led_state': led_state}), 200, {'ContentType': 'application/json'}

@app.route('/preview')
def preview():
    return Response(preview_gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    initialize_device()
    app.run(debug=True, host='0.0.0.0', port=8080, use_reloader=False, threaded=True)
