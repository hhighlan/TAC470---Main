import matplotlib.pyplot as plt
import numpy as np
from model_func import lorentz  

#input all the key values from model fit and a name for the title
def plot_fit(result, title=""):
    xr = result["xr"]
    yr = result["yr"]
    A1, g1, A2, g2 = result["params"]
    x0_1 = result["x0_1"]
    x0_2 = result["x0_2"]

    total_fit = (lorentz(A1, x0_1, g1, xr) +
                 lorentz(A2, x0_2, g2, xr))

    plt.figure()
    plt.plot(xr, yr, 'k', label="Data")
    plt.plot(xr, total_fit, 'r', linewidth=2, label="Total Fit")
    plt.plot(xr, lorentz(A1, x0_1, g1, xr), '--b', label="Peak 1")
    plt.plot(xr, lorentz(A2, x0_2, g2, xr), '--g', label="Peak 2")

    plt.xlabel("Raman shift (cm$^{-1}$)")
    plt.ylabel("Intensity")
    plt.title(title)
    plt.legend()

# input all the key percentages
def plot_percentages(percentages):
    samples = np.arange(1, len(percentages) + 1)

    p1 = [p[0] for p in percentages]
    p2 = [p[1] for p in percentages]

    plt.figure()
    plt.plot(samples, p1, '-o', linewidth=2, label="Peak 1")
    plt.plot(samples, p2, '-s', linewidth=2, label="Peak 2")

    plt.xlabel("Sample Number")
    plt.ylabel("Percentage (%)")
    plt.ylim([0, 100])
    plt.grid(True)
    plt.legend()
    plt.title("Peak Contributions")