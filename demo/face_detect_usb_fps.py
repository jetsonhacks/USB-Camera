# MIT License
# Copyright (c) 2019-2025 JetsonHacks (info@jetsonhacks.com)
# See LICENSE for OpenCV license and additional information

# https://docs.opencv.org/3.3.1/d7/d8b/tutorial_py_face_detection.html
# On the Jetson Nano, OpenCV comes preinstalled
# Data files are in /usr/sharc/OpenCV

import cv2
import time

window_title = "Face Detect"

def face_detect():
    face_cascade = cv2.CascadeClassifier(
        "/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml"
    )
    eye_cascade = cv2.CascadeClassifier(
        "/usr/share/opencv4/haarcascades/haarcascade_eye.xml"
    )
    # ASSIGN CAMERA ADDRESS HERE
    camera_id = "/dev/video0"
    # Full list of Video Capture APIs (video backends): https://docs.opencv.org/3.4/d4/d15/group__videoio__flags__base.html
    # For webcams, we use V4L2
    video_capture = cv2.VideoCapture(camera_id, cv2.CAP_V4L2)
    # Select frame size, FPS:
    video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    video_capture.set(cv2.CAP_PROP_FPS, 30)

    if video_capture.isOpened():
        try:
            cv2.namedWindow(window_title, cv2.WINDOW_AUTOSIZE)
            prev_time = time.time()
            frame_count = 0
            fps = 0

            total_face_detection_time = 0
            total_eye_detection_time = 0
            total_frames = 0

            eye_detection_enabled = True

            while True:
                start_time = time.time()
                ret, frame = video_capture.read()
                if not ret:
                    print("Failed to grab frame")
                    break

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Detect faces
                face_start_time = time.time()
                faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                face_end_time = time.time()

                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                    roi_gray = gray[y : y + h, x : x + w]
                    roi_color = frame[y : y + h, x : x + w]

                    if eye_detection_enabled:
                        # Detect eyes
                        eye_start_time = time.time()
                        eyes = eye_cascade.detectMultiScale(roi_gray)
                        eye_end_time = time.time()

                        for (ex, ey, ew, eh) in eyes:
                            cv2.rectangle(
                                roi_color, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2
                            )

                        # Accumulate eye detection time
                        total_eye_detection_time += (eye_end_time - eye_start_time) * 1000

                # Calculate FPS
                frame_count += 1
                current_time = time.time()
                elapsed_time = current_time - prev_time
                if elapsed_time >= 1.0:
                    fps = frame_count / elapsed_time
                    prev_time = current_time
                    frame_count = 0

                # Accumulate face detection time
                total_face_detection_time += (face_end_time - face_start_time) * 1000
                total_frames += 1

                # Display FPS and detection times
                fps_text = f"FPS: {fps:.2f}"
                face_detection_time_text = f"Face Detection Time: {(face_end_time - face_start_time) * 1000:.2f} ms"
                eye_detection_time_text = f"Eye Detection Time: {(eye_end_time - eye_start_time) * 1000:.2f} ms" if eye_detection_enabled else "Eye Detection: Disabled"

                # Add semi-transparent background rectangle for text
                overlay = frame.copy()
                text_background_color = (0, 0, 0)  # Black background
                text_color = (192, 192, 192)  # White text
                cv2.rectangle(overlay, (4, 4), (340, 80), text_background_color, -1)
                alpha = 0.6  # Opacity factor

                # Blend the overlay with the original frame
                cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

                cv2.putText(frame, fps_text, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)
                cv2.putText(frame, face_detection_time_text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)
                cv2.putText(frame, eye_detection_time_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)

                # Check to see if the user closed the window
                # Under GTK+, WND_PROP_VISIBLE does not work correctly. Under Qt it does
                # GTK - Substitute WND_PROP_AUTOSIZE to detect if window has been closed by user
                if cv2.getWindowProperty(window_title, cv2.WND_PROP_AUTOSIZE) >= 0:
                    cv2.imshow(window_title, frame)
                else:
                    break
                
                keyCode = cv2.waitKey(30) & 0xFF
                # Stop the program on the ESC key or 'q'
                if keyCode == 27 or keyCode == ord('q'):
                    break
                elif keyCode == ord('e'):
                    eye_detection_enabled = not eye_detection_enabled
        finally:
            video_capture.release()
            cv2.destroyAllWindows()

            # Print average FPS and detection times
            if total_frames > 0:
                avg_fps = fps
                avg_face_detection_time = total_face_detection_time / total_frames
                avg_eye_detection_time = total_eye_detection_time / total_frames if eye_detection_enabled else 0
                print(f"Average FPS: {avg_fps:.2f}")
                print(f"Average Face Detection Time: {avg_face_detection_time:.2f} ms")
                if eye_detection_enabled:
                    print(f"Average Eye Detection Time: {avg_eye_detection_time:.2f} ms")
    else:
        print("Unable to open camera")


if __name__ == "__main__":
    face_detect()