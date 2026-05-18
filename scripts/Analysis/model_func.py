import numpy as np

def lorentz(A, x0, g, x):
    """
    Lorentzian peak function.
    
    Parameters:
        A  : amplitude
        x0 : center
        g  : width (FWHM)
        x  : array
    
    Returns:
        Lorentzian evaluated at x
    """
    return A * ((g / 2)**2 / ((x - x0)**2 + (g / 2)**2))

