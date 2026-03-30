import os
import numpy as np
import pandas as pd

#HARD CODE METHOD FOR NOW
# start with function handle that takes in a string that is the directory of the data
def get_file_list(data_dir):
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

    # Attach full path using os method and join the 2 texts together via a for loop
    full_paths = [os.path.join(data_dir, f) for f in files]

    return full_paths
# return a array of names


def get_file_list_standard(data_dir):
    measurement_files = [
        "532nm_5s_IT_LP_1%.txt",
        "532nm_5s_IT_LP_5%.txt",
        "532nm_5s_IT_LP_10%.txt",
        "532nm_5s_IT_LP_50%.txt",
        "532nm_5s_IT_LP_100%.txt"
    ]
    standard_files = [
        ("NV0", "NV04_pl.dat"),
        ("NVm", "NVm4_pl.dat"),
        ("SiV", "SiV extrapolate.csv"),
    ]

    # Attach full path using os method and join the 2 texts together via a for loop
    full_measurement_files = [
        os.path.join(data_dir, f) for f in measurement_files
    ]

    full_standard_files = [
        (label, os.path.join(data_dir, fname))
        for label, fname in standard_files
    ]

    return full_measurement_files,full_standard_files


# HARD CODE 
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