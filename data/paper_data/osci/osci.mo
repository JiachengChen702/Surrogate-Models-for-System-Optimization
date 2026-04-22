model osci
  Modelica.Electrical.Analog.Basic.Ground ground annotation(
    Placement(transformation(origin = {14, 50}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Basic.VariableResistor resistor(useHeatPort = false)  annotation(
    Placement(transformation(origin = {-32, 54}, extent = {{-10, -10}, {10, 10}}, rotation = 90)));
  Modelica.Electrical.Analog.Basic.VariableCapacitor capacitor(Cmin(displayUnit = "uF"), IC = 10, UIC = true)  annotation(
    Placement(transformation(origin = {-14, 72}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Basic.VariableInductor inductor(Lmin(displayUnit = "nH"))  annotation(
    Placement(transformation(origin = {-12, 24}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant C1(k = 0.001)  annotation(
    Placement(transformation(origin = {-76, 80}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant R1(k = 0.1)  annotation(
    Placement(transformation(origin = {-76, 50}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant L1(k = 0.2)  annotation(
    Placement(transformation(origin = {-76, 18}, extent = {{-10, -10}, {10, 10}})));
equation
  connect(capacitor.p, resistor.n) annotation(
    Line(points = {{-24, 72}, {-32, 72}, {-32, 64}}, color = {0, 0, 255}));
  connect(capacitor.n, inductor.n) annotation(
    Line(points = {{-4, 72}, {-2, 72}, {-2, 24}}, color = {0, 0, 255}));
  connect(inductor.p, resistor.p) annotation(
    Line(points = {{-22, 24}, {-32, 24}, {-32, 44}}, color = {0, 0, 255}));
  connect(capacitor.n, ground.p) annotation(
    Line(points = {{-4, 72}, {14, 72}, {14, 60}}, color = {0, 0, 255}));
  connect(L1.y, inductor.L) annotation(
    Line(points = {{-64, 18}, {-46, 18}, {-46, 36}, {-12, 36}}, color = {0, 0, 127}));
  connect(R1.y, resistor.R) annotation(
    Line(points = {{-64, 50}, {-44, 50}, {-44, 54}}, color = {0, 0, 127}));
  connect(C1.y, capacitor.C) annotation(
    Line(points = {{-64, 80}, {-56, 80}, {-56, 84}, {-14, 84}}, color = {0, 0, 127}));
  annotation(
    uses(Modelica(version = "4.0.0")));
end osci;
