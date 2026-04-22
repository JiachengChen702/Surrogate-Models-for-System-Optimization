import tensorflow.keras as keras
import tensorflow as tf
from kerastuner import Hyperband
from keras_tuner import Objective
from keras.callbacks import Callback
from src.models.ANN import build_model
import logging
from keras.callbacks import EarlyStopping
#from src.models.QNN import QNN
#from src.models.QNN import build_model
#import tensorflow_quantum as tfq
#import cirq
#import random



# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(), logging.FileHandler('model_execution.log')]
)

logger = logging.getLogger()


# Had Problem calling error() from AbstractNN.py. ->Set the tuning objective back to val_loss 
class CustomErrorCallback(Callback):
    def on_epoch_end(self, epoch, logs=None):
        # Should: min. of error() in AbstractNN.py
        val_loss = logs.get('val_loss')  # Standard validation loss
        logs['val_loss'] = val_loss
        logger.info(f"Epoch {epoch + 1} - val_loss: {val_loss}")

def tune_model(preprocessor,write_folder):
    logger.info("Starting model tuning process...")
      
    def model_builder(hp):
        # Define Hyperparameters search space with a dictionary
        
        
        """Search Space nach Config1 individuell verkleinert, damit Konvergenz schneller erreicht wird
            -simpleheating:
            activation: 'relu','linear'
            optimizer: 'adam', 'nadam'
            ..
            
            -capacitator:
            activation:'relu','linear',
            optimizer: 'adam', 'nadam'
            ..
            
            -chua:
            activation:'relu','linear'
            optimizer: 'adam',
            
            -osci:
            activation:'relu','linear'
            optimizer: 'adam',
            
            -coolingnetw:
            activation:'relu','linear'
            optimizer: 'adam','nadam'
            
            -simplecooling:
            activation:'relu','linear'
            optimizer: 'adam','nadam'
        """
        Search_Space = {
            'neurons_input': preprocessor.train_x.shape[1],  # fixed
            'neurons_hidden': hp.Int('neurons_hidden', min_value=10, max_value=100),
            'activation': hp.Choice('activation', values=['relu','linear']),

            #not used, in "current" config local defined
            'anzahl_hidden': hp.Int('anzahl_hidden', min_value=1, max_value=4),
            'neurons_output': preprocessor.train_y.shape[1],  
            #'dropout_rate': hp.Float('dropout_rate', min_value=0.0, max_value=0.5, step=0.1),
             
            'optimizer': hp.Choice('optimizer', values=['adam','nadam']),            
            'learning_rate': hp.Float('learning_rate', min_value=1e-5, max_value=1e-2, sampling="log"),

        }

        # "current" config in trial
        config = {
            "input_shape": (preprocessor.train_x.shape[1],),    
            "neurons_input": Search_Space['neurons_input'],
            "activation_input": Search_Space['activation'],
            
            "anzahl_hidden": Search_Space["anzahl_hidden"],
            "neurons_hidden": [hp.Int(f"neurons_hidden_{i}", min_value=10, max_value=100) for i in range(Search_Space["anzahl_hidden"])],
            "activation_hidden": [hp.Choice(f"activation_hidden_{i}", values=['relu']) for i in range(Search_Space["anzahl_hidden"])],
            #"dropout_rate": [hp.Float(f"dropout_rate_{i}", min_value=0.0, max_value=0.5, step=0.1) for i in range(Search_Space["anzahl_hidden"])],
            
            "neurons_output": Search_Space['neurons_output'],
            "activation_output": Search_Space['activation'],
            
            "optimizer": Search_Space['optimizer'],
            "learning_rate": Search_Space['learning_rate'],
            "loss": "mean_squared_error",
            "metrics": ["mse"],
        }

        # Debug
        logger.info("Config in model_builder:", config)
        
        # Overwrite the default learning rate in the optimizer with a tuned learing rate
        optimizer = Search_Space['optimizer']
        #learning_rate = Search_Space['learning_rate']
        
        #uses default learning rate by leaving out the parameter
        if optimizer == 'adam':
            optimizer_instance = keras.optimizers.Adam(Search_Space['learning_rate'])
        else:  # nadam
            optimizer_instance = keras.optimizers.Nadam(Search_Space['learning_rate'])

        # Use the build_model function with the config
        model = build_model(config, preprocessor.train_x.shape[1])

        # Compile the model
        model.compile(
            optimizer=optimizer_instance,
            loss=keras.losses.MeanSquaredError(
                reduction='sum_over_batch_size',
                name='mean_squared_error'
            ),
            metrics=['mse']  
        )
        return model

    # Define val_loss as an objective to minimize
    custom_objective = Objective("val_loss", direction="min")

    tuner = Hyperband(
        model_builder,
        # Goal of optimization
        objective=custom_objective,
        max_epochs=100,
        factor = 2, # halving factor
        directory='ann',
        project_name=write_folder,
        seed=42
    )
    
    early_stopping = EarlyStopping(
    monitor='val_loss',
    patience=15,  # Stop training if no improvement after 15 epochs
    restore_best_weights=True
)

    try:
        # Search for the best hyperparameters
        tuner.search(preprocessor.train_x, preprocessor.train_y,
                     epochs=100, validation_data=(preprocessor.val_x, preprocessor.val_y),
                     callbacks=[CustomErrorCallback(), early_stopping])
    except Exception as e:
        logger.error(f"Error during tuning: {e}")
        return None

    try:
        # Get the best hyperparameters configuration
        best_hps = tuner.get_best_hyperparameters(num_trials=1)[0]
    except IndexError:
        logger.error("No best hyperparameters found. Tuning may have failed.")
        return None

    try:
        # Construct best_config using the best hyperparameters
        anzahl_hidden = best_hps.get("anzahl_hidden")
        
        best_config = {
            "input_shape": (preprocessor.train_x.shape[1],),
            "neurons_input": preprocessor.train_x.shape[1],  # Directly use train_x shape here
            "activation_input": best_hps.get("activation"),

            "anzahl_hidden": anzahl_hidden,
            "neurons_hidden": [best_hps.get(f"neurons_hidden_{i}") for i in range(anzahl_hidden)],
            "activation_hidden": [best_hps.get(f"activation_hidden_{i}") for i in range(anzahl_hidden)],
            #"dropout_rate": [best_hps.get(f"dropout_rate_{i}") for i in range(anzahl_hidden)],

            "neurons_output": preprocessor.train_y.shape[1],
            "activation_output": best_hps.get("activation"),

            "optimizer": best_hps.get("optimizer"),
            "learning_rate": best_hps.get("learning_rate"),
            "loss": "mean_squared_error",
            "metrics": ["mse"],  
        }
    except KeyError as e:
        logger.error(f"Error constructing best_config: {e}")
        return None

    logger.info(f"Best Configuration from Hyperband: {best_config}")


    return best_config


