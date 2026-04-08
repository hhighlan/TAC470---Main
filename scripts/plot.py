import matplotlib.pyplot as plt
import numpy as np 

def plot(
    x,
    y_series,
    labels=None,
    styles=None,
    title="",
    xlabel="",
    ylabel="",
    ylim=None,
    show_legend=True
):
    """
    General plotting function.

    Parameters:
        x : array
        y_series : list of arrays (each curve to plot)
        labels : list of labels for legend
        styles : list of matplotlib styles (e.g. 'k', '--', etc.)
    """

    plt.figure()

    n = len(y_series)

    for i in range(n):
        y = y_series[i]

        style = styles[i] if styles else '-'
        label = labels[i] if labels else None

        plt.plot(x, y, style, label=label)

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)

    if ylim is not None:
        plt.ylim(ylim)

    plt.grid(True)

    if show_legend and labels:
        plt.legend()

# plot the raw data
def plot_raw_data(filepath, title="Raw"):
    data = np.loadtxt(filepath)
    x = data[:, 0]
    y = data[:, 1]

    plot(
        x,
        [y],
        labels=["Raw Data"],
        styles=['k'],
        title=title,
        xlabel="Raman shift (cm$^{-1}$)",
        ylabel="Intensity"
    )