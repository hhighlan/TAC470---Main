import numpy as np
from scipy.optimize import curve_fit
from scipy.interpolate import PchipInterpolator
from scipy.ndimage import median_filter

from model_func import lorentz
from file_util import load_two_column_file


class SpectralFitter:
    def __init__(self, standard_files=None):
        self.standard_files = standard_files or []

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
        order = np.argsort(x_src)
        x_src = x_src[order]
        y_src = y_src[order]

        interp = PchipInterpolator(x_src, y_src, extrapolate=False)
        y_new = interp(x_target)
        return np.nan_to_num(y_new, nan=0.0)

    @staticmethod
    def _restrict_range(x, y, rangelb, rangehb):
        mask = (x >= rangelb) & (x <= rangehb)
        return x[mask], y[mask]

    @staticmethod
    def _fit_curve_model(model, x, y, p0, bounds, maxfev=20000):
        p_fit, _ = curve_fit(
            model,
            x,
            y,
            p0=p0,
            bounds=bounds,
            maxfev=maxfev
        )
        return p_fit

    @staticmethod
    def _compute_percentages_from_areas(areas):
        total_area = np.sum(areas)
        if total_area == 0:
            return [np.nan for _ in areas], total_area

        percentages = [(a / total_area) * 100 for a in areas]
        return percentages, total_area

    @staticmethod
    def _build_component_results(components, x):
        areas = [np.trapezoid(comp, x) for comp in components]
        total_fit = np.sum(components, axis=0)
        total_area = np.trapezoid(total_fit, x)

        if total_area == 0:
            percentages = [np.nan for _ in areas]
        else:
            percentages = [(area / total_area) * 100 for area in areas]

        return total_fit, areas, percentages

    def _prepare_standard_basis(self):
        if len(self.standard_files) == 0:
            raise ValueError("No standard files were provided to SpectralFitter.")

        standard_basis = []
        standard_names = []

        for label, std_path in self.standard_files:
            sx, sy = load_two_column_file(std_path)
            sy = self._zero_shift(sy)
            standard_names.append(label)
            standard_basis.append((sx, sy))

        return standard_names, standard_basis

    def fit_n_lorentzians(self, filepath, n_peaks=2, rangelb=1200, rangehb=1700):
        x, y = load_two_column_file(filepath)

        # 1. prepare data
        y_corr = self._linear_background_correct(x, y)
        xr, yr = self._restrict_range(x, y_corr, rangelb, rangehb)

        dy = np.gradient(yr, xr)
        d2y = np.gradient(dy, xr)

        zc = np.where(np.diff(np.sign(dy)) != 0)[0]
        cand = zc[d2y[zc] < 0]

        if len(cand) < n_peaks:
            raise ValueError(
                f"Found only {len(cand)} candidate peaks, but n_peaks={n_peaks} was requested."
            )

        order = np.argsort(yr[cand])[::-1]
        peak_idx = np.sort(cand[order[:n_peaks]])

        x0_list = xr[peak_idx]
        A_list = yr[peak_idx]

        g_list = []
        for i, idx in enumerate(peak_idx):
            denom = d2y[idx]
            if denom < 0:
                g_est = np.sqrt(-2 * A_list[i] / denom)
            else:
                g_est = (rangehb - rangelb) / (10 * n_peaks)
            g_list.append(g_est)

        # 2. create model
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

        bounds = ([0] * (2 * n_peaks), [np.inf] * (2 * n_peaks))

        # 3. fit model
        p_fit = self._fit_curve_model(model, xr, yr, p0, bounds)

        # 4. extract results
        peak_curves = []
        lorentz_areas = []

        for i in range(n_peaks):
            A = p_fit[2 * i]
            g = p_fit[2 * i + 1]
            x0 = x0_list[i]

            curve = lorentz(A, x0, g, xr)
            peak_curves.append(curve)

            area = (np.pi / 2) * A * g
            lorentz_areas.append(area)

        total_fit = np.sum(peak_curves, axis=0)
        percentages, _ = self._compute_percentages_from_areas(lorentz_areas)

        return {
            "filepath": filepath,
            "xr": xr,
            "yr": yr,
            "x0_list": x0_list,
            "params": p_fit,
            "peaks": peak_curves,
            "total_fit": total_fit,
            "areas": lorentz_areas,
            "percentages": percentages
        }

    def fit_n_standards(self, measurement_filepaths, rangelb=550, rangehb=800):
        standard_names, standard_basis = self._prepare_standard_basis()
        results = []

        for filepath in measurement_filepaths:
            # 1. prepare data
            x, y = load_two_column_file(filepath)
            x, y = self._restrict_range(x, y, rangelb, rangehb)
            y = self._zero_shift(y)
            y = self._fill_outliers(y, window=101)

            basis_on_x = []
            for sx, sy in standard_basis:
                sy_interp = self._interp_to_target(sx, sy, x)
                basis_on_x.append(sy_interp)

            basis_on_x = np.asarray(basis_on_x)

            # 2. create model
            def model(x_dummy, *coeffs):
                coeffs = np.asarray(coeffs)
                return np.sum(coeffs[:, None] * basis_on_x, axis=0)

            n_std = len(standard_names)
            p0 = np.ones(n_std)
            bounds = (np.zeros(n_std), np.full(n_std, np.inf))

            # 3. fit model
            p_opt = self._fit_curve_model(model, x, y, p0, bounds)

            # 4. extract results
            component_curves = []
            for i in range(n_std):
                comp = p_opt[i] * basis_on_x[i]
                component_curves.append(comp)

            total_fit, component_areas, percentages = self._build_component_results(component_curves, x)

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