#-------------------------------------QNN----------------------------------------------------


def tune_model_QNN(preprocessor):

    def build_qnn_model(hp):
        # Search Space for the hyper parameters.
        num_circuit11 = hp.Int('num_circuit11', min_value=1, max_value=3)
        num_circuit19 = hp.Int('num_circuit19', min_value=1, max_value=3)
        optimizer_choice = hp.Choice('optimizer', values=['adam', 'nadam'])
        learning_rate = hp.Float('learning_rate', min_value=1e-6, max_value=1e-2, sampling='log')
        batch_size = hp.Int('batch_size', min_value=4, max_value=32, step=4)
        
        layers = ['circuit11'] * num_circuit11 + ['circuit19'] * num_circuit19
        random.shuffle(layers)  # Randomize the order of layers
        # Config dictionary to be passed to build_model in QNN.py
        config = {
            'layers' : layers,
            'optimizer': optimizer_choice,
            'learning_rate': learning_rate,
            'batch_size': batch_size,
            'loss': 'mean_squared_error',
            'metrics': ['mse']
        }
        
        #We have two build_model functions in projects. Creating QNN model to make sure it is calling 
        #build_model from QNN.py
        qnn = QNN(preprocessor, config)
        model = qnn.build_model(config, input_shape=preprocessor.train_x.shape[1])
        
        # overwrite the default learinig rate in optimizers with the tuned one.
        if optimizer_choice == 'adam':
            optimizer_instance = tf.keras.optimizers.Adam(learning_rate=learning_rate)
        else:  # nadam
            optimizer_instance = tf.keras.optimizers.Nadam(learning_rate=learning_rate)

        model.compile(optimizer=optimizer_instance, loss=config['loss'], metrics=config['metrics'])
        return model
    
    # Initialize tuner
    tuner = Hyperband(
        build_qnn_model,
        objective='val_loss',
        max_epochs=10,
        factor=3,
        directory='qnn_tuning',
        project_name='qnn_hyperparameter_tuning',
        overwrite=True
    )
    
    # Start tuning
    tuner.search(preprocessor.train_x, preprocessor.train_y, epochs=10, validation_data=(preprocessor.val_x, preprocessor.val_y), batch_size=32)
    
    try:
        # Get the best hyperparameters configuration
        best_hps = tuner.get_best_hyperparameters(num_trials=1)[0]
    except IndexError:
        logger.error("No best hyperparameters found. Tuning may have failed.")
        return None
    
    try:
        # Construct best_config using the best hyperparameters
        num_circuit11 = best_hps.get("num_circuit11")
        num_circuit19 = best_hps.get("num_circuit19")
        optimizer_choice = best_hps.get("optimizer")
        learning_rate = best_hps.get("learning_rate")
        batch_size = best_hps.get("batch_size")
        
        layers = ['circuit11'] * num_circuit11 + ['circuit19'] * num_circuit19
        random.shuffle(layers)  # Randomize the order of layers
        
        best_config = {
            "input_shape": (preprocessor.train_x.shape[1],),
            "layers": layers,
            "optimizer": optimizer_choice,
            "learning_rate": learning_rate,
            "batch_size": batch_size,
            "loss": "mean_squared_error",
            "metrics": ["mse"]
        }
    except KeyError as e:
        logger.error(f"Error constructing best_config: {e}")
        return None
    
    #Debug:
    logger.info(f"Best Configuration from Hyperband: {best_config}")
    
    
    return best_config

