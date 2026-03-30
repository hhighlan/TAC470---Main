import numpy as np
from fit_lorentzian import fit_n_lorentzian
from plot import plot_fit, plot_percentages

class RamanObj:

    # constructor
    def __init__(self, filepaths):
        """
        Variable 
        filepath: array of string of where the files are
        results: fit result, i.e width
        percentages: for final plot, each peak percentage composition
        grainfactors: the computed value for raman
        """
        self.filepaths = filepaths   # input files
        self.results = []            # will store fit results
        self.percentages = []        # will store % contributions
        self.grain_factors = []


    def run_fits(self, n_peaks, rangelb, rangehb):
        """
        call fits to store values into the arrays
        """
        self.results = []
        self.percentages = []
        self.grain_factors = []

        for filepath in self.filepaths:
            result = fit_n_lorentzian(filepath, n_peaks,rangelb, rangehb)

            self.results.append(result)
            self.percentages.append(result["percentages"])
            self.grain_factors.append(result["grain_factor"])
        
        # Test print for now
        for i, g in enumerate(self.grain_factors):
            print(f"Sample {i+1}: grain factor = {g}")


    def plot_all_fits(self):
        """
        call plot
        """
        for i, result in enumerate(self.results):
            plot_fit(result, title=f"Sample {i+1}")


    def plot_summary(self):
        """
        call plot percentages
        """
        plot_percentages(self.percentages)