import matplotlib.pyplot as plt
import numpy as np 

#input all the key values from model fit and a name for the title
def plot_fit(result, title=""):

    xr = result["xr"]
    yr = result["yr"]
    total_fit = result["total_fit"]
    peaks = result["peaks"]

    plt.figure()
    plt.plot(xr, yr, 'k', label="Data")
    plt.plot(xr, total_fit, 'r', linewidth=2, label="Total Fit")

    # Plot each peak
    for i, peak in enumerate(peaks):
        plt.plot(xr, peak, '--', label=f"Peak {i+1}")

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