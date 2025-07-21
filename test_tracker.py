import unittest
import cv2
import numpy as np
from tracker import ObjectTracker

class TestObjectTracker(unittest.TestCase):
    def setUp(self):
        self.tracker = ObjectTracker()
        # Create a test image with a face-like rectangle
        self.test_frame = np.zeros((300, 300, 3), dtype=np.uint8)
        cv2.rectangle(self.test_frame, (100, 100), (200, 200), (255, 255, 255), -1)

    def test_tracker_initialization(self):
        """Test if the tracker is properly initialized"""
        self.assertIsNotNone(self.tracker.object_cascade)
        self.assertIsInstance(self.tracker.tracked_objects, dict)

    def test_detect_and_track(self):
        """Test if the detect_and_track method returns a valid frame"""
        processed_frame = self.tracker.detect_and_track(self.test_frame)
        
        # Check if the output is a valid numpy array
        self.assertIsInstance(processed_frame, np.ndarray)
        
        # Check if the output has the same dimensions as input
        self.assertEqual(processed_frame.shape, self.test_frame.shape)

    def test_frame_processing(self):
        """Test if the frame processing maintains correct image properties"""
        processed_frame = self.tracker.detect_and_track(self.test_frame)
        
        # Check if the processed frame maintains the correct data type
        self.assertEqual(processed_frame.dtype, np.uint8)
        
        # Check if the frame dimensions are preserved
        self.assertEqual(len(processed_frame.shape), 3)  # Should be 3D array
        self.assertEqual(processed_frame.shape[2], 3)    # Should have 3 channels

if __name__ == '__main__':
    unittest.main()