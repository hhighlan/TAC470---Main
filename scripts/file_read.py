import os
import numpy as np

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