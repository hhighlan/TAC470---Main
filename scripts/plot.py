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

def plot_raw_data(filepath, title="Raw"):
    """
    Parameters:
        filepath : str
            Path to data file
        title : str 
            Plot title
    """

    data = np.loadtxt(filepath)
    x = data[:, 0]
    y = data[:, 1]

    plt.figure()
    plt.plot(x, y, 'k')

    plt.xlabel("Raman shift (cm$^{-1}$)")
    plt.ylabel("Intensity")
    plt.title(title)

    plt.grid(True)

def plot_standard_fit(result):
    x = result["x"]
    y = result["y"]
    total_fit = result["total_fit"]
    components = result["components"]
    names = result["standard_names"]

    plt.figure()
    plt.plot(x, y, 'r--', label="Measured")

    # Plot components
    for comp, name in zip(components, names):
        plt.plot(x, comp, label=name)

    # Total fit
    plt.plot(x, total_fit, 'k', linewidth=2, label="Total Fit")

    plt.xlabel("Wavelength")
    plt.ylabel("Intensity")
    plt.title(result["filepath"])
    plt.legend()
    plt.grid(True)

def plot_lorentz_fit(result):

    xr = result["xr"]
    yr = result["yr"]
    total_fit = result["total_fit"]
    peaks = result["peaks"]

    plt.figure()
    plt.plot(xr, yr, 'k', label="Data")

    for i, peak in enumerate(peaks):
        plt.plot(xr, peak, '--', label=f"Peak {i+1}")

    plt.plot(xr, total_fit, 'r', linewidth=2, label="Total Fit")

    plt.xlabel("Raman shift")
    plt.ylabel("Intensity")
    plt.title(result["filepath"])
    plt.legend()
    plt.grid(True)