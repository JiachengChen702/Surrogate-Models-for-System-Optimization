from src.utils.preprocessing import Preprocessing
from src.models.abstractNN import AbstractNN
from typing import Dict, Optional, Any
import tensorflow as tf #2.15.0 in colab
import tensorflow.keras as keras
import cirq
import sympy
import tensorflow_quantum as tfq
import numpy as np
import matplotlib.pyplot as plt

class QNN(AbstractNN):
    
    # - the naive flag sets up a very early implementation of the model that does not implement a custom input mapping.
    #   Thus, data reuploading is not possible, but it was the only model that ever produced a usable outcome
    #   (probably due to luck in the weight initialization and thus not reproducable)
    # - the custom_scaler flag set to 'True' undoes the scaling done in the preprocessing module and applies a custom scaling
    def __init__(self, preprocessor: Preprocessing, config: Optional[Dict[str, Any]] = None, naive = False, custom_scaler = True):
        self.custom_scaler = custom_scaler
        self.naive = naive
        super().__init__(preprocessor, config)
        

    # used for custom scaling of the input data, since the author of this model does not trust the scikit-skalers
    # (due to bad handling of outliers or incorrect scaling to [-1,1])
    def transform_train_val_data(self):
        self.preprocessor.train_x = self.preprocessor.scaler.inverse_transform(self.preprocessor.train_x)
        self.preprocessor.val_x = self.preprocessor.scaler.inverse_transform(self.preprocessor.val_x)
        scales = [np.max(abs(np.concatenate([self.preprocessor.train_x.T[i], self.preprocessor.train_y.T[i], self.preprocessor.val_x.T[i], self.preprocessor.val_y.T[i]]))) for i in range (self.preprocessor.train_x.shape[1])]
        self.preprocessor.train_x /= scales
        self.preprocessor.train_y /= scales
        self.preprocessor.val_x /= scales
        self.preprocessor.val_y /= scales
        self.scales = scales

    def build_model(self, config: Dict[str, Any], input_shape: int = None) -> keras.Sequential:
        if input_shape is None:
            input_shape = self.preprocessor.train_x.shape[1]
        return build_model(config, input_shape, self.naive)


    # the plot_weights flag tells the model to plot a barplot of the different parameters (and input weights if enabled) at the end of training.
    # This way, one can tell if the model "decides" to e.g. ignore input (set its weight to 0)
    def run(self, epochs: int = 100, batch_size: int = 8, plot_weights = False):

        # scaler is fitted in the run() function since the training dataset should contain the most extreme examples.
        if self.custom_scaler:
            self.transform_train_val_data()
        
        print(f"symbols used in the model: {self.model.layers[0].symbols}")
        self.history = self.model.fit(
            tfq.convert_to_tensor([angle_encoding_circuit(val) for val in self.preprocessor.train_x]) if self.naive else self.preprocessor.train_x, # tfq.PQC needs tensord input circuits
            self.preprocessor.train_y,
            validation_data = (tfq.convert_to_tensor([angle_encoding_circuit(val) for val in self.preprocessor.val_x]) if self.naive else self.preprocessor.val_x, 
                self.preprocessor.val_y),
            epochs = epochs,
            batch_size = batch_size
            )
        if plot_weights and not self.naive:
            weights = np.concatenate([np.array(self.model.layers[0].trainable_variables[0][0]), np.array(self.model.layers[0].trainable_variables[1])])
            for i in weights:
                print(i)
            plt.bar(np.linspace(0, len(weights), num = len(weights)), weights, tick_label = self.model.layers[0].symbols)
            plt.title("the different fitted weights represented graphically")
            plt.xticks(rotation=90)
            plt.show()

    def validate(self):
        loss, mae = self.model.evaluate(
            tfq.convert_to_tensor([angle_encoding_circuit(val) for val in self.preprocessor.val_x]) if self.naive else self.preprocessor.val_x,
            self.preprocessor.val_y,
            verbose=0)
        print(f"Validierungsverlust: {loss}, MAE: {mae}")
        self.preprocessor.val_y = self.preprocessor.scaler.inverse_transform(self.preprocessor.val_y)



    def predict(self, step_size:int=10**10):
        self.step_size = step_size

        # the test dataset is scaled down just like the training dataset.
        test_x = self.preprocessor.scaler.inverse_transform(self.preprocessor.test_x)/self.scales
    
        def func(input_state: np.ndarray | None = None) -> np.ndarray:
            if self.naive:
                return tfq.convert_to_tensor([angle_encoding_circuit(input_state[0])])
            else:
                return input_state

        result = []

        # the next state is recursively predicted and reset to the simulation once the step_size is reached.
        for step in range(test_x.shape[0]):
            if step % step_size == 0:
                input_state = np.array([test_x[step]])
            input_state = self.model.predict(func(input_state), verbose = 0)
            result.append(input_state[0])

        # prediction is scaled up afterwards
        self.prediction = np.array(result)
        self.prediction*=self.scales
    
    def predict_one_step(self):
        self.one_step_prediction = self.model.predict(self.preprocessor.test_x, verbose = 0)

    def save_model(self, filename: str =  "data/model"):
        # this function only saves the rotation parameters, not the input weights
        print("saving model parameters as " + filename + ".npy")
        weights = []
        for i in self.model.layers[0].trainable_variables[0]:
            weights.append(np.array(i))
        np.save(filename, np.array(self.model.layers[0].trainable_variables[0][0]))

    def load_model(self, filename: str = "data/model"):
        # this function only implements the loading of the rotation parameters, not the input weights
        print("loading model parameters from " + filename + ".npy")
        self.model.layers[0].set_weights([np.array([np.load(filename+".npy")])])


