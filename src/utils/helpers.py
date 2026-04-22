import pandas as pd

from src.utils.preprocessing import Preprocessing
from src.models.ANN import ANN
import json


def create_dataset_evaluation(configs: list[str] = ["train_data_config.json"], train_datasets: list[str]= ["train_data"], test_datasets: list[str]= ["test_data"], n_array: list[int] = [1, 100, 1000]):
    results = {}
    for config, train_dataset, test_dataset in zip(configs, train_datasets, test_datasets): 
        preprocessor = Preprocessing()
        preprocessor.read_csv(folder_name=train_dataset)
        preprocessor.split_dataset(train_split_ratio=0.7)
        with open(config, "r") as f:
            config = json.load(f)
        ann = ANN(preprocessor, config=config, model_name=train_dataset)
        ann.run()
        ann.preprocessor.read_csv(folder_name=test_dataset)
        ann.preprocessor.test_dataset()
        output = ann.save_results(n_array)
        results[train_dataset] = output
    return pd.DataFrame(results, index=n_array)


if __name__ == "__main__":
    df = create_dataset_evaluation()
    print(df)