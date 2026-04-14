import sys
import os
import matplotlib.pyplot as plt

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QListWidget, QVBoxLayout, QHBoxLayout, QComboBox,
    QSpinBox, QFileDialog, QMessageBox, QDialog,
    QTableWidget, QTableWidgetItem, QDialogButtonBox,
    QAbstractItemView, QDoubleSpinBox, QFormLayout
)

# File import from my own
from decomp_stand import DecompDataSet
from raman import RamanDataSet
from fitters import SpectralFitter
from Exporter import ResultExporter


# Class 1
# Custom widget that allows the user to select files, rename them for plotting
# and allows easy and simple access later
class FileNamingDialog(QDialog):
    def __init__(self, filepaths, title="Name Files", parent=None):
        super().__init__(parent)

        self.setWindowTitle(title)
        self.filepaths = filepaths

        layout = QVBoxLayout()

        instruction_label = QLabel("Edit the display name for each selected file.")
        layout.addWidget(instruction_label)

        self.table = QTableWidget()
        self.table.setRowCount(len(filepaths))
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Filename", "Display Name"])
        self.table.setEditTriggers(
            QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked
        )

        for row, path in enumerate(filepaths):
            filename = os.path.basename(path)
            default_name = os.path.splitext(filename)[0]

            filename_item = QTableWidgetItem(filename)
            filename_item.setFlags(filename_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, filename_item)

            name_item = QTableWidgetItem(default_name)
            self.table.setItem(row, 1, name_item)

        self.table.resizeColumnsToContents()
        layout.addWidget(self.table)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_named_files(self):
        named_files = []

        for row, path in enumerate(self.filepaths):
            name_item = self.table.item(row, 1)
            display_name = "" if name_item is None else name_item.text().strip()

            if not display_name:
                raise ValueError(
                    f"File '{os.path.basename(path)}' is missing a display name."
                )

            named_files.append({
                "name": display_name,
                "path": path
            })

        return named_files
    
class AnalysisResultsDialog(QDialog):
    def __init__(self, mode, results, grain_metrics=None, parent=None):
        super().__init__(parent)

        self.setWindowTitle(f"{mode} Analysis Results")
        self.resize(900, 400)

        layout = QVBoxLayout()

        title = QLabel(f"{mode} fitted results")
        layout.addWidget(title)

        grain_map = {}
        if grain_metrics:
            grain_map = {
                item["filepath"]: item["grain_size_metric"]
                for item in grain_metrics
            }

        # Build headers
        base_headers = ["File"]

        max_peaks = 0
        for result in results:
            area_list = result.get("area_list", [])
            if len(area_list) > max_peaks:
                max_peaks = len(area_list)

        peak_headers = [f"Peak Area {i+1}" for i in range(max_peaks)]

        if mode == "Raman":
            headers = base_headers + ["Grain Size Metric"] + peak_headers
        else:
            headers = base_headers + peak_headers

        self.table = QTableWidget()
        self.table.setRowCount(len(results))
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        for row, result in enumerate(results):
            filepath = result.get("filepath", "")
            filename = os.path.basename(filepath)

            file_item = QTableWidgetItem(filename)
            file_item.setFlags(file_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, file_item)

            col_offset = 1

            if mode == "Raman":
                grain_value = grain_map.get(filepath, None)
                grain_text = "Not found" if grain_value is None else f"{grain_value:.4f}"
                grain_item = QTableWidgetItem(grain_text)
                grain_item.setFlags(grain_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, 1, grain_item)
                col_offset = 2

            area_list = result.get("area_list", [])

            for i in range(max_peaks):
                if i < len(area_list):
                    value_text = f"{area_list[i]:.4f}"
                else:
                    value_text = ""

                area_item = QTableWidgetItem(value_text)
                area_item.setFlags(area_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, col_offset + i, area_item)

        self.table.resizeColumnsToContents()
        layout.addWidget(self.table)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)

        self.setLayout(layout)
    
