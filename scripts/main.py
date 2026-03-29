from file_read import get_file_list
from fit_lorentzian import fit_two_lorentzian
from plot import plot_fit, plot_percentages
import matplotlib.pyplot as plt

def main():

    data_dir = "../data" 

    # 1. Get file list
    files = get_file_list(data_dir)

    results = []
    percentages = []

    # 2. Fit each file
    for i, filepath in enumerate(files):
        result = fit_two_lorentzian(filepath)

        results.append(result)
        percentages.append(result["percentages"])

        # 3. Plot each fit
        plot_fit(result, title=f"Sample {i+1}")

    # 4. Summary plot
    plot_percentages(percentages)

    plt.show()


if __name__ == "__main__":
    main()