@keras.utils.register_keras_serializable(package='QML')
class ReUploadQC(tf.keras.layers.Layer):
    def __init__(self, n_qubits, config, obs, activation = 'linear', initializer=tf.keras.initializers.HeNormal()) -> None:
        super(ReUploadQC, self).__init__()
        tf.debugging.set_log_device_placement(True)
        self.n_qubits = n_qubits
        self.activation = activation
        self.n_reupl_layers = 1
        try:
            for layer in config['layers']:
                if layer == 'reuploading':
                    self.n_reupl_layers += 1
        except:
            self.n_reupl_layers = 1
        circuit, theta_symbols, input_symbols = self.generateCircuit(n_qubits, config, self.n_reupl_layers)
        theta_init = tf.keras.initializers.RandomUniform(minval = 0.0, maxval = np.pi)
        self.theta = tf.Variable(initial_value=theta_init(
            shape=(1, len(theta_symbols)), dtype="float32"),
                                 trainable=True,
                                 name="thetas")

        lmbd_init = tf.ones(len(input_symbols),)

        # the following section can be commented in if a learnable input weighting is desired.
        '''self.lmbd = tf.Variable(initial_value=lmbd_init,
                                dtype="float32",
                                trainable=True,
                                name="lambdas")
        '''
        self.symbols = [str(symb) for symb in theta_symbols + input_symbols]
        
        self.indices = tf.constant([self.symbols.index(a) for a in sorted(self.symbols)])
        

        self.empty_circuit = tfq.convert_to_tensor([cirq.Circuit()]) #needed for batch initialization
        self.computation_layer = tfq.layers.ControlledPQC(circuit, obs)

    def call(self, inputs):
        # Batch size
        batch_dim = tf.gather(tf.shape(inputs), 0)

        # Expand inputs for re-uploading, if necessary

        inputs_expanded = tf.concat([inputs for i in range(self.n_reupl_layers)], axis=1)

        # Repeat circuits for the batch
        circuits = tf.repeat(self.empty_circuit, repeats=batch_dim)
        

        # Use broadcasting to align theta with batch size
        tiled_up_thetas = tf.broadcast_to(self.theta, [batch_dim, tf.shape(self.theta)[1]])

        # the following section can be commented in if a learnable input weighting is desired
        '''if (self.n_reupl_layers != 0):
            scaled_inputs = tf.einsum("i,ji->ji", self.lmbd, inputs_expanded)
            squashed_inputs = tf.keras.layers.Activation(
                self.activation)(scaled_inputs)
        else:'''
        squashed_inputs = inputs_expanded


        # Concatenate theta and inputs without tiling
        joined_vars = tf.concat([tiled_up_thetas, squashed_inputs], axis=1)
        joined_vars = tf.gather(joined_vars, self.indices, axis = 1)

        # Compute output using PQC layer
        res = self.computation_layer([circuits, joined_vars])

        return 2*res-1 #circuit is expected to return values [0,1] but dataset is scaled to [-1, 1]
    
    def generateCircuit(self, n_qubits, config, n_re):
        try:
            config['layers'] 
        except:
            print("config dictionary contains no \'layers\':[String] entry. Defaulting to one circuit11")
            config = {'layers':['circuit11']}
        grid = [cirq.GridQubit(0,i) for i in range (n_qubits)]
        params = np.asarray(sympy.symbols(f'theta(0:{varCountFromConfig(config, n_qubits)})'))
        inputs = np.asarray(sympy.symbols(f'x(0:{n_qubits*n_re})'))

        
        return self.resolve_config(config, params, inputs, grid), list(params.flat), list(inputs.flat)

    def resolve_config(self, config, params, inputs, grid):
        circuit, symbol_offset, inp_offset = self.reuploading(grid, inputs, 0)
        for layer in config['layers']:
            circ, n_symb, n_inp = self.call_layer_function(layer, params, inputs, grid, symbol_offset, inp_offset)
            symbol_offset += n_symb
            circuit += circ
            inp_offset += n_inp
        print(circuit)
        return circuit

    def call_layer_function(self, layer, params, inputs, grid, symbol_offset, inp_offset):
        match layer:
            case 'circuit11':
                return self.circuit11(grid, symbol_offset, params, inp_offset)
            case 'circuit19':
                return self.circuit19(grid, symbol_offset, params, inp_offset)
            case 'reuploading':
                return self.reuploading(grid, inputs, inp_offset)


    def circuit11 (self, grid, symbol_offset: int, theta, inp_offset):
        # n: amount of qubits
        n = len(grid)
        register = grid 
        out = cirq.Circuit()
        index = 0
        for i in range (int(n/2)):
            for k in range (int(n/2)-i):
                out = self.circuit11Helper(out, register, 2*k+i, theta, index+symbol_offset)
                index = index + 4
        return cirq.Circuit(out), n*int(n/2)+n, 0

    def circuit11Helper(self, circuit, register, registerIndex, theta, thetaIndex):
        circuit.append(cirq.ry(theta[thetaIndex])(register[registerIndex]))
        circuit.append(cirq.rz(theta[thetaIndex+1])(register[registerIndex]))
        circuit.append(cirq.ry(theta[thetaIndex+2])(register[registerIndex+1]))
        circuit.append(cirq.rz(theta[thetaIndex+3])(register[registerIndex+1]))
        circuit.append(cirq.CNOT(register[registerIndex], register[registerIndex+1]))
        return circuit

    def circuit19(self, grid, symbol_offset: int, theta, inp_offset):
        register = grid
        n = len(grid)
        out = cirq.Circuit()
        for i in range(n):
            out.append(cirq.rx(theta[2*i+symbol_offset])(register[i]))
            out.append(cirq.rz(theta[2*i+1+symbol_offset])(register[i]))
        for i in range(n):
            out.append(cirq.CNOT(register[n-i-1], register[-i%n]))
            out.append(cirq.rx(theta[2*n+i+symbol_offset])(register[-i%n]))
            out.append(cirq.CNOT(register[n-i-1], register[-i%n]))
        return cirq.Circuit(out), 3*n, 0

    def reuploading(self, grid, input_data, inp_offset):
        qubits = grid
        n = len(grid)
        circuit = cirq.Circuit()
        for i in range(n):
            circuit.append(cirq.rx(input_data[i+inp_offset])(qubits[i]))
        return circuit, 0, n

