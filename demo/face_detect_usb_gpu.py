# MIT License
# Copyright (c) 2019-2025 JetsonHacks (info@jetsonhacks.com)
# Modified for GPU acceleration with CUDA cascades and ROI 

import cv2
import numpy as np
import traceback
import time

window_title = "Face Detect (GPU)"

def face_detect():
    face_cascade_path = "./data/cuda/haarcascade_frontalface_default.xml"
    eye_cascade_path = "./data/cuda/haarcascade_eye.xml"

    # Load Haar cascades and configure for GPU
    try:
        print("Loading face cascade...")
        face_cascade = cv2.cuda_CascadeClassifier.create(face_cascade_path)
        face_cascade.setMinObjectSize((30, 30))
        face_cascade.setScaleFactor(1.3)
        face_cascade.setMinNeighbors(5)
        print("Face cascade loaded successfully.")
    except Exception as e:
        print(f"Error loading face cascade: {str(e)}")
        return

    try:
        print("Loading eye cascade...")
        eye_cascade = cv2.cuda_CascadeClassifier.create(eye_cascade_path)
        eye_cascade.setMinObjectSize((22, 22))
        # eye_cascade.setMaxObjectSize((27, 27))
        eye_cascade.setScaleFactor(1.05)  # Adjusted scale factor
        eye_cascade.setMinNeighbors(4)  # Increased min neighbors to reduce false positives
        print("Eye cascade loaded successfully.")
    except Exception as e:
        print(f"Error loading eye cascade: {str(e)}")
        return

    # Verify GPU availability
    if cv2.cuda.getCudaEnabledDeviceCount() == 0:
        print("Error: No CUDA-enabled GPU detected.")
        return

    # Initialize video capture (V4L2 backend)
    camera_id = "/dev/video0"
    try:
        video_capture = cv2.VideoCapture(camera_id, cv2.CAP_V4L2)
        video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        video_capture.set(cv2.CAP_PROP_FPS, 30)
        if not video_capture.isOpened():
            raise RuntimeError("Unable to open camera")
        print("Video capture initialized.")
    except Exception as e:
        print(f"Error initializing video capture: {str(e)}")
        traceback.print_exc()
        return

    try:
        cv2.namedWindow(window_title, cv2.WINDOW_AUTOSIZE)
        prev_time = time.time()
        frame_count = 0
        fps = 0

        total_face_detection_time = 0
        total_eye_detection_time = 0
        total_frames = 0
        fps = 0 

        eye_detection_enabled = True

        while True:
            start_time = time.time()
            ret, frame = video_capture.read()
            if not ret:
                print("Failed to grab frame")
                break

            # Upload frame to GPU
            gpu_frame = cv2.cuda_GpuMat()
            gpu_frame.upload(frame)

            # Convert to grayscale on GPU
            gpu_gray = cv2.cuda.cvtColor(gpu_frame, cv2.COLOR_BGR2GRAY)

            # Detect faces on GPU
            face_start_time = time.time()
            faces_gpu = face_cascade.detectMultiScale(gpu_gray)
            face_end_time = time.time()
            faces = faces_gpu.download()[0] if faces_gpu.size()[1] > 0 else np.array([])

            frame_cpu = gpu_frame.download()

            # Process detected faces
            for (x, y, w, h) in faces:
                cv2.rectangle(frame_cpu, (x, y), (x + w, y + h), (255, 0, 0), 2)

                if eye_detection_enabled:
                    # Extract ROI for eyes
                    gpu_gray_roi = gpu_gray.colRange(x, x + w).rowRange(y, y + h)
                    roi_gray_gpu = cv2.cuda_GpuMat(gpu_gray_roi.size(), gpu_gray_roi.type())
                    gpu_gray_roi.copyTo(roi_gray_gpu)

                    roi_color_cpu = frame_cpu[y:y + h, x:x + w]

                    # Detect eyes in ROI on GPU
                    eye_start_time = time.time()
                    try:
                        eyes_gpu = eye_cascade.detectMultiScale(roi_gray_gpu)
                        eyes = eyes_gpu.download()[0] if eyes_gpu.size()[1] > 0 else np.array([])
                    except Exception as e:
                        print(f"Error detecting eyes: {str(e)}")
                        traceback.print_exc()
                        eyes = np.array([])
                    eye_end_time = time.time()

                    # Filter detected eyes based on size and position
                    filtered_eyes = []
                    for (ex, ey, ew, eh) in eyes:
                        if ew > 15 and eh > 15:  # Filter based on size
                            filtered_eyes.append((ex, ey, ew, eh))

                    for (ex, ey, ew, eh) in filtered_eyes:
                        cv2.rectangle(roi_color_cpu, (ex, ey), (ex + ew, ey + eh), (0, 255, 0), 2)

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
            overlay = frame_cpu.copy()
            text_background_color = (0, 0, 0)  # Black background
            text_color = (255, 255, 255)  # White text
            cv2.rectangle(overlay, (4, 4), (340, 80), text_background_color, -1)
            alpha = 0.4  # Opacity factor

            # Blend the overlay with the original frame
            cv2.addWeighted(overlay, alpha, frame_cpu, 1 - alpha, 0, frame_cpu)

            cv2.putText(frame_cpu, fps_text, (10, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)
            cv2.putText(frame_cpu, face_detection_time_text, (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)
            cv2.putText(frame_cpu, eye_detection_time_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, text_color, 2)

            if cv2.getWindowProperty(window_title, cv2.WND_PROP_AUTOSIZE) >= 0:
                cv2.imshow(window_title, frame_cpu)
            else:
                break

            keyCode = cv2.waitKey(30) & 0xFF
            if keyCode == 27 or keyCode == ord('q'):
                break
            elif keyCode == ord('e'):
                eye_detection_enabled = not eye_detection_enabled

    except Exception as e:
        print(f"Unexpected error in main loop: {str(e)}")
        traceback.print_exc()
    finally:
        if video_capture is not None and video_capture.isOpened():
            video_capture.release()
        cv2.destroyAllWindows()
        print("Resources cleaned up.")

        # Print average FPS and detection times
        if total_frames > 0:
            avg_fps = fps
            avg_face_detection_time = total_face_detection_time / total_frames
            avg_eye_detection_time = total_eye_detection_time / total_frames if eye_detection_enabled else 0
            print(f"Average FPS: {avg_fps:.2f}")
            print(f"Average Face Detection Time: {avg_face_detection_time:.2f} ms")
            if eye_detection_enabled:
                print(f"Average Eye Detection Time: {avg_eye_detection_time:.2f} ms")

if __name__ == "__main__":
    face_detect()