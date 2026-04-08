from abc import ABC, abstractmethod # handle name for abstract classes
from file_util import load_two_column_file

# Now this class is abstract, parent class
# Private variables: 
    # file path(HARD CODE)
    # data: raw data
    # results: calculated data
class DataSet(ABC):
    #Contructor
    def __init__(self, filepaths):
        self.filepaths = filepaths
        self.data = []
        self.results = []

    #load all the data by calling file_util
    def load_all(self):
        self.data = []

        for filepath in self.filepaths:
            x, y = load_two_column_file(filepath)
            self.data.append({
                "filepath": filepath,
                "x": x,
                "y": y
            })

    # 2 abstract methods

    # plot fit
    @abstractmethod
    def plot_fits(self):
        """
        Each child class must implement its own fit plotting.
        """
        pass

    #plot percentages
    @abstractmethod
    def plot_percentages(self):
        """
        Each child class must implement its own percentage plotting.
        """
        pass
    
    # child finds its own fit method and does the fit
    @abstractmethod
    def fit(self):
        pass