class GrainMetricDialog(QDialog):
    def __init__(self, grain_metrics, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Raman Grain Size Metrics")
        self.resize(500, 300)

        layout = QVBoxLayout()

        title = QLabel("Calculated Raman grain size metric values")
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setRowCount(len(grain_metrics))
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["File", "Grain Size Metric"])

        for row, item in enumerate(grain_metrics):
            filepath = item["filepath"]
            value = item["grain_size_metric"]

            file_item = QTableWidgetItem(os.path.basename(filepath))

            if value is None:
                value_text = "Not found"
            else:
                value_text = f"{value:.4f}"

            value_item = QTableWidgetItem(value_text)

            file_item.setFlags(file_item.flags() & ~Qt.ItemIsEditable)
            value_item.setFlags(value_item.flags() & ~Qt.ItemIsEditable)

            self.table.setItem(row, 0, file_item)
            self.table.setItem(row, 1, value_item)

        self.table.resizeColumnsToContents()
        layout.addWidget(self.table)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)

        self.setLayout(layout)

class FitParameterDialog(QDialog):
    def __init__(self, mode="Raman", parent=None):
        super().__init__(parent)

        self.mode = mode
        self.setWindowTitle(f"{mode} Fit Parameters")

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        # Common fields
        self.lower_spin = QDoubleSpinBox()
        self.lower_spin.setDecimals(2)
        self.lower_spin.setRange(-1e9, 1e9)

        self.upper_spin = QDoubleSpinBox()
        self.upper_spin.setDecimals(2)
        self.upper_spin.setRange(-1e9, 1e9)

        # convinient defualt options from experience
        if mode == "Raman":
            self.lower_spin.setValue(1200)
            self.upper_spin.setValue(1700)
        else:
            self.lower_spin.setValue(550)
            self.upper_spin.setValue(800)

        form_layout.addRow("Lower bound:", self.lower_spin)
        form_layout.addRow("Upper bound:", self.upper_spin)

        # Raman-only field
        self.peak_spin = None
        if mode == "Raman":
            self.peak_spin = QSpinBox()
            self.peak_spin.setMinimum(1)
            self.peak_spin.setMaximum(20)
            self.peak_spin.setValue(2)
            form_layout.addRow("Number of Lorentzian peaks:", self.peak_spin)

        layout.addLayout(form_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def validate_and_accept(self):
        if self.lower_spin.value() >= self.upper_spin.value():
            QMessageBox.warning(
                self,
                "Invalid Range",
                "Lower bound must be smaller than upper bound."
            )
            return

        self.accept()

    def get_values(self):
        values = {
            "rangelb": self.lower_spin.value(),
            "rangehb": self.upper_spin.value()
        }

        if self.mode == "Raman":
            values["n_peaks"] = self.peak_spin.value()

        return values

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Data Analysis APP")

        # current folder for data
        self.data_dir = os.path.abspath("../data")

        # store datasets/fitter objects on the window so the app remembers state
        self.dataset = None
        self.fitter = None
        self.mode = "Raman"

        self.measurement_files = []
        self.standard_files = []
        self.raman_files = []
        self.grain_metrics = []

        # ---------- central widget ----------
        central = QWidget()
        self.setCentralWidget(central)

        # ---------- widgets ----------
        self.title_label = QLabel("MAKE THINGS EASY TOOLS")

        self.mode_label = QLabel("Analysis mode:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["Raman", "Decomposition"])

        self.load_button = QPushButton("Load Files")
        self.fit_button = QPushButton("Run Fit")
        self.plot_fits_button = QPushButton("Plot Fits")
        self.plot_percentages_button = QPushButton("Plot Percentages")
        self.raw_button = QPushButton("Plot Raw Data")
        self.clear_button = QPushButton("Clear")
        self.save_results_button = QPushButton("Save Results")

        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("color: red;")
        self.file_list = QListWidget()

        # ---------- layout ----------
        main_layout = QVBoxLayout()
        controls_row = QHBoxLayout()
        fit_row = QHBoxLayout()
        plot_row = QHBoxLayout()

        controls_row.addWidget(self.mode_label)
        controls_row.addWidget(self.mode_combo)
        controls_row.addWidget(self.mode_label)
        controls_row.addWidget(self.mode_combo)
        controls_row.addWidget(self.clear_button)

        fit_row.addWidget(self.load_button)
        fit_row.addWidget(self.fit_button)
        fit_row.addWidget(self.load_button)
        fit_row.addWidget(self.fit_button)
        fit_row.addWidget(self.save_results_button)

        plot_row.addWidget(self.raw_button)
        plot_row.addWidget(self.plot_fits_button)
        plot_row.addWidget(self.plot_percentages_button)

        main_layout.addWidget(self.title_label)
        main_layout.addLayout(controls_row)
        main_layout.addLayout(fit_row)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(QLabel("Loaded files:"))
        main_layout.addWidget(self.file_list)
        main_layout.addLayout(plot_row)
        
        central.setLayout(main_layout)

        # ---------- signals / slots ----------
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        self.load_button.clicked.connect(self.select_files)
        self.fit_button.clicked.connect(self.run_fit)
        self.plot_fits_button.clicked.connect(self.plot_fits)
        self.plot_percentages_button.clicked.connect(self.plot_percentages)
        self.raw_button.clicked.connect(self.plot_raw_data)
        self.clear_button.clicked.connect(self.clear_all)
        self.save_results_button.clicked.connect(self.save_results)

        # At the start, these buttons are disabled
        self.raw_button.setEnabled(False)
        self.plot_fits_button.setEnabled(False)
        self.plot_percentages_button.setEnabled(False)
        self.save_results_button.setEnabled(False)

        # initialize UI state
        self.on_mode_changed(self.mode_combo.currentText())

    def clear_all(self):
        reply = QMessageBox.question(
            self,
            "Confirm Clear",
            "Are you sure you want to clear all data?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.reset_state_for_new_selection()
            self.status_label.setText("Status: Cleared all data")
        
        self.raw_button.setEnabled(False)
        self.plot_fits_button.setEnabled(False)
        self.plot_percentages_button.setEnabled(False)
        self.save_results_button.setEnabled(False)

    def save_results(self):
        if self.dataset is None or not getattr(self.dataset, "results", None):
            QMessageBox.warning(self, "No Results", "Run a fit before saving results.")
            return

        folder = QFileDialog.getExistingDirectory(
            self,
            "Choose Folder to Save Results"
        )

        if not folder:
            self.status_label.setText("Status: Save cancelled")
            return

        try:
            exporter = ResultExporter(
                dataset=self.dataset,
                mode=self.mode,
                grain_metrics=self.grain_metrics if self.mode == "Raman" else None
            )

            output = exporter.export_all(folder)

            self.status_label.setText("Status: Results saved successfully")

            QMessageBox.information(
                self,
                "Save Complete",
                "Results were saved successfully.\n\n"
                f"Summary Excel:\n{output['summary_excel']}\n\n"
                f"Raw Data Excel:\n{output['raw_excel']}\n\n"
                f"Figures saved: {len(output['figures'])}"
            )

        except Exception as e:
            QMessageBox.critical(self, "Save Error", str(e))
            self.status_label.setText("Status: Save failed")

    def get_named_file_selection(self, title):
        filepaths, _ = QFileDialog.getOpenFileNames(
            self,
            title,
            self.data_dir,
            "Data Files (*.txt *.dat *.csv *.xlsx *.xls)"
        )

        if not filepaths:
            return None

        dialog = FileNamingDialog(filepaths, title=f"Rename Files: {title}", parent=self)

        if dialog.exec_() != QDialog.Accepted:
            return None

        return dialog.get_named_files()

    def reset_state_for_new_selection(self):
        self.dataset = None
        self.fitter = None
        self.measurement_files = []
        self.standard_files = []
        self.raman_files = []
        self.grain_metrics = []
        self.file_list.clear()
        self.fit_button.setEnabled(True)
        self.raw_button.setEnabled(False)
        self.plot_fits_button.setEnabled(False)
        self.plot_percentages_button.setEnabled(False)
        self.save_results_button.setEnabled(False)

    # Switch analysis modes
    # connected to self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
    # text is the selected mode
    def on_mode_changed(self, text):
        # If raman, controls enabled 
        # Not raman, controls disabled
        # Raman for sure uses lorenzian peak fitting so set the controls to be on
        self.mode = text

        # Clear and delete the current self values
        # To ensure picking the correct values
        self.file_list.clear()
        self.dataset = None
        self.fitter = None
        self.grain_metrics = []
        self.raw_button.setEnabled(False)
        self.plot_fits_button.setEnabled(False)
        self.plot_percentages_button.setEnabled(False)
        self.save_results_button.setEnabled(False)
        # Give feedback to the user
        self._update_status(f"Status: Mode set to {self.mode}")

    def run_fit(self):
        if self.dataset is None or self.fitter is None:
            QMessageBox.warning(self, "No Data", "Select files first.")
            return

        try:
            # Open parameter dialog
            dialog = FitParameterDialog(mode=self.mode, parent=self)

            if dialog.exec_() != QDialog.Accepted:
                self.status_label.setText("Status: Fit cancelled")
                return

            params = dialog.get_values()

            if self.mode == "Raman":
                n_peaks = params["n_peaks"]
                rangelb = params["rangelb"]
                rangehb = params["rangehb"]

                self.dataset.fit(
                    self.fitter,
                    n_peaks=n_peaks,
                    rangelb=rangelb,
                    rangehb=rangehb
                )

                # Attach peak areas if not already present
                if hasattr(self.dataset, "attach_peak_areas_to_results"):
                    self.dataset.attach_peak_areas_to_results()

                self.grain_metrics = self.dataset.calculate_grain_size_metric()

                self.status_label.setText(
                    f"Status: Raman fit complete | peaks={n_peaks}, "
                    f"range=({rangelb}, {rangehb})"
                )
            else:
                rangelb = params["rangelb"]
                rangehb = params["rangehb"]

                self.dataset.fit(
                    self.fitter,
                    rangelb=rangelb,
                    rangehb=rangehb
                )

                if hasattr(self.dataset, "attach_peak_areas_to_results"):
                    self.dataset.attach_peak_areas_to_results()

                self.grain_metrics = []

                self.status_label.setText(
                    f"Status: Decomposition fit complete | "
                    f"range=({rangelb}, {rangehb})"
                )
                
            # disable fit after successful run
            self.fit_button.setEnabled(False)
            self.plot_fits_button.setEnabled(True)
            self.plot_percentages_button.setEnabled(True)
            self.save_results_button.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "Fit Error", str(e))
            self.status_label.setText("Status: Fit failed")

     # LOAD THE FILES (No more hard coding yay)
     # Load the file -> preparing the dataset -> initializing a fitter -> updating the GUI
    def select_files(self):
        try:
            self.reset_state_for_new_selection()

            if self.mode == "Raman":
                named_files = self.get_named_file_selection("Select Raman Data Files")

                if not named_files:
                    self.status_label.setText("Status: No Raman files selected")
                    return

                self.raman_files = named_files

                raman_paths = [item["path"] for item in self.raman_files]

                self.dataset = RamanDataSet(raman_paths)
                self.dataset.load_all()
                self.fitter = SpectralFitter()

                # attach display names to loaded dataset items
                for i, item in enumerate(self.dataset.data):
                    item["name"] = self.raman_files[i]["name"]

                for item in self.raman_files:
                    self.file_list.addItem(f'{item["name"]}: {item["path"]}')

                self.status_label.setText(
                    f"Status: Loaded {len(self.raman_files)} Raman files"
                )

            else:
                named_measurements = self.get_named_file_selection("Select Decomposition Measurement Files")

                if not named_measurements:
                    self.status_label.setText("Status: No measurement files selected")
                    return

                named_standards = self.get_named_file_selection("Select Standard Files")

                if not named_standards:
                    self.status_label.setText("Status: No standard files selected")
                    return

                self.measurement_files = named_measurements
                self.standard_files = named_standards

                measurement_paths = [item["path"] for item in self.measurement_files]

                # fitter still expects (label, path)
                standard_label_path_pairs = [
                    (item["name"], item["path"]) for item in self.standard_files
                ]

                self.dataset = DecompDataSet(measurement_paths)
                self.dataset.load_all()
                self.fitter = SpectralFitter(standard_files=standard_label_path_pairs)

                # attach display names to loaded dataset items
                for i, item in enumerate(self.dataset.data):
                    item["name"] = self.measurement_files[i]["name"]

                self.file_list.addItem("=== Measurement Files ===")
                for item in self.measurement_files:
                    self.file_list.addItem(f'{item["name"]}: {item["path"]}')

                self.file_list.addItem("=== Standard Files ===")
                for item in self.standard_files:
                    self.file_list.addItem(f'{item["name"]}: {item["path"]}')

                self.status_label.setText(
                    f"Status: Loaded {len(self.measurement_files)} measurements and "
                    f"{len(self.standard_files)} standards"
                )
        
            self.raw_button.setEnabled(True)
        except Exception as e:
            QMessageBox.critical(self, "File Selection Error", str(e))
            self.status_label.setText("Status: File selection failed")

    # Helper functions
    # Populates a list
    def _populate_file_list(self, files):
        # Removes the items in the listWidget just incase there exist items errors from other functions
        self.file_list.clear()
        for f in files:
            self.file_list.addItem(f)
    # updates
    def _update_status(self, message):
        self.status_label.setText(f"Status: {message}")

    # PLOTTING
    # Fortunately matplotlib plots the graphs, which is an interface already,
    # Thus we can just call it
    def plot_fits(self):
        if self.dataset is None:
            QMessageBox.warning(self, "No Data", "Load and fit data first.")
            return

        try:
            self.dataset.plot_fits()
            plt.show()

            #Dont show this if not raman
            grain_metrics = self.grain_metrics if self.mode == "Raman" else None

            dialog = AnalysisResultsDialog(
                mode=self.mode,
                results=self.dataset.results,
                grain_metrics=grain_metrics,
                parent=self
            )
            dialog.exec_()

            self.status_label.setText("Status: Fit plots opened")
        except Exception as e:
            QMessageBox.critical(self, "Plot Error", str(e))

    def plot_percentages(self):
        if self.dataset is None:
            QMessageBox.warning(self, "No Data", "Load and fit data first.")
            return

        try:
            self.dataset.plot_percentages()
            plt.show()
            self.status_label.setText("Status: Percentage plot opened")
        except Exception as e:
            QMessageBox.critical(self, "Plot Error", str(e))

    def plot_raw_data(self):
        if self.dataset is None:
            QMessageBox.warning(self, "No Data", "Load files first.")
            return

        try:
            for item in self.dataset.data:
                x = item["x"]
                y = item["y"]
                plt.figure()
                plt.plot(x, y)
                plt.title(item["filepath"])
                plt.xlabel("x")
                plt.ylabel("Intensity")
                plt.grid(True)

            plt.show()
            self.status_label.setText("Status: Raw data plots opened")
        except Exception as e:
            QMessageBox.critical(self, "Plot Error", str(e))

def main():
    # Call the initializer
    app = QApplication(sys.argv)

    #change the font
    font = QFont()
    font.setPointSize(15)
    app.setFont(font)

    # set the size of the window and show
    window = MainWindow()
    window.resize(1200, 900)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()