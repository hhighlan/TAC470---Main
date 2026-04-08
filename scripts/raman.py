from dataset import DataSet
from plot import plot
import numpy as np

# Child class of Dataset
# for when there are lorenzians within the data (a classic raman)
# decomposes the raman
class RamanDataSet(DataSet):
    # Constructor
    def __init__(self, filepaths):
        super().__init__(filepaths)

    # calculates grain size
    # unique to raman
    def calculate_grain_size_metric(self):
        if not self.results:
            raise ValueError("No Raman fit results found. Run apply_lorentz_fit first.")

        grain_metrics = []

        for result in self.results:
            x0_list = result["x0_list"]
            params = result["params"]

            I_diam = None
            I_G = None

            for i, x0 in enumerate(x0_list):
                A = params[2 * i]

                if abs(x0 - 1332.5) < 20:
                    I_diam = A
                elif abs(x0 - 1550) < 50:
                    I_G = A

            if I_diam is None or I_G is None:
                grain_value = None
            else:
                grain_value = 100 * I_G / (75 * I_diam + I_G)

            grain_metrics.append({
                "filepath": result["filepath"],
                "grain_size_metric": grain_value
            })

        return grain_metrics
    
    # implement abstract method: fit
    # calls the fit LORENTZIAN
    def fit(self, fitter, n_peaks=2, rangelb=1200, rangehb=1700):
        self.results = []

        for filepath in self.filepaths:
            result = fitter.fit_n_lorentzians(
                filepath,
                n_peaks,
                rangelb,
                rangehb
            )
            self.results.append(result)

    # implement abstract method: plotfit 
    # calls plot LORENTZIAN 
    def plot_fits(self):
        for result in self.results:
            xr = result["xr"]
            yr = result["yr"]
            total_fit = result["total_fit"]
            peaks = result["peaks"]

            y_series = [yr] + peaks + [total_fit]
            labels = ["Data"] + [f"Peak {i+1}" for i in range(len(peaks))] + ["Total Fit"]
            styles = ['k'] + ['--'] * len(peaks) + ['r']

            plot(
                xr,
                y_series,
                labels=labels,
                styles=styles,
                title=result["filepath"],
                xlabel="Raman shift",
                ylabel="Intensity"
            )
    
    # implement abstract method: plotpercentages
    # pass in different values to plot percentages
    def plot_percentages(self):
        percentages = [result["percentages"] for result in self.results]
        n_peaks = len(percentages[0])
        labels = [f"Peak {i+1}" for i in range(n_peaks)]
        samples = np.arange(1, len(percentages) + 1)

        y_series = []
        for i in range(n_peaks):
            values = [p[i] for p in percentages]
            y_series.append(values)

        plot(
            samples,
            y_series,
            labels=labels,
            styles=['-o'] * n_peaks,
            title="Raman Peak Contributions",
            xlabel="Sample Number",
            ylabel="Percentage (%)",
            ylim=(0, 100)
        )