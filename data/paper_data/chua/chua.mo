model test
  Modelica.Blocks.Sources.Constant R2(k = 2200) annotation(
    Placement(transformation(origin = {-92, -20}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Ideal.IdealOpAmp3Pin opAmp annotation(
    Placement(transformation(origin = {0, -74}, extent = {{-10, -10}, {10, 10}}, rotation = 90)));
  Modelica.Electrical.Analog.Basic.Resistor resistor(R = 290) annotation(
    Placement(transformation(origin = {-24, -74}, extent = {{-10, -10}, {10, 10}}, rotation = -90)));
  Modelica.Electrical.Analog.Basic.Resistor resistor1(R = 290) annotation(
    Placement(transformation(origin = {20, -74}, extent = {{-10, -10}, {10, 10}}, rotation = -90)));
  Modelica.Electrical.Analog.Basic.VariableResistor resistor4 annotation(
    Placement(transformation(origin = {-40, -64}, extent = {{-10, -10}, {10, 10}}, rotation = 90)));
  Modelica.Blocks.Sources.Constant R1(k = 1500) annotation(
    Placement(transformation(origin = {-92, -52}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Basic.Ground ground annotation(
    Placement(transformation(origin = {-44, 24}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Sensors.CurrentSensor currentSensor annotation(
    Placement(transformation(origin = {8, 10}, extent = {{-10, -10}, {10, 10}}, rotation = -90)));
  Modelica.Electrical.Analog.Ideal.IdealDiode diode(Vknee = 0.7) annotation(
    Placement(transformation(origin = {-4, -32}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Ideal.IdealDiode diode1(Vknee = 0.7) annotation(
    Placement(transformation(origin = {-4, -10}, extent = {{10, -10}, {-10, 10}}, rotation = -0)));
  Modelica.Electrical.Analog.Basic.VariableResistor resistor2 annotation(
    Placement(transformation(origin = {-28, -10}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Basic.VariableResistor resistor3 annotation(
    Placement(transformation(origin = {-28, -32}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Basic.VariableCapacitor capacitor(IC = 0.7, UIC = true, Cmin(displayUnit = "uF"))  annotation(
    Placement(transformation(origin = {-16, 26}, extent = {{10, -10}, {-10, 10}}, rotation = -0)));
  Modelica.Electrical.Analog.Basic.VariableResistor resistor5 annotation(
    Placement(transformation(origin = {8, 48}, extent = {{-10, -10}, {10, 10}}, rotation = -90)));
  Modelica.Electrical.Analog.Basic.VariableCapacitor capacitor1(Cmin(displayUnit = "uF"))  annotation(
    Placement(transformation(origin = {-14, 58}, extent = {{-10, 10}, {10, -10}}, rotation = -180)));
  Modelica.Electrical.Analog.Basic.VariableInductor inductor(IC = 0.1, UIC = true, Lmin(displayUnit = "mH"))  annotation(
    Placement(transformation(origin = {-14, 86}, extent = {{10, -10}, {-10, 10}}, rotation = -0)));
  Modelica.Blocks.Sources.Constant L1(k = 0.018)  annotation(
    Placement(transformation(origin = {-92, 86}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant C2(k = 0.0001)  annotation(
    Placement(transformation(origin = {68, 92}, extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Sources.Constant R(k = 1800)  annotation(
    Placement(transformation(origin = {70, 60}, extent = {{10, -10}, {-10, 10}})));
  Modelica.Blocks.Sources.Constant C1(k = 0.00001)  annotation(
    Placement(transformation(origin = {72, 28}, extent = {{10, -10}, {-10, 10}})));
equation
  connect(resistor1.p, opAmp.out) annotation(
    Line(points = {{20, -64}, {0, -64}}, color = {0, 0, 255}));
  connect(resistor.p, opAmp.out) annotation(
    Line(points = {{-24, -64}, {0, -64}}, color = {0, 0, 255}));
  connect(resistor.n, opAmp.in_n) annotation(
    Line(points = {{-24, -84}, {-6, -84}}, color = {0, 0, 255}));
  connect(opAmp.in_p, resistor1.n) annotation(
    Line(points = {{6, -84}, {20, -84}}, color = {0, 0, 255}));
  connect(resistor4.R, R1.y) annotation(
    Line(points = {{-52, -64}, {-65, -64}, {-65, -52}, {-81, -52}}, color = {0, 0, 127}));
  connect(resistor4.p, resistor.n) annotation(
    Line(points = {{-40, -74}, {-40, -84}, {-24, -84}}, color = {0, 0, 255}));
  connect(currentSensor.n, resistor1.n) annotation(
    Line(points = {{8, 0}, {8, -36}, {54, -36}, {54, -84}, {20, -84}}, color = {0, 0, 255}));
  connect(resistor2.n, diode1.n) annotation(
    Line(points = {{-18, -10}, {-14, -10}}, color = {0, 0, 255}));
  connect(diode1.p, currentSensor.n) annotation(
    Line(points = {{6, -10}, {8, -10}, {8, 0}}, color = {0, 0, 255}));
  connect(diode.n, currentSensor.n) annotation(
    Line(points = {{6, -32}, {8, -32}, {8, 0}}, color = {0, 0, 255}));
  connect(resistor2.p, resistor4.n) annotation(
    Line(points = {{-38, -10}, {-40, -10}, {-40, -54}}, color = {0, 0, 255}));
  connect(resistor3.p, resistor4.n) annotation(
    Line(points = {{-38, -32}, {-40, -32}, {-40, -54}}, color = {0, 0, 255}));
  connect(resistor3.n, diode.p) annotation(
    Line(points = {{-18, -32}, {-14, -32}}, color = {0, 0, 255}));
  connect(resistor2.R, R2.y) annotation(
    Line(points = {{-28, 2}, {-80, 2}, {-80, -20}}, color = {0, 0, 127}));
  connect(resistor3.R, R2.y) annotation(
    Line(points = {{-28, -20}, {-80, -20}}, color = {0, 0, 127}));
  connect(capacitor.p, currentSensor.p) annotation(
    Line(points = {{-6, 26}, {8, 26}, {8, 20}}, color = {0, 0, 255}));
  connect(capacitor.n, resistor2.p) annotation(
    Line(points = {{-26, 26}, {-38, 26}, {-38, -10}}, color = {0, 0, 255}));
  connect(ground.p, capacitor.n) annotation(
    Line(points = {{-44, 34}, {-26, 34}, {-26, 26}}, color = {0, 0, 255}));
  connect(resistor5.n, currentSensor.p) annotation(
    Line(points = {{8, 38}, {8, 20}}, color = {0, 0, 255}));
  connect(capacitor1.p, resistor5.p) annotation(
    Line(points = {{-4, 58}, {8, 58}}, color = {0, 0, 255}));
  connect(capacitor1.n, capacitor.n) annotation(
    Line(points = {{-24, 58}, {-26, 58}, {-26, 26}}, color = {0, 0, 255}));
  connect(inductor.p, capacitor1.p) annotation(
    Line(points = {{-4, 86}, {-4, 58}}, color = {0, 0, 255}));
  connect(inductor.n, capacitor1.n) annotation(
    Line(points = {{-24, 86}, {-24, 58}}, color = {0, 0, 255}));
  connect(inductor.L, L1.y) annotation(
    Line(points = {{-14, 98}, {-58, 98}, {-58, 86}, {-81, 86}}, color = {0, 0, 127}));
  connect(C2.y, capacitor1.C) annotation(
    Line(points = {{57, 92}, {14, 92}, {14, 70}, {-14, 70}}, color = {0, 0, 127}));
  connect(resistor5.R, R.y) annotation(
    Line(points = {{20, 48}, {34, 48}, {34, 60}, {59, 60}}, color = {0, 0, 127}));
  connect(capacitor.C, C1.y) annotation(
    Line(points = {{-16, 38}, {2, 38}, {2, 32}, {30, 32}, {30, 28}, {61, 28}}, color = {0, 0, 127}));
  annotation(
    uses(Modelica(version = "4.0.0")));
end test;
