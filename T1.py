import numpy as np
import matplotlib.pyplot as plt
import gurobipy as gp
from gurobipy import GRB


k = 3
S = range(k)
h = [3,2]
t = [2,1]
w = [1,2]
p = [1/4,3/4]

L = 0
xlb = 0
xub = 3

# Espacio lineal para graficar
x_vals = np.linspace(xlb -1, xub + 1, 100)