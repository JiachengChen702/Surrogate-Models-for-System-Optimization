from OMPython import ModelicaSystem
import numpy as np
import pandas as pd

model = ModelicaSystem("C:/Users/tgerm/Documents/SublimeProjects/QCP/bmw-quantum-surrogate-models/paper_data/simpleheating/SimpleCooling2.mo", "SimpleCooling2")
model.setSimulationOptions("stepSize=0.001")

vals = np.random.rand(3, 5)
vals[0] = vals[0]+1
vals[1] = vals[1]+1
vals[2] = vals[2]*-10-10

print(vals.T)
model.setParameters("TAmb=60.0")

def createDataset(model, vals):
	for i in vals.T:
		model.setParameters(["volumeFlow.k="+str(i[0]), "thermalConductance.k="+str(i[1]), "heatFlow.k="+str(i[2])])
		model.simulate()
		data = {
			"time": model.getSolutions("time")[0],
			"heatCapacitor.T": model.getSolutions("heatCapacitor.T")[0],
			"pipe.T": model.getSolutions("pipe.T")[0],
			"der(pipe.T)": model.getSolutions("der(pipe.T)")[0],
			"pump.V_flow": model.getSolutions("pump.V_flow")[0],
			"dtCoolant": model.getSolutions("dTCoolant")[0],
			"dtSource": model.getSolutions("dTSource")[0],
			"dtToPipe": model.getSolutions("dTtoPipe")[0],
			"der(heatCapacitor.T)": model.getSolutions("der(heatCapacitor.T)")[0],
			"convection.Gc": model.getSolutions("convection.Gc")[0],
			"prescribedHeatFlow.Q_flow": model.getSolutions("prescribedHeatFlow.Q_flow")[0],
		}
		frame = pd.DataFrame(data)
		frame.to_csv("test_data/"+str(i[0])+"_"+str(i[1])+"_"+str(i[2])+".csv", index = False, quoting = 1)

createDataset(model, vals)