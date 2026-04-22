import QNN
import preprocessing
import matplotlib.pyplot as plt
import numpy as np
import datetime

# This file could very well be implemented in a notebook but the author preferred to use a runfile.
# The queue represents a list of dicts that contain information of the model, such as name (must equal the folder of the train data) and hyperparameters.
# The queued executions will be logged to the specified logfile.
# The queue can be used to sweep hyperparameters manually or run different models consecutively.



runfolder = 'QNN_paper_runs/'
logfile = runfolder + 'QNN_log.txt'

architecture = ['circuit19','reuploading', 'circuit11']

# mode is either 'predict' or 'train'. 
# 	- 'predict' loads models expected to be saved in the runfolder and only executes the metrics.
# 	- 'run' only relies on the queue, saves the loss histories and evaluates the metrics.
mode = 'predict'


queue = [
		 {'name': 'simplecooling',	'epochs': 50, 'optimizer': 'adamw', 'layers': architecture, 'learning_rate': 0.0001, 'var': 0},
		 {'name': 'simpleheating',	'epochs': 50, 'optimizer': 'adamw', 'layers': architecture, 'learning_rate': 0.01, 'var': 0},
		 #{'name': 'capacitor',		'epochs': 50, 'optimizer': 'adamw', 'layers': architecture, 'learning_rate': 0.01, 'var': 1},
		 #{'name': 'coolingnetw',	'epochs': 50, 'optimizer': 'adamw', 'layers': architecture, 'learning_rate': 0.001, 'var': 0},
		 {'name': 'osci',			'epochs': 50, 'optimizer': 'adamw', 'layers': architecture, 'learning_rate': 0.01, 'var': 2},
		 {'name': 'chua',			'epochs': 50, 'optimizer': 'adamw', 'layers': architecture, 'learning_rate': 0.01, 'var': 0}

		 #{'name': 'capacitor', 'epochs': 300, 'optimizer': 'adamw', 'layers': architecture, 'learning_rate': 0.1},
		 #{'name': 'capacitor', 'epochs': 300, 'optimizer': 'adamw', 'layers': architecture, 'learning_rate': 0.01},
		 #{'name': 'capacitor', 'epochs': 300, 'optimizer': 'adamw', 'layers': architecture, 'learning_rate': 0.001},
		 #{'name': 'capacitor', 'epochs': 300, 'optimizer': 'adamw', 'layers': architecture, 'learning_rate': 0.0001},
		 #{'name': 'capacitor', 'epochs': 300, 'optimizer': 'adamw', 'layers': architecture, 'learning_rate': 0.00001},
		 #{'name': 'capacitor', 'epochs': 300, 'optimizer': 'adamw', 'layers': architecture, 'learning_rate': 0.000001}

		 #{'name': 'simplecooling', 'epochs': 200, 'var': 0, "optimizer": "adamw", "learning_rate":0.005404630243936168, "layers": ['circuit19', 'circuit11', 'circuit11', 'reuploading', 'circuit11'], "best_val_loss": 0.9856899380683899},
		 #{"optimizer":"adamw", "learning_rate": 6.235933473508026e-05, "layers":['circuit19', 'circuit11'], 'name': 'capacitor', 'epochs': 500, 'var': 1}
		 ]

metrics = {'step_sizes': [1, 5, 25, 100, 1000], 'metrics': ['mase']} # the 'metrics' entry is only used for labeling since no other metrics were implemented



# helper function that plots and saves the loss history
def save_history(modelname, folder, log, numOfEpochs):
	if log:
		plt.yscale('log')
	plt.legend()
	plt.title("history of " + modelname)
	plt.ylabel("loss")
	plt.xlabel("epochs")
	plt.xlim(1, numOfEpochs+1)
	plt.grid(True, which = 'both')
	plt.xticks(np.append([1, 5], np.arange(10, numOfEpochs, numOfEpochs/10)))
	plt.savefig(folder + modelname + str(log) + ".png")
	plt.cla()

	
preproc = preprocessing.Preprocessing()
open(logfile, "a").write("\n##Starting job\n\n")

open(logfile, "a").write(str(datetime.datetime.now()) + ": queue " + str(queue) + "\n")
open(logfile, "a").write(str(datetime.datetime.now()) + ": metrics" + str(metrics) + "\n")

for entry in queue:

	# reading and executing the train files. model.run() always has to be called to initialize the internal scaler.
	open(logfile, "a").write('\n#' + entry['name'] + "\n\n")
	preproc.read_csv("paper_data/" + entry['name'])
	open(logfile, "a").write(str(datetime.datetime.now()) + ': read ' + entry['name'] + ' training files\n')
	preproc.split_dataset()
	model = QNN.QNN(preproc, config = entry)
	model.run(epochs = entry['epochs'] if mode == 'run' else 0, batch_size = 8)
	if mode == 'run':
		open(logfile, "a").write(str(datetime.datetime.now()) + ': model train loss history: ' + str(model.history.history['loss']) + "\n")
		open(logfile, "a").write(str(datetime.datetime.now()) + ': model val loss history: ' + str(model.history.history['val_loss']) + "\n")
		model.save_model(runfolder + entry['name'])
		open(logfile, "a").write(str(datetime.datetime.now()) + ": saved model\n")
		plt.plot(np.arange(1, entry['epochs']+1, 1), model.history.history['loss'], label = "training loss")
		plt.plot(np.arange(1, entry['epochs']+1, 1), model.history.history['val_loss'], label = "validation loss")
		save_history(entry['name'], runfolder, True, entry['epochs'])
		plt.plot(np.arange(1, entry['epochs']+1, 1), model.history.history['loss'], label = "training loss")
		plt.plot(np.arange(1, entry['epochs']+1, 1), model.history.history['val_loss'], label = "validation loss")
		save_history(entry['name'], runfolder, False, entry['epochs'])
	elif mode == 'predict':
		model.load_model(runfolder + entry['name'])
		open(logfile, "a").write(str(datetime.datetime.now()) + ": loaded model\n")

	# reading, executing and plotting test metrics
	preproc.read_csv("paper_data/" + entry['name'] + "/test_data")
	open(logfile, "a").write(str(datetime.datetime.now()) + ": read " + entry['name'] + " test files\n")
	preproc.test_dataset()
	for stepsize in metrics['step_sizes']:
		model.predict(step_size = stepsize)
		plt.cla()
		model.plot_prediction(variable_to_predict = entry['var'], save = True, filename = runfolder + entry['name'] + f"_{stepsize}")
		open(logfile, "a").write(str(datetime.datetime.now()) +  ": " + metrics['metrics'][0] + f" with stepsize {stepsize}: {model.relative_error(variable_to_predict = entry['var'])}\n")
		np.save(runfolder + entry['name'] + f"_stepsize_{stepsize}_prediction", model.prediction)


open(logfile, "a").write(str(datetime.datetime.now()) + ": Job finished :)\n")



