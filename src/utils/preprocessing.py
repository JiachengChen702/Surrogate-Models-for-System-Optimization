import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

class Preprocessing:
    def __init__(self):
        self.train_x, self.train_y, self.val_x, self.val_y = None, None, None, None
        self.test_x, self.test_y = None, None
        self.row_tuples_combined = None
        self.csv_array = None
        self.scaler = StandardScaler()


    def read_csv(self, folder_name: str = "train_data", amount_of_files = 10000):
        amount = 0 #added so the QNN can predict on less datasets for testing. Default set to 10K since we probably wont be reading that many
        csv_array = []
        for file_name in os.listdir(folder_name):
            if file_name.endswith(".csv") and amount < amount_of_files:
                file_path = os.path.join(folder_name, file_name)
                csv_array.append(pd.read_csv(file_path)[:-1])
                amount += 1
        self.csv_array = csv_array
        self.row_tuples_combined = self.combine_tuples()


    def combine_tuples(self):
        row_tuples_combined = []
        for _, df in enumerate(self.csv_array):
            df = df.drop("time", axis=1)
            row_tuples = [(df.iloc[i], df.iloc[i+1]) for i in range(len(df) - 1)]
            row_tuples_combined.extend(row_tuples)
        
        return row_tuples_combined


    def plot_desired_variable(self, variable_to_plot="heatCapacitor.T"):

        plt.figure(figsize=(8, 5))

        for _, df in enumerate(self.csv_array): plt.plot(df["time"], df[variable_to_plot])

        plt.title(f"{variable_to_plot} over time.")
        plt.xlabel("Time t")
        plt.ylabel(variable_to_plot)
        plt.legend()
        plt.grid()
        plt.show()


    def split_dataset(self, train_split_ratio=0.7):
        train_arr, val_arr = train_test_split(self.row_tuples_combined, train_size=train_split_ratio)

        self.train_x = np.array([x[0] for x in train_arr]) # Features for training
        self.scaler.fit(self.train_x)
        self.train_x = self.scaler.transform(self.train_x)
        self.train_y = np.array([x[1] for x in train_arr])  # Targets for training
        self.val_x = np.array([x[0] for x in val_arr])  # Features for validation
        self.val_x = self.scaler.transform(self.val_x)
        self.val_y = np.array([x[1] for x in val_arr])  # Targets for validation

        print(f"Number of training samples: {len(self.train_x)}")


    def test_dataset(self):
        self.test_x = np.array([x[0] for x in self.row_tuples_combined])  # Features for testing
        self.test_x = self.scaler.transform(self.test_x)
        self.test_y = np.array([x[1] for x in self.row_tuples_combined])  # Targets for testing