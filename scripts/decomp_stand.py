from dataset import DataSet
from plot import plot_fit_figure, plot_multiple_series
import numpy as np
import matplotlib.pyplot as plt

# Child class 1: Decomposition 
# For when standards create data, want to decompose standard
# CURRENTLY dont have new unique functions
class DecompDataSet(DataSet):
    #Constructor
    def __init__(self, filepaths):
        super().__init__(filepaths)

    #Get a table of decomposition values 
    # convinient for saving purposes
    def get_component_table(self):
        if not self.results:
            raise ValueError("No decomposition results found. Run apply_standard_fit first.")

        table = []

        for result in self.results:
            row = {"filepath": result["filepath"]}
            for name, pct in zip(result["standard_names"], result["percentages"]):
                row[name] = pct
            table.append(row)

        return table
    
    # implement abstract method: fit
    # calls the STANDARD fitter
    # CURRENTLY HARD CODED BOUNDS
    def fit(self, fitter,rangelb, rangehb):
        self.results = fitter.fit_n_standards(self.filepaths,rangelb, rangehb)

    # implement abstract method: plot fit
    # calls plot STANDARD fit
    def plot_fits(self):
        for result in self.results:
            fig = self.make_fit_figure(result)
        plt.show()

    # implement abstract method: plot percentages
    # sends different values to plot percentages
    def plot_percentages(self):
        percentages = [result["percentages"] for result in self.results]
        labels = self.results[0]["standard_names"]
        samples = np.arange(1, len(percentages) + 1)

        y_series = []
        for i in range(len(labels)):
            values = [p[i] for p in percentages]
            y_series.append(values)

        plot_multiple_series(
            samples,
            y_series,
            labels=labels,
            styles=['-o'] * len(labels),
            title="Standard Decomposition Percentages",
            xlabel="Sample Number",
            ylabel="Percentage (%)",
            ylim=(0, 100)
        )
    
    def make_fit_figure(self, result):
        x = result["x"]
        y = result["y"]
        total_fit = result["total_fit"]
        components = result["components"]
        names = result["standard_names"]

        labels = ["Measured"] + names + ["Total Fit"]
        styles = ['r--'] + ['-'] * len(components) + ['k']
        y_series = [y] + components + [total_fit]

        fig = plot_fit_figure(
            x,
            y_series,
            labels=labels,
            styles=styles,
            title=result["filepath"],
            xlabel="Wavelength",
            ylabel="Intensity"
        )

        return fig