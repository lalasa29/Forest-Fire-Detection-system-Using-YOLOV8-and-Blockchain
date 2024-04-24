from flask import Flask, render_template, Response, request
from werkzeug.utils import secure_filename
from ultralytics import YOLO
import cv2
import cvzone
import math
import os
from send_sms import send_sms


app = Flask(__name__)


model = YOLO('fire.pt')
classnames = ['fire']

processing_paused = False

def detect_fire(frame, confidence_threshold=0.5):
    # Fire detection takes place here
    result = model(frame, stream=True)
    fire_detected = False
    for info in result:
        boxes = info.boxes
        for box in boxes:
            confidence = box.conf[0]
            Class = int(box.cls[0])
            if confidence > confidence_threshold and Class == classnames.index('fire'):
                fire_detected = True
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 5)
                cvzone.putTextRect(frame, f'{classnames[Class]} {confidence*100:.2f}%', [x1 + 8, y1 + 100],
                                   scale=1.5, thickness=2)
    msg = 'Fire detected in your area. Contact local authorities and evacuate.' if fire_detected else 'No fire detected'
    if fire_detected:
        send_sms(msg)
    return frame, fire_detected


def generate_frames(video_path=None):
    global processing_paused
    if video_path:
        cap = cv2.VideoCapture(video_path)
    else:
        cap = cv2.VideoCapture(0)
    while True:
        if not processing_paused:
            success, frame = cap.read()
            if not success:
                break
            else:
                frame, fire_detected = detect_fire(frame)
                ret, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        else:
            while processing_paused:
                frame = cv2.imread('static/pause_screen.jpg')
                ret, buffer = cv2.imencode('.jpg', frame)
                frame_bytes = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html', fire_detected=None)

@app.route('/upload', methods=['POST'])
def upload_file():
    global processing_paused
    if 'file' not in request.files:
        return render_template('index.html', message='No file part', fire_detected=None)
    file = request.files['file']
    if file.filename == '':
        return render_template('index.html', message='No selected file', fire_detected=None)
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join('uploads', filename)
        file.save(file_path)
        processing_paused = False

        
        cap = cv2.VideoCapture(file_path)

        
        while True:
            success, frame = cap.read()
            if not success:
                break
            else:
                detection_result, fire_detected = detect_fire(frame)
                cv2.imwrite(file_path, detection_result)
                return render_template('index.html', message='File uploaded successfully', file_path=file_path, fire_detected=fire_detected)

        cap.release()  



@app.route('/static')
def static_processing():
    return render_template('static.html', fire_detected=None)


@app.route('/live')
def live_processing():
    return render_template('live.html', fire_detected=None)


@app.route('/video_feed')
def video_feed():
    video_path = request.args.get('video_path')
    return Response(generate_frames(video_path), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/pause')
def pause_processing():
    global processing_paused
    processing_paused = not processing_paused
    return 'Processing paused' if processing_paused else 'Processing resumed'


if __name__ == "__main__":
    app.run(debug=True)
