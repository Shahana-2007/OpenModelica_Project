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
    QGridLayout,
    QTextEdit,
    QVBoxLayout
)


class Validator:
    """Handles validation of user inputs."""

    @staticmethod
    def validate_inputs(executable_path, start_time, stop_time):
        # Check whether executable path is empty
        if not executable_path:
            return False, "Please select an executable file."

        # Check whether executable file exists
        if not os.path.exists(executable_path):
            return False, "Selected executable file was not found."

        # Check whether selected file is an .exe file
        if not executable_path.endswith(".exe"):
            return False, "Please select a valid .exe file."

        # Convert start and stop time into integers
        try:
            start_time = int(start_time)
            stop_time = int(stop_time)
        except ValueError:
            return False, "Start time and stop time must be integer values."

        # Check negative values
        if start_time < 0 or stop_time < 0:
            return False, "Start time and stop time cannot be negative."

        # Check same values
        if start_time == stop_time:
            return False, "Start time and stop time cannot be the same."

        # Check logical order
        if start_time > stop_time:
            return False, "Start time must be smaller than stop time."

        # Check maximum allowed stop time
        if stop_time >= 5:
            return False, "Stop time must be less than 5."

        # Final validation condition
        if not (0 <= start_time < stop_time < 5):
            return False, "Condition must be: 0 <= start time < stop time < 5"

        return True, "Valid"


class ModelRunner:
    """Runs the selected OpenModelica executable."""

    @staticmethod
    def run_model(executable_path, start_time, stop_time):
        exe_folder = os.path.dirname(executable_path)

        command = [
            executable_path,
            "-override",
            f"startTime={start_time},stopTime={stop_time},tank2.Q1=1"
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                cwd=exe_folder,
                shell=True
            )
            return result

        except Exception as e:
            return None, str(e)


class MainWindow(QWidget):
    """Main GUI window for the OpenModelica launcher."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("OpenModelica Launcher")
        self.setGeometry(300, 200, 800, 500)

        # Apply custom styling
        self.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                color: white;
                font-size: 14px;
                font-family: Segoe UI;
            }

            QLabel {
                font-size: 15px;
                font-weight: bold;
            }

            QLineEdit {
                background-color: #2d2d2d;
                color: white;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 8px;
            }

            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #005fa3;
            }

            QTextEdit {
                background-color: #2d2d2d;
                color: #00ff99;
                border: 1px solid #555;
                border-radius: 6px;
                padding: 8px;
            }
        """)

        main_layout = QVBoxLayout()
        grid_layout = QGridLayout()

        # Executable selection widgets
        self.app_label = QLabel("Application to Launch:")
        self.app_input = QLineEdit()
        self.app_input.setPlaceholderText("Select executable file")

        self.browse_button = QPushButton("Browse")

        # Start time widgets
        self.start_label = QLabel("Start Time:")
        self.start_input = QLineEdit()
        self.start_input.setPlaceholderText("Enter start time")

        # Stop time widgets
        self.stop_label = QLabel("Stop Time:")
        self.stop_input = QLineEdit()
        self.stop_input.setPlaceholderText("Enter stop time")

        # Run button
        self.run_button = QPushButton("Run Model")

        # Output area
        self.output_label = QLabel("Execution Output:")
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)

        # Add widgets to grid layout
        grid_layout.addWidget(self.app_label, 0, 0)
        grid_layout.addWidget(self.app_input, 0, 1)
        grid_layout.addWidget(self.browse_button, 0, 2)

        grid_layout.addWidget(self.start_label, 1, 0)
        grid_layout.addWidget(self.start_input, 1, 1)

        grid_layout.addWidget(self.stop_label, 2, 0)
        grid_layout.addWidget(self.stop_input, 2, 1)

        grid_layout.addWidget(self.run_button, 3, 1)

        main_layout.addLayout(grid_layout)
        main_layout.addWidget(self.output_label)
        main_layout.addWidget(self.output_box)

        self.setLayout(main_layout)

        # Connect button actions
        self.browse_button.clicked.connect(self.select_executable)
        self.run_button.clicked.connect(self.execute_model)

    def select_executable(self):
        """Open file dialog to select executable file."""

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Executable File",
            "",
            "Executable Files (*.exe)"
        )

        if file_path:
            self.app_input.setText(file_path)

    def execute_model(self):
        """Validate inputs and execute the model."""

        executable_path = self.app_input.text()
        start_time = self.start_input.text()
        stop_time = self.stop_input.text()

        # Clear previous output
        self.output_box.clear()

        # Validate user inputs
        is_valid, message = Validator.validate_inputs(
            executable_path,
            start_time,
            stop_time
        )

        if not is_valid:
            QMessageBox.warning(self, "Validation Error", message)
            return

        # Run the executable file
        result = ModelRunner.run_model(
            executable_path,
            start_time,
            stop_time
        )

        if isinstance(result, tuple):
            QMessageBox.critical(
                self,
                "Execution Error",
                result[1]
            )
            return

        # Display execution output
        output_text = ""
        output_text += "Return Code: " + str(result.returncode) + "\n\n"

        if result.stdout:
            output_text += "STDOUT:\n"
            output_text += result.stdout + "\n\n"

        if result.stderr:
            output_text += "STDERR:\n"
            output_text += result.stderr + "\n\n"

        self.output_box.setPlainText(output_text)

        full_output = (result.stdout + result.stderr).lower()

        # Show detailed message boxes
        if result.returncode == 0:
            QMessageBox.information(
                self,
                "Success",
                "Model executed successfully!"
            )
        else:
            if "division by zero" in full_output:
                QMessageBox.critical(
                    self,
                    "Simulation Error",
                    "Simulation failed because division by zero occurred during initialization."
                )

            elif "not found" in full_output:
                QMessageBox.critical(
                    self,
                    "File Error",
                    "Executable file or required model file was not found."
                )

            elif "access is denied" in full_output:
                QMessageBox.critical(
                    self,
                    "Permission Error",
                    "Access denied while trying to execute the file."
                )

            elif "invalid" in full_output:
                QMessageBox.critical(
                    self,
                    "Invalid Input Error",
                    "The model received invalid input values."
                )

            else:
                QMessageBox.warning(
                    self,
                    "Execution Finished with Warning",
                    "Model execution failed or returned warnings. Check the output box for more details."
                )


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