def build_model(config=None, input_shape = None, naive = False):
    try:
        config['layers']
        #debug 
        print(f"Config layers: {config['layers']}")
    except:
        print("config dictionary contains no \'layers\':[String] entry. Defaulting to one circuit11")
        config = {'layers':['circuit11']}
    grid = [cirq.GridQubit(0,i) for i in range (input_shape)]
    if naive:
        model = keras.Sequential([
            keras.layers.Input(shape=(), dtype=tf.string),
            tfq.layers.PQC(
            resolve_config(config, input_shape),
                [cirq.Z(q) for q in grid]),     #measurement observables
            ])
    else:    
        model = keras.Sequential([
            keras.layers.Input(shape=(input_shape,), dtype=tf.float32),
            ReUploadQC(input_shape, config,
                [cirq.Z(q) for q in grid]),     #measurement observables
            ])
    
    return model

def varCountFromConfig(config, n_qubits):
    n_params = 0
    for layer in config['layers']:
        match layer:
            case 'circuit11':
                n_params += n_qubits*int(n_qubits/2)+n_qubits
            case 'circuit19':
                n_params += 3*n_qubits
    return n_params

# The following functions are logically equivalent to thir counterparts in the ReUploadQC() class.
# They are a relict from a past implementation and only used if model type is set to 'naive'

