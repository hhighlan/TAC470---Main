import numpy as np
from scipy.optimize import curve_fit
from model_func import lorentz 

# HARD CODE VERSION
# intake the file names, and the bounds
def fit_two_lorentzian(filepath, rangelb=1200, rangehb=1700):
    """
    Takes a file path and returns:
    - xr, yr (ROI data)
    - fit parameters
    - peak percentages
    """

    data = np.loadtxt(filepath)
    x = data[:, 0]
    y = data[:, 1]

    # Background subtraction
    p = np.polyfit(x, y, 1)
    y_corr = y - np.polyval(p, x)
    y_corr -= np.min(y_corr)

    # ROI
    roi = (x >= rangelb) & (x <= rangehb)
    xr = x[roi]
    yr = y_corr[roi]

    # Derivatives
    dy = np.gradient(yr, xr)
    d2y = np.gradient(dy, xr)

    #extract the peaks (d2s is negative so peak max only)
    zc = np.where(np.diff(np.sign(dy)) != 0)[0]
    cand = zc[d2y[zc] < 0]

    #sort the peaks to keep in order index finding
    order = np.argsort(yr[cand])[::-1]
    peak_idx = np.sort(cand[order[:2]])

    # standard value for curve fit guesses
    x0_1, x0_2 = xr[peak_idx]

    A1, A2 = yr[peak_idx]

    g1 = np.sqrt(-2 * A1 / d2y[peak_idx[0]])
    g2 = np.sqrt(-2 * A2 / d2y[peak_idx[1]])

    # define curve fit model by calling lorenzian
    def model(x, A1, g1, A2, g2):
        return (lorentz(A1, x0_1, g1, x) +
                lorentz(A2, x0_2, g2, x))

    p0 = [A1, g1, A2, g2]
    bounds = ([0, 0, 0, 0], [np.inf, np.inf, np.inf, np.inf])

    #calc fit
    p_fit, _ = curve_fit(model, xr, yr, p0=p0, bounds=bounds)

    # extract curve fit values
    A1_fit, g1_fit, A2_fit, g2_fit = p_fit

    peak1_curve = lorentz(A1_fit, x0_1, g1_fit, xr)
    peak2_curve = lorentz(A2_fit, x0_2, g2_fit, xr)
    total_fit = peak1_curve + peak2_curve

    # calculate percentages using area
    area1 = (np.pi / 2) * A1_fit * g1_fit
    area2 = (np.pi / 2) * A2_fit * g2_fit
    total = area1 + area2

    percent1 = 100 * area1 / total
    percent2 = 100 * area2 / total

    # return all interested parameters for plotting
    return {
        "xr": xr,
        "yr": yr,
        "total_fit": total_fit,       
        "peak1": peak1_curve,         
        "peak2": peak2_curve,         
        "percentages": (percent1, percent2)
    }