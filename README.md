# USB-Camera
Code examples for running V4L2 USB Cameras on NVIDIA Jetson Developer Kits

Here are a few examples on how to interface a USB Camera with a Jetson Developer Kit through V4L2 and GStreamer.

"Plug and Play" USB cameras on Linux, such as webcams, use the kernel module _**uvcvideo**_ to interface with the **V**ideo **4** **L**inux subsystem (**V4L2**). Several specialty cameras such as the Stereolabs ZED camera and Intel RealSense cameras also use uvcvideo.

In the Jetson Camera Architecture, you can use V4L2 or GStreamer (which runs on top of V4L2) to interface with such devices. OpenCV is used in these samples to demonstrate how to read the cameras. OpenCV works with multiple camera front ends, including V4L2 and GStreamer. OpenCV is included in the default Jetson software install, and supports V4L2 and GStreamer in the default configuration.

OpenCV is only one way to interface with these interfaces. There are others. For example, here are samples from NVIDIA on how to interface with V4L2 cameras using Input/Output Control (ioctl): [jetson-utils](https://github.com/dusty-nv/jetson-utils)

Many people use OpenCV for the ease of use to open a camera, read frames, and then display the frames without having to worry bout configuring a video capture interface or GUI display interface. 

## Samples
The intent of the samples is to give a minimal sample script to be able to work with a USB camera. You will need to configure the scripts to meet your needs. You will need to assign the correct video address.  /dev/videoX must match your camera address, where X is a number. For example, /dev/video1. 

#### usb-camera-simple.py
usb-camera-simple.py uses the V4L2 backend for OpenCV to interface with the camera (cv2.CAP_V4L2). You can use the V4L2 camera properties to configure the camera. Create the camera first before setting properties. Some properties are only available when integrated properly with OpenCV. For example, even though V4L2 has a fourcc description for H.264 video, the default OpenCV is not compiled with libx264. This means that the video will not be decoded correctly.

To run:
```
$ python3 usb-camera-simple.py
```

#### usb-camera-gst.py
usb-camera-gst.py uses the GStreamer backend for OpenCV to interface with the camera (cv2.CAP_GSTREAMER). You are *not* able to use the V4l2 camera properties when using the GStreamer backend. There is a sample H.264 GStreamer pipeline, (commented out). This has been tested with a [Logitech C920 webcam](https://amzn.to/3qQzKfi).

To run:
```
$ python3 usb-camera-gst.py
```
GStreamer is a very flexible framework, which in practice means there may be some challenges in configuring pipelines for maximum performance. Different cameras may have different results on the same pipelines. 

Note that OpenCV requires a 'BGR' pixel output input. This is usually placed before the appsink element with an associated videoconvert element.

#### face-detect-usb.py
face-detect-usb.py is an example of reading frames and manipulating them in OpenCV. The face and eye detection is performed using Haar cascades. The sample Haar cascades are in the default Jetson distribution. 
To run:
```
$ python3 face-detect-usb.py
```

### OpenCV
The samples use OpenCV to render frames. The standard OpenCV release on the Jetson currently uses GTK+ as its graphic output. Also, OpenCV is compiled here with support for GStreamer and V4L2 Camera input. If you encounter issues and do not have the standard OpenCV installed, check to make sure that these are loaded and selected. 

In Python3, to examine the options that were selected when OpenCV was built:
```
>>> import cv2
>>> print(cv2.getBuildInformation())
```

The GUI sections lists the graphics backend, the Video I/O sections lists the video front ends.

### Tools
A valuable tool for working with V4L2 cameras is v4l2-ctl. To install:
```
$ sudo apt install v4l-utils
```
Useful commands:
#### Return a List of Cameras
```
$ v4l2-ctl --list-devices
```
#### Get Camera Pixel Formats
Get the list of supported pixel formats. /dev/videoX for camera address, e.g.
```
$ v4l2-ctl --list-formats-ext -d /dev/video0
```

#### Get All Information about a Camera
Get the list of supported pixel formats. /dev/videoX for camera address, e.g.
```
$ v4l2-ctl --all -d /dev/video0
```
Lists driver, pixel formats, frame sizes, controls


### canberra-gtk-module
If you see the error:
```
Failed to load module "canberra-gtk-module"
``` 
Generally, this will not cause issues. However, you can remove the error with:
```
$ sudo apt install libcanberra-gtk-module
```

## Release 

### January, 20200
* Initial Release
* JetPack 4.6.1, L4T 32.6.1
* Tested on Jetson Nano and Jetson Xavier NX
* Cameras tested: [Logitech C920 webcam](https://amzn.to/3qQzKfi), Stereolabs ZED, [Intel Realsense D435](https://amzn.to/32ltans)
