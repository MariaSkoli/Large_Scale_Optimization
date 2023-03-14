from solver_Final import *

m = Model()
m.BuildModel()
s = Solver(m)
sol = s.solve()