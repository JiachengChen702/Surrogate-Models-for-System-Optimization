from OMPython import ModelicaSystem
import numpy as np
import pandas as pd

print("preloading")
model = ModelicaSystem("C:/Users/timmi/Documents/SublimeProjects/QCP/bmw-quantum-surrogate-models/paper_data/chua/chua.mo", "test")
print("postloading")


foldername = "test_data/"
exportValues = ["capacitor.v", "capacitor1.v", "inductor.i", "capacitor.C", "capacitor1.C", "inductor.L", "inductor.IC", "capacitor.IC", "resistor.R", "resistor1.R", "resistor2.R", "resistor3.R", "resistor4.R", "resistor5.R"]


vals_minmax = {'L1.k': (0.01, 0.012), 'R2.k': (2200, 2250), 'R1.k': (1500, 1550), 'C2.k': (0.0001, 0.00012), 'R.k': (1800, 1850), 'C1.k': (0.00001, 0.000012)}
keymap = [key for key in vals_minmax]
datasetSize = 5

vals = np.random.rand(len(vals_minmax), datasetSize) #vals element [0,1]

#model.setParameters("capacitor.IC=10.0")
#model.setParameters("capacitor.v=10.0")
model.setSimulationOptions("stepSize=0.001")
print(model.getSimulationOptions())
print(model.getParameters())


for i in range(len(keymap)):
	vals[i] = vals[i]*(vals_minmax[keymap[i]][1]-vals_minmax[keymap[i]][0])+vals_minmax[keymap[i]][0]

print("initial setup done")
print(vals.T)

def removeUnevenTimeStamps(data):
	droppedIndices = []
	for i in range(len(data['time'])):
		if len(str(data['time'][i])) > 5:
			droppedIndices.append(i)
	for entry in data:
		data[entry] = np.delete(data[entry], droppedIndices)
	return len(droppedIndices)
			

def createDataset(model, vals):
	for i in vals.T:
		model.setParameters([keymap[k]+"="+str(i[k]) for k in range(len(keymap))])
		#model.setParameters(["volumeFlow.k="+str(i[0]), "thermalConductance.k="+str(i[1]), "heatFlow.k="+str(i[2])])
		model.simulate()
		data = {
			"time": model.getSolutions("time")[0]}
		for var in exportValues:
			data[var] = model.getSolutions(var)[0]
			#print(var + " " + str(model.getSolutions(var)[0]))
		removedFrames = removeUnevenTimeStamps(data)
		frame = pd.DataFrame(data)
		
		frame.to_csv(foldername+f"L1_{i[0]:.3f}_R2_{i[1]:.3f}_R1_{i[2]:.3f}_C2_{i[3]:.3f}_R_{i[4]:.3f}_C1_{i[5]:.3f}.csv", index = False, quoting = 1)
		print(f"simd and saved, dropped {removedFrames} rows")

createDataset(model, vals)