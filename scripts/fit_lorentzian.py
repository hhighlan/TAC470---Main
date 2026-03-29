import numpy as np
from scipy.optimize import curve_fit
from model_func import lorentz


def fit_n_lorentzian(filepath, n_peaks, rangelb, rangehb):

    data = np.loadtxt(filepath)
    x = data[:, 0]
    y = data[:, 1]

    # --- Background subtraction ---
    p = np.polyfit(x, y, 1)
    y_corr = y - np.polyval(p, x)
    y_corr -= np.min(y_corr)

    # --- ROI ---
    roi = (x >= rangelb) & (x <= rangehb)
    xr = x[roi]
    yr = y_corr[roi]

    # --- Derivatives ---
    dy = np.gradient(yr, xr)
    d2y = np.gradient(dy, xr)

    zc = np.where(np.diff(np.sign(dy)) != 0)[0]
    cand = zc[d2y[zc] < 0]

    # Sort peaks by height
    order = np.argsort(yr[cand])[::-1]

    # Take top n peaks
    peak_idx = np.sort(cand[order[:n_peaks]])

    x0_list = xr[peak_idx]
    A_list = yr[peak_idx]

    # Width estimates
    g_list = []
    for i in range(n_peaks):
        idx = peak_idx[i]
        g_est = np.sqrt(-2 * A_list[i] / d2y[idx])
        g_list.append(g_est)

    # --- Model function ---
    # With n peaks, there are n A, g x0 and yfit
    # this should return a n sized array of y_fits with lorentzs read to go
    def model(x, *params):
        y_fit = np.zeros_like(x)
        for i in range(n_peaks):
            A = params[2*i]
            g = params[2*i + 1]
            x0 = x0_list[i]
            y_fit += lorentz(A, x0, g, x)
        return y_fit

    # Initial guess: [A1, g1, A2, g2, ...]
    p0 = []
    for i in range(n_peaks):
        p0.extend([A_list[i], g_list[i]])

    bounds_lower = [0] * (2 * n_peaks)
    bounds_upper = [np.inf] * (2 * n_peaks)

    # _ contains things like error and mean free square, side products 
    # of fit functions
    p_fit, _ = curve_fit(model, xr, yr, p0=p0,
                         bounds=(bounds_lower, bounds_upper))

    # --- Build curves ---
    peak_curves = []
    areas = []

    for i in range(n_peaks):
        A = p_fit[2*i]
        g = p_fit[2*i + 1]
        x0 = x0_list[i]

        curve = lorentz(A, x0, g, xr)
        peak_curves.append(curve)

        area = (np.pi / 2) * A * g
        areas.append(area)

    total_fit = np.sum(peak_curves, axis=0)
    total_area = sum(areas)

    percentages = [(a / total_area) * 100 for a in areas]

    return {
        "xr": xr,
        "yr": yr,
        "total_fit": total_fit,
        "peaks": peak_curves,        # list of arrays
        "percentages": percentages   # list
    }