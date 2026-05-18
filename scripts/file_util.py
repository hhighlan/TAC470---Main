import os
import numpy as np
import pandas as pd

# The util file that will handle the hardcode file names and reading them base on 
# file types

# since known the current data files contain 2 column with good data
# for now directly extract those 2 values 
def load_two_column_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()

     # --- TXT / DAT ---
    if ext in [".txt", ".dat"]:
        try:
            data = np.loadtxt(filepath)
        except Exception:
            # fallback if there are headers or weird spacing
            data = np.genfromtxt(filepath, delimiter=None)

    # --- CSV ---
    elif ext == ".csv":
        df = pd.read_csv(filepath)
        data = df.values

    # --- EXCEL ---
    elif ext in [".xlsx", ".xls"]:
        df = pd.read_excel(filepath, header=0)
        data = df.iloc[:, :2].values

    else:
        raise ValueError(f"Unsupported file type: {ext}")

    x = data[:, 0]
    y = data[:, 1]

    return np.asarray(x, dtype=float), np.asarray(y, dtype=float)