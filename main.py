import sys
import os
import subprocess

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QGridLayout
)


class Validator:
    @staticmethod
    def validate_inputs(executable_path, start_time, stop_time):
        if not executable_path:
            return False, "Please select an executable file."

        if not os.path.exists(executable_path):
            return False, "Executable file not found."

        try:
            start_time = int(start_time)
            stop_time = int(stop_time)
        except ValueError:
            return False, "Start time and stop time must be integers."

        if not (0 <= start_time < stop_time < 5):
            return False, "Condition must be: 0 <= start time < stop time < 5"

        return True, "Valid"


class ModelRunner:
    @staticmethod
    def run_model(executable_path, start_time, stop_time):
        command = [
            executable_path,
            "-override",
            f"startTime={start_time},stopTime={stop_time}"
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        return result


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("OpenModelica Launcher")
        self.setGeometry(300, 300, 500, 200)

        self.layout = QGridLayout()

        self.app_label = QLabel("Application to Launch:")
        self.app_input = QLineEdit()
        self.browse_button = QPushButton("Browse")

        self.start_label = QLabel("Start Time:")
        self.start_input = QLineEdit()

        self.stop_label = QLabel("Stop Time:")
        self.stop_input = QLineEdit()

        self.run_button = QPushButton("Run Model")

        self.layout.addWidget(self.app_label, 0, 0)
        self.layout.addWidget(self.app_input, 0, 1)
        self.layout.addWidget(self.browse_button, 0, 2)

        self.layout.addWidget(self.start_label, 1, 0)
        self.layout.addWidget(self.start_input, 1, 1)

        self.layout.addWidget(self.stop_label, 2, 0)
        self.layout.addWidget(self.stop_input, 2, 1)

        self.layout.addWidget(self.run_button, 3, 1)

        self.setLayout(self.layout)

        self.browse_button.clicked.connect(self.select_executable)
        self.run_button.clicked.connect(self.execute_model)

    def select_executable(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Executable",
            "",
            "Executable Files (*.exe)"
        )

        if file_path:
            self.app_input.setText(file_path)

    def execute_model(self):
        executable_path = self.app_input.text().strip()
        start_time = self.start_input.text().strip()
        stop_time = self.stop_input.text().strip()

        is_valid, message = Validator.validate_inputs(
            executable_path,
            start_time,
            stop_time
        )

        if not is_valid:
            QMessageBox.warning(self, "Validation Error", message)
            return

        result = ModelRunner.run_model(
            executable_path,
            start_time,
            stop_time
        )

        if result.returncode == 0:
            QMessageBox.information(
                self,
                "Success",
                "Model executed successfully."
            )
        else:
            QMessageBox.critical(
                self,
                "Execution Failed",
                result.stderr
            )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())