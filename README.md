# Multi-Camera Tracking System

A real-time multi-camera tracking system implemented in Python using OpenCV and PyQt5. The system can simultaneously process video feeds from multiple cameras and perform object detection and tracking.

## Features

- Real-time video processing from multiple cameras
- Object detection and tracking using Haar Cascade Classifier
- Modern GUI interface built with PyQt5
- Timestamp overlay on video feeds
- Scalable to handle multiple camera inputs

## Requirements

- Python 3.7+
- OpenCV
- PyQt5
- NumPy
- imutils

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd tracking_system
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

Run the tracking system:
```bash
python tracker.py
```

By default, the system will try to use cameras with IDs 0 and 1. You can modify the camera IDs in the `main()` function of `tracker.py`.

## System Architecture

- `CameraThread`: Handles video capture from individual cameras in separate threads
- `ObjectTracker`: Implements object detection and tracking logic
- `CameraWidget`: PyQt5 widget for displaying individual camera feeds
- `MultiCameraTracker`: Main application window managing multiple camera widgets

## Customization

You can customize the tracking system by:
- Modifying the detection parameters in the `ObjectTracker` class
- Adding different object detection models
- Adjusting the GUI layout and appearance
- Implementing additional tracking features

## License

This project is licensed under the MIT License - see the LICENSE file for details.