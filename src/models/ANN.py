import tensorflow.keras as keras
from keras.callbacks import ModelCheckpoint
import numpy as np
from typing import Dict, Optional, Any
import logging

from src.utils.preprocessing import Preprocessing
from src.models.abstractNN import AbstractNN

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(), logging.FileHandler('model_execution.log')]
)
logger = logging.getLogger()


class ANN(AbstractNN):
    def __init__(self, preprocessor: Preprocessing, config: Optional[Dict[str, Any]] = None, model_name: str = "ANN"):
        #default model, if no config is passed
        default_config = {
        "neurons_input": 10,
        "activation_input": "linear",
        "anzahl_hidden": 2,
        "neurons_hidden": [10, 10],
        "activation_hidden": ["relu", "relu"],
        "neurons_output": 10,
        "activation_output": "linear",
        'optimizer': 'adam'
    }
        if config is None:
            config = default_config
        super().__init__(preprocessor, config) 

        self.model_name = model_name
        logger.info(f"Model structure: {self.model.summary()}")


    def build_model(self, config: Dict[str, Any], input_shape: int) -> keras.Sequential:
        return build_model(config, input_shape)


    def run(self, epochs: int = 100, batch_size: int = 8):
        logger.info("Starting model training...")
        try:
            checkpoint = ModelCheckpoint(
                filepath=f'model/{self.model_name}.keras',
                monitor='val_loss',
                save_best_only=True,
                mode='min'
            )

            self.history = self.model.fit(
                self.preprocessor.train_x, 
                self.preprocessor.train_y, 
                validation_data=(self.preprocessor.val_x, self.preprocessor.val_y), 
                epochs=epochs, 
                batch_size=batch_size,
                callbacks=[checkpoint]
            )
            logger.info("model training complete")

            self.load_model(f'model/{self.model_name}.keras')
        except Exception as e:
            logger.error(f"Error during model training: {str(e)}")
            raise


    def validate(self):
        loss, mae = self.model.evaluate(self.preprocessor.val_x, self.preprocessor.val_y, verbose=0)
        logger.info(f"Validierungsverlust: {loss}, MAE: {mae}")


    def predict(self, step_size:int=10**10):
        return super().predict(step_size)


    def predict_one_step(self):
        logger.info("predicting onestep...")
        self.one_step_prediction = self.model.predict(self.preprocessor.test_x)


def build_model(config=None, input_shape=10):
    #create a default model with if config, if no config is passed
    default_config = {
        "neurons_input": input_shape,
        "activation_input": "linear",
        "anzahl_hidden": 2,
        "neurons_hidden": [10, 10],
        "activation_hidden": ["relu", "relu"],
        "neurons_output": 10,
        "activation_output": "linear",
        'optimizer': 'adam'
    }

    if config is None:
        config = default_config

    model = keras.Sequential()

    # Input Layer
    model.add(keras.layers.Dense(config['neurons_input'], input_shape=(input_shape,), activation=config['activation_input']))

    # Hidden Layers 
    for i in range(config['anzahl_hidden']):
        model.add(keras.layers.Dense(
            config['neurons_hidden'][i], 
            activation=config['activation_hidden'][i]))

    # Output Layer 
    model.add(keras.layers.Dense(
        units=config['neurons_output'],  
        activation=config['activation_output']  
    ))

    return model