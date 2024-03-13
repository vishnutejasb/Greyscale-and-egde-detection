import sys
import cv2
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QButtonGroup
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap


class VideoProcessor(QWidget):
    def __init__(self):
        super().__init__()
        self.video_capture = cv2.VideoCapture(0)  # Change to specify video file

        self.gray_image_label = QLabel()
        self.edges_image_label = QLabel()

        self.start_stop_button = QPushButton('Start')

        self.threshold_buttons = QButtonGroup()
        self.threshold_buttons.buttonClicked[int].connect(self.set_threshold)
        self.threshold_labels = []

        self.threshold = 127  # Default threshold value

        self.exit_label = QLabel("Press 'q' to exit")
        self.exit_label.setAlignment(Qt.AlignCenter)

        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("<h1>Grayscale Output</h1>"))
        left_layout.addWidget(self.gray_image_label)

        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("<h1>Edge Detection</h1>"))
        right_layout.addWidget(self.edges_image_label)

        layout.addLayout(left_layout)
        layout.addLayout(right_layout)

        control_layout = QVBoxLayout()
        control_layout.addWidget(self.start_stop_button)
        control_layout.addWidget(QLabel("<b>Threshold Levels</b>"))

        for i in range(1, 11):
            button = QPushButton(f"Level {i}")
            button.setProperty("level", i)

            def val(level):
                thresholds = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900]
                return thresholds[level - 1]

            def create_lambda(level):
                threshold_value = val(level)
                return lambda: (print("Threshold value:", threshold_value), self.set_threshold(threshold_value))

            button.clicked.connect(create_lambda(i))
            self.threshold_buttons.addButton(button, i)
            control_layout.addWidget(button)
            label = QLabel()
            self.threshold_labels.append(label)
            control_layout.addWidget(label)

        control_layout.addWidget(self.exit_label)
        layout.addLayout(control_layout)

        self.setLayout(layout)

        self.start_stop_button.clicked.connect(self.toggle_video)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # Update frame every 30 milliseconds

    def toggle_video(self):
        if self.timer.isActive():
            self.timer.stop()
            self.start_stop_button.setText('Start')
        else:
            self.timer.start(30)
            self.start_stop_button.setText('Stop')

    def update_frame(self):
        ret, frame = self.video_capture.read()
        if ret:
            gray_frame, edges_frame = self.process_frame(frame)
            self.display_frame(gray_frame, self.gray_image_label)
            self.display_frame(edges_frame, self.edges_image_label)

    def process_frame(self, frame):
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, binary_frame = cv2.threshold(gray_frame, self.threshold, 255, cv2.THRESH_BINARY)
        edges = cv2.Canny(gray_frame, 100, 200)  # Perform Canny edge detection
        return gray_frame, edges

    def set_threshold(self, value):
        if isinstance(value, int):
            self.threshold = value
            for i in range(10):
                if i + 1 == value:
                    self.threshold_labels[i].setText("<b>Threshold:</b> " + str(self.threshold))
                else:
                    self.threshold_labels[i].setText("")

    def display_frame(self, frame, label):
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        label.setPixmap(pixmap)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            self.close()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VideoProcessor()
    window.setWindowTitle('Vyorius Test - Image Display and Processing')
    window.show()
    sys.exit(app.exec_())
