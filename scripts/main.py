from file_util import get_file_list_standard, get_file_list
from decomp_stand import DecompDataSet
from raman import RamanDataSet
from fitters import SpectralFitter
import matplotlib.pyplot as plt

# currently basically just hard code tests to make sure that everything is working
def main():
    data_dir = "../data"

    # 1. Get files
    measurement_files, standard_files = get_file_list_standard(data_dir)
    raman_files = get_file_list(data_dir)

    # 2. Create dataset objects
    dataset_decomp = DecompDataSet(measurement_files)
    dataset_decomp.load_all()

    dataset_raman = RamanDataSet(raman_files)
    dataset_raman.load_all()

    # 3. Create fitter objects
    fitter_decomp = SpectralFitter(standard_files=standard_files)
    fitter_raman = SpectralFitter()

    # 4. Decomposition fit + plots
    dataset_decomp.fit(fitter_decomp)
    #dataset_decomp.plot_fits()
    #dataset_decomp.plot_percentages()

    # 5. Raman fit + plots
    dataset_raman.fit(fitter_raman, n_peaks=2)
    dataset_raman.plot_fits()
    dataset_raman.plot_percentages()

    # 6. Optional: grain size metric
    grain_results = dataset_raman.calculate_grain_size_metric()
    print("\nRaman grain size metric results:")
    for item in grain_results:
        print(item)

    plt.show()


if __name__ == "__main__":
    main()