model Capacitor
  Modelica.Electrical.Analog.Basic.VariableCapacitor capacitor(IC = 10, UIC = true)  annotation(
    Placement(transformation(origin = {-12, 64}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Electrical.Analog.Basic.VariableResistor resistor annotation(
    Placement(transformation(origin = {-12, 44}, extent = {{-10, 10}, {10, -10}}, rotation = -0)));
  Modelica.Electrical.Analog.Basic.Ground ground annotation(
    Placement(transformation(origin = {12, 54}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant C1(k = 0.001)  annotation(
    Placement(transformation(origin = {-60, 78}, extent = {{-10, -10}, {10, 10}})));
  Modelica.Blocks.Sources.Constant R1(k = 200)  annotation(
    Placement(transformation(origin = {-60, 46}, extent = {{-10, -10}, {10, 10}})));
equation
  connect(capacitor.p, resistor.p) annotation(
    Line(points = {{-22, 64}, {-22, 44}}, color = {0, 0, 255}));
  connect(capacitor.n, resistor.n) annotation(
    Line(points = {{-2, 64}, {-2, 44}}, color = {0, 0, 255}));
  connect(ground.p, capacitor.n) annotation(
    Line(points = {{12, 64}, {-2, 64}}, color = {0, 0, 255}));
  connect(R1.y, resistor.R) annotation(
    Line(points = {{-48, 46}, {-36, 46}, {-36, 32}, {-12, 32}}, color = {0, 0, 127}));
  connect(C1.y, capacitor.C) annotation(
    Line(points = {{-48, 78}, {-12, 78}, {-12, 76}}, color = {0, 0, 127}));

annotation(
    uses(Modelica(version = "4.0.0")));
end Capacitor;
