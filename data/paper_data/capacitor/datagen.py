from OMPython import ModelicaSystem
import numpy as np
import pandas as pd

print("preloading")
model = ModelicaSystem("C:/Users/tgerm/Documents/SublimeProjects/QCP/bmw-quantum-surrogate-models/paper_data/capacitor/Capacitor.mo", "Capacitor")
print("postloading")
model.setSimulationOptions("stepSize=0.001")

foldername = "C:/Users/tgerm/Documents/SublimeProjects/QCP/bmw-quantum-surrogate-models/paper_data/osci/"
foldername = "test_data/"
exportValues = ["capacitor.C", "capacitor.v", "resistor.R", "resistor.i"]

vals_minmax = {'C1.k': (0.001, 0.002), 'R1.k': (200, 300)}
keymap = [key for key in vals_minmax]
datasetSize = 5

vals = np.random.rand(len(vals_minmax), datasetSize) #vals element [0,1]

#model.setParameters("capacitor.IC=10.0")
#model.setParameters("capacitor.v=10.0")
#print(model.getParameters("capacitor.IC"))
#print(model.getParameters("inductor.IC"))
#print(model.getParameters())



for i in range(len(keymap)):
	vals[i] = vals[i]*(vals_minmax[keymap[i]][1]-vals_minmax[keymap[i]][0])+vals_minmax[keymap[i]][0]

print("initial setup done")
print(vals.T)

def createDataset(model, vals):
	for i in vals.T:
		#print([keymap[k]+"="+str(i[k]) for k in range(len(keymap))])
		model.setParameters([keymap[k]+"="+str(i[k]) for k in range(len(keymap))])
		#model.setParameters(["volumeFlow.k="+str(i[0]), "thermalConductance.k="+str(i[1]), "heatFlow.k="+str(i[2])])
		model.simulate()
		data = {
			"time": model.getSolutions("time")[0]}
		for var in exportValues:
			data[var] = model.getSolutions(var)[0]
		frame = pd.DataFrame(data)
		#print(frame)
		frame.to_csv(foldername+f"C_{i[0]:.3f}_R_{i[1]:.3f}.csv", index = False, quoting = 1)
		print("simd and saved")

createDataset(model, vals)