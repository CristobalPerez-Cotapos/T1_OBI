import numpy as np
import matplotlib.pyplot as plt
import gurobipy as gp



def graficar_region_factible(cortes, iter, sol, L=0, x_vals=np.linspace(-1, 4, 100)):

    # Tamaño de la figura
    plt.figure(figsize=(10, 6))
    ax = plt.gca()  # Get current axes
    ax.set_facecolor('black')

    # Draw x and y axis lines
    plt.axhline(0, color='white', lw=1)  # Add y-axis through the origin
    plt.axvline(0, color='white', lw=1)  # Add x-axis through the origin
    
    # Hacer un llenado inical
    plt.plot(x_vals, [L for _ in x_vals], color='red', linestyle='--',label=f'Cota inferior')
    plt.fill_between([0, 3], 0, 10, color='grey', alpha=0.4, label='Region Factible')
    
    # Para cada corte, llenar el area infactible
    for corte in cortes:

        coeffs = corte[0]

        if corte[-1] == 'opt':
            y_vals = [coeffs[1] * x_val + coeffs[0] for x_val in x_vals]
            plt.plot(x_vals, y_vals, label=f'Corte de opt {cortes.index(corte)+1}')
            plt.fill_between(x_vals, -10, y_vals, color='black', alpha=0.5)
        else:
            const = -coeffs[0] / coeffs[1]
            plt.axvline(x=const, color='blue', linestyle='--', label=f'Corte de fact {cortes.index(corte)+1}')
            plt.fill_betweenx(np.linspace(-10, 10, 100), 0, const, color='black', alpha=0.5)

    # Plot candidate point
    plt.scatter(sol[0], sol[1], color='red', zorder=5, label='Solucion candidata')
    
    plt.xlim(x_vals[0], x_vals[-1])
    plt.ylim(-1, 10)
    plt.xlabel('x')
    plt.ylabel('theta')
    plt.title(f'Iteration {iter}')
    plt.legend()
    plt.show()


class Problema:
    def __init__(self, nodo, h=2):
        self.hijos = []
        self.padre = None
        self.nodo = nodo
        self.h = h
        self.terminado = False
        self.cortes = []

    def agregar_hijo(self, hijo):
        self.hijos.append(hijo)
        hijo.padre = self

    def crear_modelo(self):
        if self.padre is None:
            self.problema = gp.Model("MSSP")

            self.x = self.problema.addVar(vtype=gp.GRB.CONTINUOUS, name="x")
            self.tetha = self.problema.addVar(vtype=gp.GRB.CONTINUOUS, name="tetha")

            self.problema.addConstr(1 <= self.x)
            self.problema.addConstr(self.x <= 3)
            self.problema.addConstr(0 <= self.tetha)
            self.problema.setObjective(self.x + self.tetha, gp.GRB.MINIMIZE)
            self.problema.update()
    
        else:
            self.problema = gp.Model(f"{self.nodo}")
            self.x = self.problema.addVar(vtype=gp.GRB.CONTINUOUS, name=f"y{self.nodo}", lb=0)
            self.problema.addConstr(self.x <= 2, name="NV")
            self.tetha = self.problema.addVar(vtype=gp.GRB.CONTINUOUS, name="tetha")
            self.problema.setObjective(2 * self.x + self.tetha, gp.GRB.MINIMIZE)
            self.problema.update()
        self.problema.Params.OutputFlag = 0

    def iteracion(self):
        self.problema.optimize()
        print(f"########### Nodo {self.nodo} ###########", f"X{self.nodo} = {self.x.X}", f"tetha{self.nodo} = {self.tetha.X}")
        if self.hijos:
            for hijo in self.hijos:
                restriccion = hijo.problema.getConstrByName("c1")
                if restriccion:
                    hijo.problema.remove(restriccion)
                hijo.problema.addConstr(hijo.x >= hijo.h - self.x.X, name="c1")
                hijo.iteracion()


            print(f"########### Nodo {self.nodo} valor de los hijos {self.hijos[0].problema.objVal} y {self.hijos[1].problema.objVal} ###########")
            print(self.tetha.X, ((1/2) * self.hijos[0].problema.objVal + (1/2) * self.hijos[1].problema.objVal))
            if self.tetha.X <= ((1/2) * self.hijos[0].problema.objVal + (1/2) * self.hijos[1].problema.objVal) - 0.0001:
                self.agregar_corte(self.calcular_coeficinetes())
            else:
                print("No se agrega corte")
                self.terminado = True
            self.problema.update()

            self.problema.optimize()
            print(f"Tetha{self.nodo} = {self.tetha.X}", f"X{self.nodo} = {self.x.X}")
        

    @property
    def variables_duales(self):
        return (self.problema.getConstrByName("c1").Pi, self.problema.getConstrByName("NV").Pi)

    


    def calcular_coeficinetes(self):
        suma_positiva = 0
        suma_negativa = 0
        for hijo in self.hijos:
            suma_positiva += (1/2) * hijo.h * hijo.problema.getConstrByName("c1").getAttr("Pi")
            suma_negativa += (1/2) * hijo.problema.getConstrByName("c1").getAttr("Pi")

            # Tomo todas las otras restricciones que no son la c1
            restricciones = filter(lambda x: x.getAttr("ConstrName") != "c1", hijo.problema.getConstrs())

            for restriccion in restricciones:
                suma_positiva += restriccion.getAttr("rhs") * restriccion.getAttr("Pi") * (1/2)

        return (suma_positiva, -suma_negativa)


    
    def agregar_corte(self, coeffs):
        self.problema.addConstr(coeffs[0] + coeffs[1] * self.x <= self.tetha, name="corte")
        print(f"************Corte de optimalidad en {self.nodo}: {coeffs[0]} + {coeffs[1]}x <= theta*************")
        #self.problema.addConstr(gp.quicksum(((1/2) * (hijo.h - self.x) * hijo.variables_duales[0]) for hijo in self.hijos) <= self.tetha, name="corte")
        self.problema.update()
        self.cortes.append((coeffs, "opt"))


    def imprimir_resultado(self):
        print(f"X{self.nodo} = {self.x.X}", f"tetha{self.nodo} = {self.tetha.X}")
        print()
        for hijo in self.hijos:
            hijo.imprimir_resultado()

if __name__ == "__main__":
    raiz = Problema((1,1))
    raiz.crear_modelo()

    hijo2_1 = Problema((2,1), h=3)
    hijo2_2 = Problema((2,2))

    raiz.agregar_hijo(hijo2_1)
    raiz.agregar_hijo(hijo2_2)

    hijo3_1 = Problema((3,1))
    hijo3_2 = Problema((3,2))
    hijo3_3 = Problema((3,3))
    hijo3_4 = Problema((3,4))

    hijo2_1.agregar_hijo(hijo3_1)
    hijo2_1.agregar_hijo(hijo3_2)
    hijo2_2.agregar_hijo(hijo3_3)
    hijo2_2.agregar_hijo(hijo3_4)

    for hijo in raiz.hijos:
        hijo.crear_modelo()
        for nieto in hijo.hijos:
            nieto.crear_modelo()

    iteracion = 0
    while not raiz.terminado:
        raiz.iteracion()    
        print("\n" * 2)
        print(f"XXXXXXXXX Solucion iteracion {iteracion} XXXXXXXXX")
        print(raiz.problema.objVal)
        raiz.imprimir_resultado()
        print("\n" * 2)
        iteracion += 1
        graficar_region_factible(raiz.cortes, iteracion, (raiz.x.X, raiz.tetha.X))




    



