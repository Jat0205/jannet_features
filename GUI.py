import sys
import numpy as np
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
import pyqtgraph as pg

from arduino_DUE_TEC import Newport700C  
from design import Ui_MainWindow  # Assuming the .ui file is converted to design.py
#To convert design.ui: pyuic5 -x design.ui -o design.py


class DataThread(QThread):
    data_signal = pyqtSignal(np.ndarray)

    def __init__(self, instrument, measurement_period):
        super().__init__()
        self.instrument = instrument
        self.measurement_period = measurement_period
        self.running = True

    def run(self):
        time_elapsed = 0.0
        while self.running:
            print("Getting status from instrument")  # Debugging print statement
            try:
                temp, output_frac = self.instrument.get_status()
                print(f"Status: temp={temp}, output_frac={output_frac}")  # Debugging print statement
                setpoint_temp = self.instrument.global_setpoint  
                temp_error = temp - setpoint_temp if temp is not None else None
                new_data = np.array([time_elapsed, temp, output_frac, temp_error])
                self.data_signal.emit(new_data)
                time_elapsed += self.measurement_period
                self.msleep(int(self.measurement_period * 1000))
            except Exception as e:
                print(f"Error in DataThread: {e}")  # Debugging print statement

    def stop(self):
        self.running = False

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.instrument = None
        self.data_thread = None

        # Temperature vs time
        self.plot_widget = pg.PlotWidget(title="Temperature vs Time")
        self.plot_widget.setLabel('left', 'Temperature (C)')
        self.plot_widget.setLabel('bottom', 'Time (s)')
        self.plot_container.layout().addWidget(self.plot_widget)

        # PlotWidget for temperature error
        self.error_plot_widget = pg.PlotWidget(title="Temperature Error vs Time")
        self.error_plot_widget.setLabel('left', 'Temperature Error (C)')
        self.error_plot_widget.setLabel('bottom', 'Time (s)')
        self.error_plot_container.layout().addWidget(self.error_plot_widget)

        # Initialize data arrays for plotting
        self.time_data = []
        self.temp_data = []
        self.output_frac_data = []
        self.error_data = []

        # Initialize plots
        self.temp_plot = self.plot_widget.plot(pen='r', name='Temperature (C)')
        self.output_frac_plot = self.plot_widget.plot(pen='b', name='Output Fraction')
        self.error_plot = self.error_plot_widget.plot(pen='y', name='Temperature Error (C)')

        # Connect buttons to functions
        self.connectButton.clicked.connect(self.connect_to_instrument)
        self.startButton.clicked.connect(self.start_process)
        self.stopButton.clicked.connect(self.stop_process)
        self.clearButton.clicked.connect(self.clear_data)
        self.initializeButton.clicked.connect(self.initialize)
        self.setupButton.clicked.connect(self.setup)
        print("Enter parameters and port, click connect button, and then click start button")

    def connect_to_instrument(self):
        port = self.portLineEdit.text()
        try:
            self.instrument = Newport700C(port=port)
            QMessageBox.information(self, 'Success', f'Connected to Arduino on {port}')
        except Exception as e:
            QMessageBox.critical(self, 'Error', str(e))

    def initialize(self):
        if self.instrument:
            try:
                # You can ping the Arduino by requesting status
                temp, output = self.instrument.get_status()
                QMessageBox.information(self, "Connection", f"Arduino Ready.\nTemp: {temp}\nOutput: {output}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to communicate with Arduino:\n{e}")


    def setup(self):
        if self.instrument:
            try:
                print("Setup process...")
                T_setpoint = int(self.setpointLineEdit.text())
                kp = float(self.kpLineEdit.text())
                ki = float(self.kiLineEdit.text())
                print(f"Parsed values - T_setpoint: {T_setpoint}, Kp: {kp}, Ki: {ki}")  # Debugging print statement
                self.instrument.setup(T_setpoint, kp, ki)
            except ValueError as e:
                print(f"ValueError: {e}")  # Debugging print statement
                QMessageBox.warning(self, 'Warning', 'Invalid numeric input')
            except Exception as e:
                print(f"Exception: {e}")  # Debugging print statement
                QMessageBox.warning(self, 'Warning', f'Unexpected error: {e}')

    def start_process(self):
        if self.instrument and not self.data_thread:
            try:
                print("Starting process...")

                # Get control parameters from the GUI
                T_setpoint = int(self.setpointLineEdit.text())
                kp = float(self.kpLineEdit.text())
                ki = float(self.kiLineEdit.text())
                regulate_TEC0 = 1   

                # Start the instrument with proper arguments
                self.instrument.start(T_setpoint, kp, ki, regulate_TEC0)

                # Start the data thread
                measurement_period = float(self.periodLineEdit.text())
                self.data_thread = DataThread(self.instrument, measurement_period)
                self.data_thread.data_signal.connect(self.update_plot)
                self.data_thread.start()
                print("DataThread started")  # Debugging print statement

            except ValueError as e:
                print(f"ValueError: {e}")
                QMessageBox.warning(self, 'Warning', 'Invalid numeric input')
            except Exception as e:
                print(f"Exception: {e}")
                QMessageBox.warning(self, 'Warning', f'Unexpected error: {e}')

    def stop_process(self):
        if self.data_thread:
            self.data_thread.stop()
            self.data_thread = None

    def clear_data(self):
        self.time_data.clear()
        self.temp_data.clear()
        self.output_frac_data.clear()
        self.temp_plot.setData([], [])
        self.output_frac_plot.setData([], [])


    def update_plot(self, new_data):
        if new_data is None:
            return

        try:
            time, temp, output_frac, temp_error = new_data
            print(f"New data received: {new_data}")  # Debugging print statement

            # Append new data to arrays, ensure data is numeric
            if temp is not None and output_frac is not None:
                self.time_data.append(float(time))
                self.temp_data.append(float(temp))
                self.output_frac_data.append(float(output_frac))
                if temp_error is not None:
                    self.error_data.append(float(temp_error))

                # Update plots
                self.temp_plot.setData(self.time_data, self.temp_data)
                self.output_frac_plot.setData(self.time_data, self.output_frac_data)
                self.error_plot.setData(self.time_data, self.error_data)
            else:
                print("Received None for temperature or output fraction data")
        except ValueError as e:
            print(f"Error updating plot with data {new_data}, Error: {e}")

    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
