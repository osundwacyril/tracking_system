import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
import sys
from typing import List, Dict
from datetime import datetime
import multiprocessing as mp
from queue import Empty

class CameraProcess(mp.Process):
    def __init__(self, camera_id: int, frame_queue: mp.Queue, stop_event: mp.Event):
        super().__init__()
        self.camera_id = camera_id
        self.frame_queue = frame_queue
        self.stop_event = stop_event
        self.object_cascade = None

    def detect_objects(self, frame):
        if self.object_cascade is None:
            self.object_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        objects = self.object_cascade.detectMultiScale(gray, 1.1, 4)
        
        for (x, y, w, h) in objects:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            cv2.putText(frame, timestamp, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        return frame

    def run(self):
        cap = cv2.VideoCapture(self.camera_id)
        while not self.stop_event.is_set():
            ret, frame = cap.read()
            if ret:
                processed_frame = self.detect_objects(frame)
                self.frame_queue.put((self.camera_id, processed_frame))
        cap.release()

class FrameReceiver(QThread):
    frame_ready = pyqtSignal(np.ndarray, int)

    def __init__(self, frame_queue: mp.Queue, stop_event: mp.Event):
        super().__init__()
        self.frame_queue = frame_queue
        self.stop_event = stop_event

    def run(self):
        while not self.stop_event.is_set():
            try:
                camera_id, frame = self.frame_queue.get(timeout=1)
                self.frame_ready.emit(frame, camera_id)
            except Empty:
                continue

class CameraWidget(QWidget):
    def __init__(self, camera_id: int):
        super().__init__()
        self.camera_id = camera_id
        self.layout = QVBoxLayout()
        self.camera_label = QLabel()
        self.layout.addWidget(self.camera_label)
        self.setLayout(self.layout)

    def update_frame(self, frame: np.ndarray, camera_id: int):
        if camera_id == self.camera_id:
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_image = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
            self.camera_label.setPixmap(QPixmap.fromImage(q_image).scaled(
                self.camera_label.width(), self.camera_label.height(),
                Qt.KeepAspectRatio, Qt.SmoothTransformation
            ))

class MultiCameraTracker(QMainWindow):
    def __init__(self, camera_ids: List[int]):
        super().__init__()
        self.setWindowTitle('Multi-Camera Tracking System')
        
        # Multiprocessing setup
        self.frame_queue = mp.Queue()
        self.stop_event = mp.Event()
        self.camera_processes = []
        
        # GUI setup
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        
        # Create camera widgets and processes
        for camera_id in camera_ids:
            camera_widget = CameraWidget(camera_id)
            layout.addWidget(camera_widget)
            
            # Create and start camera process
            camera_process = CameraProcess(camera_id, self.frame_queue, self.stop_event)
            camera_process.start()
            self.camera_processes.append(camera_process)
        
        # Start frame receiver
        self.frame_receiver = FrameReceiver(self.frame_queue, self.stop_event)
        self.frame_receiver.frame_ready.connect(self.update_all_widgets)
        self.frame_receiver.start()

    def update_all_widgets(self, frame: np.ndarray, camera_id: int):
        for widget in self.findChildren(CameraWidget):
            widget.update_frame(frame, camera_id)

    def closeEvent(self, event):
        self.stop_event.set()
        for process in self.camera_processes:
            process.join()
        self.frame_receiver.wait()
        event.accept()

def main():
    # Required for Windows support
    mp.freeze_support()
    
    app = QApplication(sys.argv)
    # Use camera IDs 0 and 1 for testing with two cameras
    tracker = MultiCameraTracker([0, 1])
    tracker.resize(1280, 480)
    tracker.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()