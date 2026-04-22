import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import tensorflow.keras as keras
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any

from src.utils.preprocessing import Preprocessing


class AbstractNN(ABC):
    def __init__(self, preprocessor: Preprocessing, config: Optional[Dict[str, Any]] = None):
        self.preprocessor = preprocessor
        self.prediction = None
        self.one_step_prediction = None
        self.config = config
        self.history = None
        self.results = None
        self.step_size: int | None = None

        if preprocessor.train_x is None or preprocessor.train_y is None:
            raise ValueError("Training data is not properly loaded.")
        if preprocessor.val_x is None or preprocessor.val_y is None:
            raise ValueError("Validation data is not properly loaded.")


        # create a model with config from Hyperband Tuner
        self.model = self.build_model(config, self.preprocessor.train_x.shape[1])
        
        '''if config['optimizer'] == 'adam': 
            if 'learning_rate' in config: 
                optimizer_instance = keras.optimizers.Adam(learning_rate=config['learning_rate']) 
            else: optimizer_instance = keras.optimizers.Adam()
        elif config['optimizer'] == 'nadam': 
            if 'learning_rate' in config: 
                optimizer_instance = keras.optimizers.Nadam(learning_rate=config['learning_rate']) 
            else: optimizer_instance = keras.optimizers.Nadam()'''

        if not 'optimizer' in config:
            config['optimizer'] = 'adam'
            print("No optimizer found in config. Defaulting to Adam")

        match config['optimizer']:
            case 'adam':
                optimizer_instance = keras.optimizers.Adam(learning_rate=config['learning_rate']) if 'learning_rate' in config else keras.optimizers.Adam()
            case 'nadam':
                optimizer_instance = keras.optimizers.Nadam(learning_rate=config['learning_rate']) if 'learning_rate' in config else keras.optimizers.Nadam()
            case 'adamw':
                optimizer_instance = keras.optimizers.AdamW(learning_rate=config['learning_rate']) if 'learning_rate' in config else keras.optimizers.AdamW()
            case 'lion':
                optimizer_instance = keras.optimizers.Lion(learning_rate=config['learning_rate']) if 'learning_rate' in config else keras.optimizers.Lion()
        self.model.compile(
            optimizer=optimizer_instance,
            #fixed
            loss=keras.losses.MeanSquaredError(
                reduction='sum_over_batch_size',
                name='mean_squared_error'
            ), 
            metrics=['mse']
        )


    @abstractmethod
    def build_model(self, config: Dict[str, Any], input_shape: int) -> keras.Sequential:
        ...


    @abstractmethod
    def run(self, epochs: int = 100, batch_size: int = 8):
        ...


    ### ----------------------------------- Prediction ----------------------------------- ###

    def predict_wrapper(self, step_size: int = 10**10):
        self.step_size = step_size
        def wrapper(func):
            def inner(*args, **kwargs):
                result = []
                for step in range(self.preprocessor.test_x.shape[0]):
                    if step % step_size == 0:
                        input_state = np.array([self.preprocessor.test_x[step]])
                    input_state = self.model.predict(func(input_state))
                    result.append(input_state[0])
                    input_state = self.preprocessor.scaler.transform(input_state)
                self.prediction = np.array(result)
            return inner
        return wrapper


    @abstractmethod
    def predict(self, step_size:int=10**10):
        @AbstractNN.predict_wrapper(self, step_size)
        def func(input_state: np.ndarray | None = None) -> np.ndarray:
            return input_state
        return func()


    @abstractmethod
    def predict_one_step(self):
        ...


    def _setup_prediction(self, one_step: bool = False):
        if one_step:
            if self.one_step_prediction is None: self.predict_one_step()
        else:
            if self.prediction is None: self.predict()


    ### ----------------------------------- Error Calculation ----------------------------------- ###

    def _error_function(self, y_true, y_pred, error_type: str = 'mae') -> float:
        match error_type:
            case 'mse': return np.mean((y_true - y_pred) ** 2)
            case 'mae': return np.mean(np.abs(y_true - y_pred))
            case 'rmse': return np.sqrt(np.mean((y_true - y_pred) ** 2))
            case 'mase': return (np.mean(np.abs(y_true - y_pred)) / np.mean(np.abs(y_true[1:] - y_true[:-1])) 
                     if np.mean(np.abs(y_true[1:] - y_true[:-1])) != 0 else float('inf'))



    def error(self, variable_to_predict: int = 0, error_type: str = 'mae', one_step: bool = False) -> float:
        self._setup_prediction(one_step)
        return self._error_function(self.preprocessor.test_y[:, variable_to_predict], (self.one_step_prediction if one_step else self.prediction)[:, variable_to_predict], error_type)


    def naive_error(self, variable_to_predict: int = 0, error_type: str = 'mae') -> float:
        non_scaled_test_x = self.preprocessor.scaler.inverse_transform(self.preprocessor.test_x)
        length_test_x = len(non_scaled_test_x)
        repeated_array = np.array([non_scaled_test_x[i][variable_to_predict] for i in range(0, length_test_x, self.step_size) for _ in range(min(self.step_size, length_test_x))])
        repeated_array = repeated_array[:non_scaled_test_x.shape[0]]
        if self.step_size == 1:
            assert np.all(np.array(non_scaled_test_x[1:, variable_to_predict]) == repeated_array[1:])
        return self._error_function(non_scaled_test_x[:-1, variable_to_predict], repeated_array[1:], error_type)


    def relative_error(self, variable_to_predict: int = 0, error_type: str = 'mae', one_step: bool = False) -> float:
       
        return self.error(variable_to_predict, error_type, one_step=one_step) / self.naive_error(variable_to_predict, error_type)


    def evaluate_metrics(self, variable_to_predict: int = 0) -> pd.DataFrame:
        error_metrics = ['mae', 'mse', 'rmse']
        data = {
            'Prediction': [np.around(self.error(variable_to_predict, error_type=metric), 2) for metric in error_metrics],
            'One Step Prediction': [np.around(self.error(variable_to_predict, error_type=metric, one_step=True), 2) for metric in error_metrics],
            'Naive Model': [np.around(self.naive_error(variable_to_predict, error_type=metric), 2) for metric in error_metrics],
            'Relative Error': [np.around(self.relative_error(variable_to_predict, error_type=metric), 2) for metric in error_metrics]
        }
        self.results = pd.DataFrame(data, index=error_metrics)


    ### ----------------------------------- Plotting ----------------------------------- ###

    def plot_prediction(self, variable_to_predict: int = -1, baseline: bool = True, one_step: bool = False, save: bool = False, show = False, filename = ""):
        plt.cla()
        
        self._setup_prediction(one_step)
        prediction = self.one_step_prediction if one_step else self.prediction
        
        y = prediction[:, variable_to_predict]
        x = np.linspace(0, 1, num=len(y), endpoint=True)
        if (variable_to_predict == -1): #if left unused, all variables to be predicted are plotted to better observe dynamics in the model
            num_statevars = self.preprocessor.test_x.shape[1]
            n_cols = int((num_statevars+3)/5)
            fig, axs = plt.subplots(n_cols, int((num_statevars+2)/n_cols))
            axs = axs.flatten()
            plt.xlabel('Time t [s]')
            for i in range (num_statevars):
                axs[i].plot(x, prediction[:, i], label = 'prediction')
                axs[i].plot(x, self.preprocessor.test_y[:, i], label='baseline')
                axs[i].legend()
        else:
            plt.xlabel('Time t')
            plt.ylabel('Temperature T')
            plt.plot(x, y, label='prediction')
            if baseline:
                plt.plot(x, self.preprocessor.test_y[:, variable_to_predict], label='baseline')
            plt.legend()
        if show:
            plt.show()
        if save:
            if filename == "":
                filename = "model_prediction"
            plt.savefig(filename +".png")


    def plot_results(self):
        length = len(self.history.history['loss'][2:])
        plt.plot(list(range(2, length + 2)), self.history.history['loss'][2:], label='Trainingsverlust')
        plt.plot(list(range(2, length + 2)), self.history.history['val_loss'][2:], label='Validierungsverlust')
        plt.xlabel('Epochen')
        plt.ylabel('Verlust')
        plt.legend()
        plt.show()


    ### ----------------------------------- Save and Load ----------------------------------- ###

    def save_metric_results(self, save_type: str = 'csv', filename: str = "evaluation"):
        if self.results is None: self.evaluate_metrics()
        match save_type:
            case 'csv': self.results.to_csv(f'data/{filename}.csv')
            case 'json': self.results.to_json(f'data/{filename}.json')
            case 'latex': print(self.results.to_latex())

    
    def save_results(self, n_array: list[int] = [1, 100, 1000], variable_to_predict: int = 0):
        results = []
        for n in n_array:
            print("Calculating relative error for n =", n)
            self.predict(step_size=n)
            results.append(self.relative_error(variable_to_predict))
        return results


    def save_model(self, filename: str = "data/model"):
        self.model.save(filename)


    def load_model(self, filename: str = "data/model"):
        self.model = keras.models.load_model(filename)
