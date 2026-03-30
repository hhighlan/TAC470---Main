import numpy as np
from scipy.optimize import curve_fit
from scipy.interpolate import PchipInterpolator, interp1d
from scipy.ndimage import median_filter
from scipy.integrate import trapezoid

from model_func import lorentz
from file_util import load_two_column_file


class SpectralFitter:
    def __init__(self, standard_files=None):
        """
        standard_files should be a list of tuples like:
        [
            ("NV0", r"path\\to\\NV04_pl.dat"),
            ("NVm", r"path\\to\\NVm4_pl.dat"),
            ("SiV", r"path\\to\\SiV extrapolate.txt")
        ]
        """
        self.standard_files = standard_files or []

    # create some static methods 
    # that does math only internally and never called elsewhere

    @staticmethod
    def _zero_shift(y):
        return y - np.min(y)

    @staticmethod
    def _linear_background_correct(x, y):
        p = np.polyfit(x, y, 1)
        background = np.polyval(p, x)
        y_corr = y - background
        return SpectralFitter._zero_shift(y_corr)

    @staticmethod
    def _fill_outliers(y, window=101, z_thresh=3.5):
        if len(y) < window:
            return y

        med = median_filter(y, size=window, mode="nearest")
        resid = y - med
        mad = np.median(np.abs(resid - np.median(resid)))

        if mad == 0:
            return y

        robust_z = 0.6745 * resid / mad
        mask = np.abs(robust_z) > z_thresh

        if not np.any(mask):
            return y

        idx = np.arange(len(y))
        good = ~mask

        y_new = y.copy()
        y_new[mask] = np.interp(idx[mask], idx[good], y[good])
        return y_new

    @staticmethod
    def _interp_to_target(x_src, y_src, x_target):
        """
        Interpolate source data onto the target x-grid using PCHIP.
        Outside the source range, values become 0.
        """
        order = np.argsort(x_src)
        x_src = x_src[order]
        y_src = y_src[order]

        interp = PchipInterpolator(x_src, y_src, extrapolate=False)
        y_new = interp(x_target)
        return np.nan_to_num(y_new, nan=0.0)
    

    # First fit type, n lorentzians 
    def fit_n_lorentzians(self, filepath, n_peaks=2, rangelb=1200, rangehb=1700):
        """
        Fit a file using n Lorentzian peaks with fixed centers found from derivatives.
        Returns a dictionary with fit results.
        """
        x, y = load_two_column_file(filepath)

        # background correction
        y_corr = self._linear_background_correct(x, y)

        # ROI
        roi = (x >= rangelb) & (x <= rangehb)
        xr = x[roi]
        yr = y_corr[roi]

        # derivatives
        dy = np.gradient(yr, xr)
        d2y = np.gradient(dy, xr)

        # candidate maxima
        zc = np.where(np.diff(np.sign(dy)) != 0)[0]
        cand = zc[d2y[zc] < 0]

        # alert user if conditions not met (throw error)
        if len(cand) < n_peaks:
            raise ValueError(
                f"Found only {len(cand)} candidate peaks, but n_peaks={n_peaks} was requested."
            )

        # take the tallest n peaks
        order = np.argsort(yr[cand])[::-1]
        peak_idx = np.sort(cand[order[:n_peaks]])

        x0_list = xr[peak_idx]
        A_list = yr[peak_idx]

        # width guesses
        g_list = []
        for i, idx in enumerate(peak_idx):
            denom = d2y[idx]
            if denom < 0:
                g_est = np.sqrt(-2 * A_list[i] / denom)
            else:
                g_est = (rangehb - rangelb) / (10 * n_peaks)
            g_list.append(g_est)

        def model(x, *params):
            y_fit = np.zeros_like(x, dtype=float)
            for i in range(n_peaks):
                A = params[2 * i]
                g = params[2 * i + 1]
                x0 = x0_list[i]
                y_fit += lorentz(A, x0, g, x)
            return y_fit

        p0 = []
        for i in range(n_peaks):
            p0.extend([A_list[i], g_list[i]])

        bounds_lower = [0] * (2 * n_peaks)
        bounds_upper = [np.inf] * (2 * n_peaks)

        p_fit, _ = curve_fit(
            model,
            xr,
            yr,
            p0=p0,
            bounds=(bounds_lower, bounds_upper),
            maxfev=20000
        )

        peak_curves = []
        areas = []

        for i in range(n_peaks):
            A = p_fit[2 * i]
            g = p_fit[2 * i + 1]
            x0 = x0_list[i]

            curve = lorentz(A, x0, g, xr)
            peak_curves.append(curve)

            area = (np.pi / 2) * A * g
            areas.append(area)

        total_fit = np.sum(peak_curves, axis=0)
        total_area = np.sum(areas)

        percentages = [(a / total_area) * 100 if total_area != 0 else np.nan for a in areas]

        return {
            "filepath": filepath,
            "xr": xr,
            "yr": yr,
            "x0_list": x0_list,
            "params": p_fit,
            "peaks": peak_curves,
            "total_fit": total_fit,
            "areas": areas,
            "percentages": percentages
        }

    # Second fit type, n standards 
    def fit_n_standards(self, measurement_filepaths,rangelb=550, rangehb=800):
        """
        Fit each measured spectrum as a linear combination of the standard spectra.
        The standard spectra are interpolated onto the measured x-grid.
        """
        if len(self.standard_files) == 0:
            raise ValueError("No standard files were provided to SpectralFitter.")

        # load standard basis spectra once
        standard_basis = []
        standard_names = []

        for label, std_path in self.standard_files:
            sx, sy = load_two_column_file(std_path)
            sy = self._zero_shift(sy)
            standard_names.append(label)
            standard_basis.append((sx, sy))

        results = []

        for filepath in measurement_filepaths:
            x, y = load_two_column_file(filepath)
            def restrict_range(x, y):
                mask = (x >= rangelb) & (x <= rangehb)
                return x[mask], y[mask]
            x, y = restrict_range(x, y)

            # baseline shift and outlier handling, similar to MATLAB code
            y = self._zero_shift(y)
            y = self._fill_outliers(y, window=101)

            # interpolate all standards onto this x-grid
            basis_on_x = []
            for sx, sy in standard_basis:
                sy_interp = self._interp_to_target(sx, sy, x)
                basis_on_x.append(sy_interp)

            basis_on_x = np.asarray(basis_on_x)  # shape: (n_standards, len(x))

            def model(x_dummy, *coeffs):
                coeffs = np.asarray(coeffs)
                return np.sum(coeffs[:, None] * basis_on_x, axis=0)

            n_std = len(standard_names)
            p0 = np.ones(n_std)
            bounds_lower = np.zeros(n_std)
            bounds_upper = np.full(n_std, np.inf)

            p_opt, _ = curve_fit(
                model,
                x,
                y,
                p0=p0,
                bounds=(bounds_lower, bounds_upper),
                maxfev=20000
            )

            component_curves = []
            component_areas = []

            for i in range(n_std):
                comp = p_opt[i] * basis_on_x[i]
                component_curves.append(comp)
                component_areas.append(np.trapezoid(comp, x))

            total_fit = np.sum(component_curves, axis=0)
            total_area = np.trapezoid(total_fit, x)

            percentages = [
                (area / total_area) * 100 if total_area != 0 else np.nan
                for area in component_areas
            ]

            results.append({
                "filepath": filepath,
                "x": x,
                "y": y,
                "standard_names": standard_names,
                "coefficients": p_opt,
                "components": component_curves,
                "total_fit": total_fit,
                "areas": component_areas,
                "percentages": percentages
            })

        return results