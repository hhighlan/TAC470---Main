import os

from PyQt5.QtCore import Qt

from PyQt5.QtWidgets import (
    QLabel, QDialog, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QDialogButtonBox, QAbstractItemView,
    QMessageBox, QDoubleSpinBox, QSpinBox, QFormLayout
)


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

        base_headers = ["File"]

        max_peaks = 0
        for result in results:
            area_list = result.get("area_list", [])
            max_peaks = max(max_peaks, len(area_list))

        peak_headers = [f"Peak Area {i + 1}" for i in range(max_peaks)]

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
            value_text = "Not found" if value is None else f"{value:.4f}"
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

        self.lower_spin = QDoubleSpinBox()
        self.lower_spin.setDecimals(2)
        self.lower_spin.setRange(-1e9, 1e9)

        self.upper_spin = QDoubleSpinBox()
        self.upper_spin.setDecimals(2)
        self.upper_spin.setRange(-1e9, 1e9)

        if mode == "Raman":
            self.lower_spin.setValue(1200)
            self.upper_spin.setValue(1700)
        else:
            self.lower_spin.setValue(550)
            self.upper_spin.setValue(800)

        form_layout.addRow("Lower bound:", self.lower_spin)
        form_layout.addRow("Upper bound:", self.upper_spin)

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