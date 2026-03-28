import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

base_dir = r"C:\Users\titih\Desktop\TAC470---Main\data"

# File names
files = [
    "sample 70_1.txt",
    "sample 70_2.txt",
    "sample 70_3.txt",
    "sample 70_4.txt",
    "sample 70_5.txt",
    "sample 70_6.txt",
    "sample 70_7.txt",
    "sample 70_8.txt"
]

numFiles = len(files)

# Storage
S70 = []
y_corrected = []
peak_percentages = np.zeros((numFiles, 2))

# Parameters
rangelb = 1200
rangehb = 1700

# Lorentzian function
def lorentz(A, x0, g, x):
    return A * ((g/2)**2 / ((x - x0)**2 + (g/2)**2))

# Model with two peaks (fixed centers)
def model(x, A1, g1, A2, g2, x0_1, x0_2):
    return lorentz(A1, x0_1, g1, x) + lorentz(A2, x0_2, g2, x)

for k in range(numFiles):

    # --- Read data ---
    filepath = os.path.join(base_dir, files[k])
    data = np.loadtxt(filepath)
    S70.append(data)

    x = data[:, 0]
    y = data[:, 1]

    # --- Linear background subtraction ---
    p = np.polyfit(x, y, 1)
    background = np.polyval(p, x)

    y_corr = y - background
    y_corr = y_corr - np.min(y_corr)

    y_corrected.append(y_corr)

    # --- Region of interest ---
    roi = (x >= rangelb) & (x <= rangehb)
    xr = x[roi]
    yr = y_corr[roi]

    # --- Derivative-based peak detection ---
    dy = np.gradient(yr, xr)
    d2y = np.gradient(dy, xr)

    zc = np.where(np.diff(np.sign(dy)) != 0)[0]
    cand = zc[d2y[zc] < 0]  # maxima only

    # Sort by peak height
    order = np.argsort(yr[cand])[::-1]
    peak_idx = cand[order[:2]]
    peak_idx = np.sort(peak_idx)

    # Peak centers
    x0_1 = xr[peak_idx[0]]
    x0_2 = xr[peak_idx[1]]

    # Initial guesses
    A1 = yr[peak_idx[0]]
    A2 = yr[peak_idx[1]]

    # Width estimates from curvature
    g1 = np.sqrt(-2 * A1 / d2y[peak_idx[0]])
    g2 = np.sqrt(-2 * A2 / d2y[peak_idx[1]])

    p0 = [A1, g1, A2, g2]

    # Fit (note: x0 fixed via lambda wrapper)
    def fit_func(x, A1, g1, A2, g2):
        return model(x, A1, g1, A2, g2, x0_1, x0_2)

    bounds = ([0, 0, 0, 0], [np.inf, np.inf, np.inf, np.inf])

    p_fit, _ = curve_fit(fit_func, xr, yr, p0=p0, bounds=bounds)

    A1_fit, g1_fit, A2_fit, g2_fit = p_fit

    # --- Areas ---
    area1 = (np.pi / 2) * A1_fit * g1_fit
    area2 = (np.pi / 2) * A2_fit * g2_fit

    total_area = area1 + area2

    percent1 = 100 * area1 / total_area
    percent2 = 100 * area2 / total_area

    peak_percentages[k, :] = [percent1, percent2]

    # --- Plot ---
    plt.figure()
    plt.plot(xr, yr, 'k', label='Data')
    plt.plot(xr, fit_func(xr, *p_fit), 'r', linewidth=2, label='Total Fit')
    plt.plot(xr, lorentz(A1_fit, x0_1, g1_fit, xr), '--b', label='Peak 1')
    plt.plot(xr, lorentz(A2_fit, x0_2, g2_fit, xr), '--g', label='Peak 2')

    plt.xlabel('Raman shift (cm$^{-1}$)')
    plt.ylabel('Intensity')
    plt.title(f'File {k+1}: {files[k]}')
    plt.legend()

# --- Final plot ---
samples = np.arange(1, numFiles + 1)

peak1 = peak_percentages[:, 0]
peak2 = peak_percentages[:, 1]

plt.figure()
plt.plot(samples, peak1, '-o', linewidth=2, markersize=8, label='Peak 1')
plt.plot(samples, peak2, '-s', linewidth=2, markersize=8, label='Peak 2')

plt.xlabel('Sample Number')
plt.ylabel('Percentage Contribution (%)')
plt.xticks(samples)
plt.ylim([0, 100])
plt.grid(True)
plt.legend()
plt.title('Percentage Contribution of Peaks 1 and 2 Across Samples')

plt.show()