def resolve_config(config, input_shape, index = 0):
    circuit, symbol_offset = call_layer_function(config['layers'][0], input_shape, 0)
    for layer in config['layers'][1:]:
        circ, n_symb = call_layer_function(layer, input_shape, symbol_offset)
        symbol_offset += n_symb
        circuit += circ
    return circuit

def call_layer_function(layer_name, input_shape, symbol_offset):
    match layer_name:
        case 'circuit11':
            return circuit11(n = input_shape, symbol_offset = symbol_offset)
        case 'circuit19':
            return circuit19(n = input_shape, symbol_offset = symbol_offset)
    return None



def circuit11Helper(circuit, register, registerIndex, theta, thetaIndex):
    circuit.append(cirq.ry(theta[thetaIndex])(register[registerIndex]))
    circuit.append(cirq.rz(theta[thetaIndex+1])(register[registerIndex]))
    circuit.append(cirq.ry(theta[thetaIndex+2])(register[registerIndex+1]))
    circuit.append(cirq.rz(theta[thetaIndex+3])(register[registerIndex+1]))
    circuit.append(cirq.CNOT(register[registerIndex], register[registerIndex+1]))
    return circuit


def circuit11 (n: int = 10, symbol_offset: int = 0):
    # n: amount of qubits 
    register = [cirq.GridQubit(0,i) for i in range(n)]
    out = cirq.Circuit()
    theta = sympy.symbols(f'theta({symbol_offset}:{symbol_offset+n*int(n/2)+n})')
    index = 0
    for i in range (int(n/2)):
        for k in range (int(n/2)-i):
            out = circuit11Helper(out, register, 2*k+i, theta, index)
            index = index + 4
    return cirq.Circuit(out), n*int(n/2)+n

def circuit19(n: int = 10, symbol_offset: int = 0):
    register = [cirq.GridQubit(0,i) for i in range(n)]
    out = cirq.Circuit()
    theta = sympy.symbols(f'theta({symbol_offset}:{symbol_offset+3*n}')
    for i in range(n):
        out.append(cirq.rx(theta[2*i])(register[i]))
        out.append(cirq.rz(theta[2*i+1])(register[i]))
    for i in range(n):
        out.append(cirq.CNOT(register[n-i-1], register[-i%n]))
        out.append(cirq.rx(theta[2*n+i])(register[-i%n]))
        out.append(cirq.CNOT(register[n-i-1], register[-i%n]))
    return cirq.Circuit(out), 3*n


def angle_encoding_circuit(input_data):
    qubits = [cirq.GridQubit(0,i) for i in range(len(input_data))]
    circuit = cirq.Circuit()
    for i, value in enumerate(input_data):
        circuit.append(cirq.rx(value)(qubits[i]))
    return circuit

