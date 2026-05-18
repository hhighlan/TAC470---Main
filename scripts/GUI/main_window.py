import os
import matplotlib.pyplot as plt
import numpy as np

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QLabel, QPushButton,
    QListWidget, QVBoxLayout, QHBoxLayout, QComboBox,
    QFileDialog, QMessageBox, QDialog
)

from Analysis.decomp_stand import DecompDataSet
from Analysis.raman import RamanDataSet
from Analysis.fitters import SpectralFitter
from Exporter import ResultExporter

from GUI.gui_dialogs import (
    FileNamingDialog,
    AnalysisResultsDialog,
    FitParameterDialog
)

from GUI.gui_style import get_main_stylesheet


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Data Analysis APP")
        self.setStyleSheet(get_main_stylesheet())

        self.data_dir = os.path.abspath("../data")

        self.dataset = None
        self.fitter = None
        self.mode = "Raman"

        self.measurement_files = []
        self.standard_files = []
        self.raman_files = []
        self.grain_metrics = []

        central = QWidget()
        self.setCentralWidget(central)

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
        self.help_button = QPushButton("Help")

        self.status_label = QLabel("Status: Ready")
        self.status_label.setObjectName("statusLabel")

        self.file_list = QListWidget()

        main_layout = QVBoxLayout()
        controls_row = QHBoxLayout()
        fit_row = QHBoxLayout()
        plot_row = QHBoxLayout()

        controls_row.addWidget(self.mode_label)
        controls_row.addWidget(self.mode_combo)
        controls_row.addWidget(self.clear_button)
        controls_row.addWidget(self.help_button)

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

        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        self.load_button.clicked.connect(self.select_files)
        self.fit_button.clicked.connect(self.run_fit)
        self.plot_fits_button.clicked.connect(self.plot_fits)
        self.plot_percentages_button.clicked.connect(self.plot_percentages)
        self.raw_button.clicked.connect(self.plot_raw_data)
        self.clear_button.clicked.connect(self.clear_all)
        self.save_results_button.clicked.connect(self.save_results)
        self.help_button.clicked.connect(self.show_help)

        self.set_initial_button_state()

        self.on_mode_changed(self.mode_combo.currentText())

    def show_help(self):
        QMessageBox.information(
            self,
            "How to Use This Program",
            "Typical analysis procedure:\n\n"
            "1. Choose an analysis mode: Raman or Decomposition.\n"
            "2. Click Load Files and select your data files.\n"
            "3. Rename files if you want cleaner plot labels.\n"
            "4. Click Run Fit and enter the fitting range.\n"
            "5. Click Plot Fits to view the fitted curves and calculated values.\n"
            "6. Click Plot Percentages to compare peak or component contributions.\n"
            "7. Click Save Results to export numerical results and figures.\n\n"
            "Raman mode:\n"
            "- Fits Lorentzian peaks.\n"
            "- Calculates peak areas.\n"
            "- Calculates the grain size metric when diamond and G peaks are found.\n\n"
            "Decomposition mode:\n"
            "- Uses selected standard spectra.\n"
            "- Fits measured spectra as a combination of standards.\n"
            "- Reports component percentages."
        )

    def set_initial_button_state(self):
        self.raw_button.setEnabled(False)
        self.plot_fits_button.setEnabled(False)
        self.plot_percentages_button.setEnabled(False)
        self.save_results_button.setEnabled(False)

    def clear_all(self):
        reply = QMessageBox.question(
            self,
            "Confirm Clear",
            "Are you sure you want to clear all data?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.reset_state_for_new_selection()
            self._update_status("Cleared all data")

    def save_results(self):
        if self.dataset is None or not getattr(self.dataset, "results", None):
            QMessageBox.warning(self, "No Results", "Run a fit before saving results.")
            return

        folder = QFileDialog.getExistingDirectory(
            self,
            "Choose Folder to Save Results"
        )

        if not folder:
            self._update_status("Save cancelled")
            return

        try:
            exporter = ResultExporter(
                dataset=self.dataset,
                mode=self.mode,
                grain_metrics=self.grain_metrics if self.mode == "Raman" else None
            )

            output = exporter.export_all(folder)

            self._update_status("Results saved successfully")

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
            self._update_status("Save failed")

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

    def on_mode_changed(self, text):
        self.mode = text

        self.file_list.clear()
        self.dataset = None
        self.fitter = None
        self.grain_metrics = []

        self.raw_button.setEnabled(False)
        self.plot_fits_button.setEnabled(False)
        self.plot_percentages_button.setEnabled(False)
        self.save_results_button.setEnabled(False)

        self._update_status(f"Mode set to {self.mode}")

    def run_fit(self):
        if self.dataset is None or self.fitter is None:
            QMessageBox.warning(self, "No Data", "Select files first.")
            return

        try:
            dialog = FitParameterDialog(mode=self.mode, parent=self)

            if dialog.exec_() != QDialog.Accepted:
                self._update_status("Fit cancelled")
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

                if hasattr(self.dataset, "attach_peak_areas_to_results"):
                    self.dataset.attach_peak_areas_to_results()

                self.grain_metrics = self.dataset.calculate_grain_size_metric()

                self._update_status(
                    f"Raman fit complete | peaks={n_peaks}, range=({rangelb}, {rangehb})"
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

                self._update_status(
                    f"Decomposition fit complete | range=({rangelb}, {rangehb})"
                )

            self.fit_button.setEnabled(False)
            self.plot_fits_button.setEnabled(True)
            self.plot_percentages_button.setEnabled(True)
            self.save_results_button.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "Fit Error", str(e))
            self._update_status("Fit failed")

    def select_files(self):
        try:
            self.reset_state_for_new_selection()

            if self.mode == "Raman":
                named_files = self.get_named_file_selection("Select Raman Data Files")

                if not named_files:
                    self._update_status("No Raman files selected")
                    return

                self.raman_files = named_files
                raman_paths = [item["path"] for item in self.raman_files]

                self.dataset = RamanDataSet(raman_paths)
                self.dataset.load_all()
                self.fitter = SpectralFitter()

                for i, item in enumerate(self.dataset.data):
                    item["name"] = self.raman_files[i]["name"]

                for item in self.raman_files:
                    self.file_list.addItem(f'{item["name"]}: {item["path"]}')

                self._update_status(f"Loaded {len(self.raman_files)} Raman files")

            else:
                named_measurements = self.get_named_file_selection(
                    "Select Decomposition Measurement Files"
                )

                if not named_measurements:
                    self._update_status("No measurement files selected")
                    return

                named_standards = self.get_named_file_selection("Select Standard Files")

                if not named_standards:
                    self._update_status("No standard files selected")
                    return

                self.measurement_files = named_measurements
                self.standard_files = named_standards

                measurement_paths = [item["path"] for item in self.measurement_files]

                standard_label_path_pairs = [
                    (item["name"], item["path"]) for item in self.standard_files
                ]

                self.dataset = DecompDataSet(measurement_paths)
                self.dataset.load_all()
                self.fitter = SpectralFitter(standard_files=standard_label_path_pairs)

                for i, item in enumerate(self.dataset.data):
                    item["name"] = self.measurement_files[i]["name"]

                self.file_list.addItem("=== Measurement Files ===")
                for item in self.measurement_files:
                    self.file_list.addItem(f'{item["name"]}: {item["path"]}')

                self.file_list.addItem("=== Standard Files ===")
                for item in self.standard_files:
                    self.file_list.addItem(f'{item["name"]}: {item["path"]}')

                self._update_status(
                    f"Loaded {len(self.measurement_files)} measurements and "
                    f"{len(self.standard_files)} standards"
                )

            self.raw_button.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "File Selection Error", str(e))
            self._update_status("File selection failed")

    def _populate_file_list(self, files):
        self.file_list.clear()

        for f in files:
            self.file_list.addItem(f)

    def _update_status(self, message):
        self.status_label.setText(f"Status: {message}")

    def plot_fits(self):
        if self.dataset is None:
            QMessageBox.warning(self, "No Data", "Load and fit data first.")
            return

        try:
            self.dataset.plot_fits()

            grain_metrics = self.grain_metrics if self.mode == "Raman" else None

            dialog = AnalysisResultsDialog(
                mode=self.mode,
                results=self.dataset.results,
                grain_metrics=grain_metrics,
                parent=self
            )
            dialog.exec_()

            self._update_status("Fit plots opened")

        except Exception as e:
            QMessageBox.critical(self, "Plot Error", str(e))

    def plot_percentages(self):
        if self.dataset is None:
            QMessageBox.warning(self, "No Data", "Load and fit data first.")
            return

        try:
            self.dataset.plot_percentages()
            self._update_status("Percentage plot opened")

        except Exception as e:
            QMessageBox.critical(self, "Plot Error", str(e))

    def plot_raw_data(self):
        if self.dataset is None:
            QMessageBox.warning(self, "No Data", "Load files first.")
            return

        try:
            n_files = len(self.dataset.data)

            if n_files == 0:
                QMessageBox.warning(self, "No Data", "No loaded data found.")
                return

            # Choose number of columns
            n_cols = 2

            # Compute number of rows needed
            n_rows = int(np.ceil(n_files / n_cols))

            fig, axes = plt.subplots(
                n_rows,
                n_cols,
                figsize=(14, 4 * n_rows),
                sharex=False
            )

            fig.suptitle("Raw Data", fontsize=20, fontweight="bold")

            # Make axes always easy to loop over
            axes = np.array(axes).flatten()

            for i, item in enumerate(self.dataset.data):
                ax = axes[i]

                x = item["x"]
                y = item["y"]

                title = item.get("name", item.get("filepath", "Raw Data"))

                ax.plot(x, y)
                ax.set_title(title, fontsize=16)
                ax.set_xlabel("x", fontsize=14)
                ax.set_ylabel("Intensity", fontsize=14)
                ax.tick_params(axis="both", labelsize=12)
                ax.grid(True)

            # Hide unused subplot boxes
            for j in range(n_files, len(axes)):
                axes[j].axis("off")

            fig.tight_layout(rect=[0, 0, 1, 0.95])
            plt.show()

            self._update_status("Raw data plots opened")

        except Exception as e:
            QMessageBox.critical(self, "Plot Error", str(e))