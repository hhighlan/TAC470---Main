import os
import pandas as pd
import matplotlib.pyplot as plt


class ResultExporter:
    def __init__(self, dataset, mode, grain_metrics=None):
        self.dataset = dataset
        self.mode = mode
        self.grain_metrics = grain_metrics or []

    def _make_grain_metric_map(self):
        return {
            item["filepath"]: item["grain_size_metric"]
            for item in self.grain_metrics
        }

    def export_excel(self, folder):
        os.makedirs(folder, exist_ok=True)

        grain_map = self._make_grain_metric_map()
        rows = []

        max_peaks = 0
        for result in self.dataset.results:
            max_peaks = max(max_peaks, len(result.get("area_list", [])))

        for result in self.dataset.results:
            row = {}
            filepath = result.get("filepath", "")
            row["File"] = os.path.basename(filepath)

            if self.mode == "Raman":
                row["Grain Size Metric"] = grain_map.get(filepath, None)

            x0_list = result.get("x0_list", [])
            area_list = result.get("area_list", [])

            for i in range(max_peaks):
                row[f"Peak Center {i+1}"] = x0_list[i] if i < len(x0_list) else None
                row[f"Peak Area {i+1}"] = area_list[i] if i < len(area_list) else None

            rows.append(row)

        df = pd.DataFrame(rows)
        excel_path = os.path.join(folder, f"{self.mode.lower()}_results.xlsx")
        df.to_excel(excel_path, index=False)
        return excel_path

    def export_raw_data_excel(self, folder):
        os.makedirs(folder, exist_ok=True)

        file_path = os.path.join(folder, f"{self.mode.lower()}_raw_data.xlsx")

        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            for item in self.dataset.data:
                name = os.path.splitext(os.path.basename(item["filepath"]))[0][:31]
                df = pd.DataFrame({
                    "x": item["x"],
                    "y": item["y"]
                })
                df.to_excel(writer, sheet_name=name, index=False)

        return file_path

    def export_fit_figures(self, folder):
        os.makedirs(folder, exist_ok=True)

        saved_files = []

        for result in self.dataset.results:
            filepath = result.get("filepath", "unknown")
            name = os.path.splitext(os.path.basename(filepath))[0]

            fig = self.dataset.make_fit_figure(result)
            outpath = os.path.join(folder, f"{name}_fit.png")
            fig.savefig(outpath, dpi=300, bbox_inches="tight")
            plt.close(fig)
            saved_files.append(outpath)

        return saved_files

    def export_all(self, folder):
        excel_summary = self.export_excel(folder)
        excel_raw = self.export_raw_data_excel(folder)
        figures = self.export_fit_figures(folder)

        return {
            "summary_excel": excel_summary,
            "raw_excel": excel_raw,
            "figures": figures
        }