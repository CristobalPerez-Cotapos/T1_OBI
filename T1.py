import numpy as np
import matplotlib.pyplot as plt
import gurobipy as gp
from gurobipy import GRB


class Maestro:

    def __init__(self, xlb=0, xub=GRB.INFINITY, L=0):
        
        self.model = gp.Model('Maestro')
        self.model.Params.OutputFlag = 0

        # Variables
        self.x = self.model.addVar(name='x')
        self.theta = self.model.addVar(name='theta')

        self.model.addConstr(self.x <= xub)
        self.model.addConstr(self.theta >= L)

        # Funcion objetivo
        self.model.setObjective(self.x + self.theta)

        # Actualizar el modelo
        self.model.update()

        self.iter = 0

    def optimizar(self):

        self.model.update()
        self.model.optimize()
        self.iter +=1 
        
        print(f"{'#'*8} Iteracion {self.iter} {'#'*8}")
        print("Objetivo maestro:", self.model.objVal) 
        print("Solucion candidata: x =", self.x.X)
        
    def agregar_corte_factibilidad(self, coeffs):

        # agregar corte
        self.model.addConstr(coeffs[0] + coeffs[1] * self.x <= 0)
        print(f"Corte de factibilidad: {coeffs[0]} + {coeffs[1]}x <= 0")

    def agregar_corte_optimalidad(self, coeffs):

        # agregar corte
        self.model.addConstr(coeffs[0] + coeffs[1] * self.x <= self.theta)
        print(f"Corte de optimalidad: {coeffs[0]} + {coeffs[1]}x <= theta")
