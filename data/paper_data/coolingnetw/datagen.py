from OMPython import ModelicaSystem
import numpy as np
import pandas as pd

model = ModelicaSystem("C:/Users/tgerm/Desktop/CoolingNetw.mo", "SimpleCooling2")
model.setSimulationOptions("stepSize=0.001")
vals = np.random.rand(5, 5)
vals[0] = vals[0]+1
vals[1] = vals[1]+1
vals[2] = vals[2]*10+10
vals[3] = vals[3]+1
vals[4] = vals[4]*10+10


print(vals.T)

def createDataset(model, vals):
	for i in vals.T:
		model.setParameters(["VFlow.k="+str(i[0]), "ConvEng.k="+str(i[1]), "HFlowEng.k="+str(i[2]), "ConvCooler.k="+str(i[3]), "HFlowCooler.k="+str(i[4])])
		model.simulate()
		data = {
			"time": model.getSolutions("time")[0],

			"heatCapacitor.T": model.getSolutions("heatCapacitor.T")[0], #heatsrc
			"der(heatCapacitor.T)": model.getSolutions("der(heatCapacitor.T)")[0],
			"convection.Gc": model.getSolutions("convection.Gc")[0],
			"convection.dT": model.getSolutions("convection.dT")[0],
			"pipe.T": model.getSolutions("pipe.T")[0],
			"der(pipe.T)": model.getSolutions("der(pipe.T)")[0],
			"pipe.dT": model.getSolutions("pipe.dT")[0],
			"pipe.Q_flow": model.getSolutions("pipe.Q_flow")[0],
			"prescribedHeatFlow.Q_flow": model.getSolutions("prescribedHeatFlow.Q_flow")[0],

			"pump.V_flow": model.getSolutions("pump.V_flow")[0],
			"openTank.T_port": model.getSolutions("openTank.T_port")[0],
							
			"heatCapacitor1.T": model.getSolutions("heatCapacitor.T")[0], #heatsink
			"der(heatCapacitor1.T)": model.getSolutions("der(heatCapacitor.T)")[0],
			"convection1.Gc": model.getSolutions("convection.Gc")[0],
			"convection1.dT": model.getSolutions("convection.dT")[0],
			"pipe1.T": model.getSolutions("pipe.T")[0],
			"der(pipe1.T)": model.getSolutions("der(pipe.T)")[0],
			"pipe1.dT": model.getSolutions("pipe.dT")[0],
			"pipe1.Q_flow": model.getSolutions("pipe.Q_flow")[0],
			"prescribedHeatFlow1.Q_flow": model.getSolutions("prescribedHeatFlow.Q_flow")[0],
			
			
			
		}
		frame = pd.DataFrame(data)
		frame.to_csv("test_data/"+str(i[0])+"_"+str(i[1])+"_"+str(i[2])+"_"+str(i[3])+"_"+str(i[4])+".csv", index = False, quoting = 1)

createDataset(model, vals)