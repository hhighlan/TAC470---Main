
from file_util import load_two_column_file
from plot import plot_standard_fit, plot_lorentz_fit, plot_percentages

class DataSet:
    def __init__(self, filepaths):
        """
        Generic container for any dataset
        """
        self.filepaths = filepaths
        self.data = []          # raw (x, y)
        self.processed = []     # cleaned / corrected data
        self.results = []       # analysis outputs

    def add_data(self, x, y):
        self.data.append({"x": x, "y": y})

    def add_result(self, result):
        self.results.append(result)

    def load_all(self):
        self.data = []

        for filepath in self.filepaths:
            x, y = load_two_column_file(filepath)
            self.data.append({
                "filepath": filepath,
                "x": x,
                "y": y
            })
    
    def apply_standard_fit(self, fitter):
        self.results = fitter.fit_n_standards(self.filepaths)

    def apply_lorentz_fit(self, fitter, n_peaks=2):
        self.results = [
            fitter.fit_n_lorentzians(fp, n_peaks=n_peaks)
            for fp in self.filepaths
        ]
    
    def plot_standard_fits(self):
        """
        Loop through results and plot standard decomposition
        """
        for result in self.results:
            plot_standard_fit(result)

    def plot_lorentz_fits(self):
        """
        Loop through results and plot Lorentzian fits
        """
        for result in self.results:
            plot_lorentz_fit(result)

    def plot_percentages(self):
        plot_percentages([r["percentages"] for r in self.results])