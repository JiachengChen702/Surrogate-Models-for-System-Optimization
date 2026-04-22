from OMPython import ModelicaSystem
import numpy as np
import pandas as pd

print("preloading")
model = ModelicaSystem("C:/Users/tgerm/Desktop/osci.mo", "osci")
print("postloading")
model.setSimulationOptions("stepSize=0.001")

foldername = "C:/Users/tgerm/Documents/SublimeProjects/QCP/bmw-quantum-surrogate-models/paper_data/osci/"
foldername = ""
exportValues = ["capacitor.C", "capacitor.IC", "capacitor.v", "inductor.L", "inductor.i", "resistor.R", "resistor.v", "resistor.LossPower"]

vals_minmax = {'C1.k': (0.001, 0.5), 'R1.k': (0.001, 0.05), 'L1.k': (0.05, 1)}
keymap = [key for key in vals_minmax]
datasetSize = 100

vals = np.random.rand(len(vals_minmax), datasetSize) #vals element [0,1]

#model.setParameters("capacitor.IC=10.0")
#model.setParameters("capacitor.v=10.0")
print(model.getParameters("capacitor.IC"))
print(model.getParameters("inductor.IC"))
print(model.getParameters())



for i in range(len(keymap)):
	vals[i] = vals[i]*(vals_minmax[keymap[i]][1]-vals_minmax[keymap[i]][0])+vals_minmax[keymap[i]][0]

print("initial setup done")
print(vals.T)

def createDataset(model, vals):
	for i in vals.T:
		model.setParameters([keymap[k]+"="+str(i[k]) for k in range(len(keymap))])
		#model.setParameters(["volumeFlow.k="+str(i[0]), "thermalConductance.k="+str(i[1]), "heatFlow.k="+str(i[2])])
		model.simulate()
		data = {
			"time": model.getSolutions("time")[0]}
		for var in exportValues:
			data[var] = model.getSolutions(var)[0]
		frame = pd.DataFrame(data)
		frame.to_csv(foldername+f"C_{i[0]:.3f}_R_{i[1]:.3f}_L_{i[2]:.3f}.csv", index = False, quoting = 1)
		print("simd and saved")

createDataset(model, vals)