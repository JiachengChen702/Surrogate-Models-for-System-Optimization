model SimpleCooling2 "Simple cooling circuit"
  extends Modelica.Icons.Example;
  parameter Modelica.Thermal.FluidHeatFlow.Media.Medium medium = Modelica.Thermal.FluidHeatFlow.Media.Medium() "Cooling medium" annotation(
    choicesAllMatching = true);
  parameter Modelica.Units.SI.Temperature TAmb(displayUnit = "degC") = 293.15 "Ambient temperature";
  output Modelica.Units.SI.TemperatureDifference dTSource = prescribedHeatFlow.port.T - TAmb "Source over Ambient";
  output Modelica.Units.SI.TemperatureDifference dTtoPipe = prescribedHeatFlow.port.T - pipe.T_q "Source over Coolant";
  output Modelica.Units.SI.TemperatureDifference dTCoolant = pipe.dT "Coolant's temperature increase";
  Modelica.Thermal.FluidHeatFlow.Sources.VolumeFlow pump(T0 = TAmb, constantVolumeFlow = 1, m = 0, medium = medium, useVolumeFlowInput = true) annotation(
    Placement(transformation(extent = {{-40, -10}, {-20, 10}})));
  Modelica.Thermal.FluidHeatFlow.Components.Pipe pipe(T0 = TAmb, T0fixed = true, V_flowLaminar = 0.1, V_flowNominal = 1, dpLaminar(displayUnit = "Pa") = 0.1, dpNominal(displayUnit = "Pa") = 1, h_g = 0, m = 0.1, medium = medium, useHeatPort = true) annotation(
    Placement(transformation(extent = {{0, -10}, {20, 10}})));
  Modelica.Thermal.HeatTransfer.Components.HeatCapacitor heatCapacitor(C = 0.1, T(fixed = true, start = TAmb)) annotation(
    Placement(transformation(origin = {40, -50}, extent = {{-10, 10}, {10, -10}}, rotation = 90)));
  Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow prescribedHeatFlow annotation(
    Placement(transformation(extent = {{-30, -40}, {-10, -60}})));
  Modelica.Blocks.Sources.Constant volumeFlow(k = 2) annotation(
    Placement(transformation(origin = {-36, -4}, extent = {{-60, 10}, {-40, 30}})));
  Modelica.Thermal.HeatTransfer.Components.Convection convection annotation(
    Placement(transformation(origin = {10, -30}, extent = {{-10, -10}, {10, 10}}, rotation = 90)));
  Modelica.Thermal.FluidHeatFlow.Components.Pipe pipe1(T0 = TAmb, T0fixed = true, V_flowLaminar = 0.1, V_flowNominal = 1, dpLaminar(displayUnit = "Pa") = 0.1, dpNominal(displayUnit = "Pa") = 1, h_g = 0, m = 0.1, medium = medium, useHeatPort = true) annotation(
    Placement(transformation(origin = {20, 36}, extent = {{0, 10}, {-20, -10}})));
  Modelica.Thermal.FluidHeatFlow.Components.OpenTank openTank(ATank = 0.5, T(fixed = true, start = 293.15), T0 = TAmb, hTank = 0.5, level(fixed = true, start = 0.2), medium = medium) annotation(
    Placement(transformation(origin = {-56, 46}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Thermal.HeatTransfer.Components.Convection convection1 annotation(
    Placement(transformation(origin = {10, 64}, extent = {{10, 10}, {-10, -10}}, rotation = 90)));
  Modelica.Thermal.HeatTransfer.Components.HeatCapacitor heatCapacitor1(C = 0.1, T(fixed = true, start = TAmb)) annotation(
    Placement(transformation(origin = {38, 86}, extent = {{-10, 10}, {10, -10}}, rotation = 90)));
  Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow prescribedHeatFlow1 annotation(
    Placement(transformation(origin = {0, 136}, extent = {{-30, -40}, {-10, -60}})));
  Modelica.Blocks.Sources.Constant CoolerHeatFlow(k = 30) annotation(
    Placement(transformation(origin = {-92, 92}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Math.Product product annotation(
    Placement(transformation(origin = {-52, 86}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant negative(k = -1) annotation(
    Placement(transformation(origin = {-92, 60}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant coolerConv(k = 1.5) annotation(
    Placement(transformation(origin = {74, 64}, extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Sources.Constant EngineHeatFlow(k = 20) annotation(
    Placement(transformation(origin = {-82, -56}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant EngineConv(k = 1.5) annotation(
    Placement(transformation(origin = {-84, -22}, extent = {{-10, -10}, {10, 10}})));
equation
  connect(pump.flowPort_b, pipe.flowPort_a) annotation(
    Line(points = {{-20, 0}, {0, 0}}, color = {255, 0, 0}));
  connect(convection.solid, prescribedHeatFlow.port) annotation(
    Line(points = {{10, -40}, {10, -50}, {-10, -50}}, color = {191, 0, 0}));
  connect(convection.solid, heatCapacitor.port) annotation(
    Line(points = {{10, -40}, {10, -50}, {30, -50}}, color = {191, 0, 0}));
  connect(pipe.heatPort, convection.fluid) annotation(
    Line(points = {{10, -10}, {10, -20}}, color = {191, 0, 0}));
  connect(volumeFlow.y, pump.volumeFlow) annotation(
    Line(points = {{-75, 16}, {-32, 16}, {-32, 10}, {-30, 10}}, color = {0, 0, 127}));
  connect(pipe.flowPort_b, pipe1.flowPort_a) annotation(
    Line(points = {{20, 0}, {36, 0}, {36, 36}, {20, 36}}, color = {255, 0, 0}));
  connect(pipe1.flowPort_b, openTank.flowPort) annotation(
    Line(points = {{0, 36}, {-56, 36}}, color = {255, 0, 0}));
  connect(pipe1.flowPort_b, pump.flowPort_a) annotation(
    Line(points = {{0, 36}, {-50, 36}, {-50, 0}, {-40, 0}}, color = {255, 0, 0}));
  connect(convection1.fluid, pipe1.heatPort) annotation(
    Line(points = {{10, 54}, {10, 46}}, color = {191, 0, 0}));
  connect(prescribedHeatFlow1.port, heatCapacitor1.port) annotation(
    Line(points = {{-10, 86}, {28, 86}}, color = {191, 0, 0}));
  connect(prescribedHeatFlow1.port, convection1.solid) annotation(
    Line(points = {{-10, 86}, {10, 86}, {10, 74}}, color = {191, 0, 0}));
  connect(CoolerHeatFlow.y, product.u1) annotation(
    Line(points = {{-81, 92}, {-64, 92}}, color = {0, 0, 127}));
  connect(product.y, prescribedHeatFlow1.Q_flow) annotation(
    Line(points = {{-40, 86}, {-30, 86}}, color = {0, 0, 127}));
  connect(negative.y, product.u2) annotation(
    Line(points = {{-81, 60}, {-64, 60}, {-64, 80}}, color = {0, 0, 127}));
  connect(coolerConv.y, convection1.Gc) annotation(
    Line(points = {{63, 64}, {20, 64}}, color = {0, 0, 127}));
  connect(EngineHeatFlow.y, prescribedHeatFlow.Q_flow) annotation(
    Line(points = {{-70, -56}, {-30, -56}, {-30, -50}}, color = {0, 0, 127}));
  connect(EngineConv.y, convection.Gc) annotation(
    Line(points = {{-73, -22}, {-40, -22}, {-40, -30}, {0, -30}}, color = {0, 0, 127}));
  annotation(
    Documentation(info = "<html>
<p>
1st test example: SimpleCooling
</p>
A prescribed heat source dissipates its heat through a thermal conductor to a coolant flow. The coolant flow is taken from an ambient and driven by a pump with prescribed mass flow.<br>
<strong>Results</strong>:<br>
<table>
<tr>
<td><strong>output</strong></td>
<td><strong>explanation</strong></td>
<td><strong>formula</strong></td>
<td><strong>actual steady-state value</strong></td>
</tr>
<tr>
<td>dTSource</td>
<td>Source over Ambient</td>
<td>dtCoolant + dtToPipe</td>
<td>20 K</td>
</tr>
<tr>
<td>dTtoPipe</td>
<td>Source over Coolant</td>
<td>Losses / ThermalConductor.G</td>
<td>10 K</td>
</tr>
<tr>
<td>dTCoolant</td>
<td>Coolant's temperature increase</td>
<td>Losses * cp * massFlow</td>
<td>10 K</td>
</tr>
</table>
</html>"),
    experiment(StopTime = 1.0, Interval = 0.001),
  uses(Modelica(version = "4.0.0")));
end SimpleCooling2;
