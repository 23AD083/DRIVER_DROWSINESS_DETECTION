from flask import Flask, jsonify, render_template, Response
import cv2
import numpy as np
from keras.models import load_model
import os
print("Current working directory:", os.getcwd())
print("Templates directory contents:", os.listdir('templates'))

app = Flask(__name__)

# Load the pre-trained model
new_model = load_model('my_model.h5')

# Load the Haar cascade classifiers for face and eye detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# Video capture for webcam
def generate_frames():
    cap = cv2.VideoCapture(0)  # Use 0 for the default webcam
    if not cap.isOpened():
        raise IOError("Cannot open webcam")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)

        for (x, y, w, h) in faces:
            roi_gray = gray[y:y + h, x:x + w]
            roi_color = frame[y:y + h, x:x + w]

            # Detect eyes in the face region
            eyes = eye_cascade.detectMultiScale(roi_gray, 1.1, 4)
            for (ex, ey, ew, eh) in eyes:
                eyes_roi = roi_color[ey:ey + eh, ex:ex + ew]
                try:
                    # Preprocess the eye ROI for prediction
                    final_image = cv2.resize(eyes_roi, (224, 224))
                    final_image = np.expand_dims(final_image, axis=0)
                    final_image = final_image / 255.0

                    # Predict eye status
                    predictions = new_model.predict(final_image)
                    status = "Open Eyes" if predictions[0][0] > 0.5 else "Closed Eyes"
                except Exception as e:
                    print(f"Error processing eye ROI: {e}")
                    status = "Unknown"

                # Draw rectangles around eyes and put status text
                cv2.rectangle(frame, (x + ex, y + ey), (x + ex + ew, y + ey + eh), (255, 0, 0), 2)
                cv2.putText(frame, status, (x + ex, y + ey - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

            # Draw rectangle around the face
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Encode the frame to JPEG format
        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()

# Routes
@app.route('/')
def index():
    return render_template('index.html')  # Your HTML file

@app.route('/video_feed')
def video_feed():
    global stop_prediction_flag
    stop_prediction_flag = False  # Reset the flag to allow streaming
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stop_prediction', methods=['POST'])
def stop_prediction():
    global stop_prediction_flag
    stop_prediction_flag = True
    return jsonify({'message': 'Prediction stopped successfully!'})

if __name__ == "__main__":
    app.run(debug=True)
