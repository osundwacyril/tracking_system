import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
import sys
from typing import List, Dict
from datetime import datetime

class CameraThread(QThread):
    frame_ready = pyqtSignal(np.ndarray, int)

    def __init__(self, camera_id: int):
        super().__init__()
        self.camera_id = camera_id
        self.running = True

    def run(self):
        cap = cv2.VideoCapture(self.camera_id)
        while self.running:
            ret, frame = cap.read()
            if ret:
                self.frame_ready.emit(frame, self.camera_id)
        cap.release()

    def stop(self):
        self.running = False

class ObjectTracker:
    def __init__(self):
        self.object_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.tracked_objects: Dict[int, List[tuple]] = {}

    def detect_and_track(self, frame: np.ndarray) -> np.ndarray:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        objects = self.object_cascade.detectMultiScale(gray, 1.1, 4)

        for (x, y, w, h) in objects:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            center = (x + w//2, y + h//2)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        return frame

class CameraWidget(QWidget):
    def __init__(self, camera_id: int, tracker: ObjectTracker):
        super().__init__()
        self.camera_id = camera_id
        self.tracker = tracker
        self.layout = QVBoxLayout()
        self.camera_label = QLabel()
        self.layout.addWidget(self.camera_label)
        self.setLayout(self.layout)

        self.camera_thread = CameraThread(camera_id)
        self.camera_thread.frame_ready.connect(self.update_frame)
        self.camera_thread.start()

    def update_frame(self, frame: np.ndarray, camera_id: int):
        if camera_id == self.camera_id:
            processed_frame = self.tracker.detect_and_track(frame)
            height, width, channel = processed_frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(processed_frame.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
            self.camera_label.setPixmap(QPixmap.fromImage(q_image).scaled(
                self.camera_label.width(), self.camera_label.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))

class MultiCameraTracker(QMainWindow):
    def __init__(self, camera_ids: List[int]):
        super().__init__()
        self.setWindowTitle('Multi-Camera Tracking System')
        self.tracker = ObjectTracker()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        for camera_id in camera_ids:
            camera_widget = CameraWidget(camera_id, self.tracker)
            layout.addWidget(camera_widget)

    def closeEvent(self, event):
        for child in self.findChildren(CameraWidget):
            child.camera_thread.stop()
        event.accept()

def main():
    app = QApplication(sys.argv)
    # Use camera IDs 0 and 1 for testing with two cameras
    tracker = MultiCameraTracker([0, 1])
    tracker.resize(1280, 480)
    tracker.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()