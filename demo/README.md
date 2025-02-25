# Demo for OpenCV with GPU support

Two demo scripts for comparing OpenCV when it has GPU support, and when it does not.

Pressing the 'e' key will toggle between eye detection.

To run the OpenCV with GPU demo, which assumes that you have a version of OpenCV with GPU enabled for Python:
```
python face_detect_usb_gpu.py
```
For comparison, here's how it runs without using the GPU:
```
python face_detect_usb_fps.py
```