from file_util import get_file_list_standard, get_file_list
from dataset import DataSet
from fitters import SpectralFitter
import matplotlib.pyplot as plt

def main():

    data_dir = "../data"

    # 1. Get files
    measurement_files,standard_files = get_file_list_standard(data_dir)
    raman_file = get_file_list(data_dir)  

    # 2. Create analysis object
    dataset_decomp = DataSet(measurement_files)
    dataset_decomp.load_all()

    dataset_raman = DataSet(raman_file)
    dataset_raman.load_all

    # 3.  Create fitter obj
    fitter_decomp = SpectralFitter(standard_files=standard_files)
    fitter_Raman = SpectralFitter(standard_files=raman_file)

    # fit and plot
    dataset_decomp.apply_standard_fit(fitter_decomp)
    dataset_decomp.plot_standard_fits()
    dataset_decomp.plot_percentages()

    dataset_raman.apply_lorentz_fit(fitter_Raman)
    #dataset_raman.plot_lorentz_fits()
    #dataset_raman.plot_percentages()
    
    plt.show()


if __name__ == "__main__":
    main()