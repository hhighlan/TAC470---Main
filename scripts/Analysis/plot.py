import matplotlib.pyplot as plt
import numpy as np


def plot_fit_figure(
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
    fig, ax = plt.subplots()

    n = len(y_series)

    for i in range(n):
        y = y_series[i]
        style = styles[i] if styles else '-'
        label = labels[i] if labels else None
        ax.plot(x, y, style, label=label)

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)

    if ylim is not None:
        ax.set_ylim(ylim)

    ax.grid(True)

    if show_legend and labels:
        ax.legend()

    return fig


def plot_multiple_series(
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
    fig = plot_fit_figure(
        x,
        y_series,
        labels=labels,
        styles=styles,
        title=title,
        xlabel=xlabel,
        ylabel=ylabel,
        ylim=ylim,
        show_legend=show_legend
    )
    return fig


def plot_raw_data(filepath, title="Raw"):
    data = np.loadtxt(filepath)
    x = data[:, 0]
    y = data[:, 1]

    fig = plot_fit_figure(
        x,
        [y],
        labels=["Raw Data"],
        styles=['k'],
        title=title,
        xlabel="Raman shift (cm$^{-1}$)",
        ylabel="Intensity"
    )

    return fig