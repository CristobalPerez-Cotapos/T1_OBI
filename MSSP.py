import gurobipy as gp 


class Problema:
    def __init__(self, nodo, h=2):
        self.hijos = []
        self.padre = None
        self.nodo = nodo
        self.h = h

    def agregar_hijo(self, hijo):
        self.hijos.append(hijo)
        hijo.padre = self

    def crear_modelo(self, x_superior=None):
        if self.padre is None:
            self.problema = gp.Model("MSSP")
            self.x = self.problema.addVar(vtype=gp.GRB.CONTINUOUS, name="x")
            self.omega = self.problema.addVar(vtype=gp.GRB.CONTINUOUS, name="omega")
            self.problema.addConstr(1 <= self.x)
            self.problema.addConstr(self.x <= 3)
            self.problema.addConstr(0 <= self.omega)
            self.problema.setObjective(1 * self.x + self.omega, gp.GRB.MINIMIZE)
            self.problema.update()
    
        else:
            self.problema = gp.Model(f"{self.nodo}")
            self.x = self.problema.addVar(vtype=gp.GRB.CONTINUOUS, name=f"y{self.nodo}", lb=0)
            self.problema.addConstr(self.x >= 0, name="NV")
            self.problema.addConstr(self.x <= 2, name="NV")
            self.omega = self.problema.addVar(vtype=gp.GRB.CONTINUOUS, name="omega")
            self.problema.setObjective(2 * self.x + self.omega, gp.GRB.MINIMIZE)
            self.problema.update()
        self.problema.Params.OutputFlag = 0

    def iteracion(self):
        print("\n" * 2)
        self.problema.optimize()
        if self.hijos:
            for hijo in self.hijos:
                restriccion = hijo.problema.getConstrByName("c1")
                if restriccion:
                    hijo.problema.remove(restriccion)
                hijo.problema.addConstr(hijo.x >= hijo.h - self.x.X, name="c1")
                hijo.iteracion()

                print((hijo.h - self.x.X) * hijo.variable_dual)


            ######################################################### Duda de que hay que eliminar el .X de self.x
            self.problema.addConstr(gp.quicksum(((1/2) * (hijo.h - self.x.X) * hijo.variable_dual) for hijo in self.hijos) <= self.omega, name="corte")
            print(self.hijos[0].variable_dual, self.hijos[1].variable_dual)
            self.problema.update()

            self.problema.optimize()
        
        if self.padre is not None:
            self.variable_dual = self.problema.getConstrByName("c1").Pi
            print(f"Variable dual del nodo {self.nodo} = {self.variable_dual}")
            print(f"El optimo del nodo {self.nodo} es {self.problema.objVal}")
            print(f"Omega del nodo {self.nodo} = {self.omega.X}")


    def imprimir_resultado(self):
        print(f"X{self.nodo} = {self.x.X}")
        for hijo in self.hijos:
            hijo.imprimir_resultado()


if __name__ == "__main__":
    raiz = Problema((1,1))
    raiz.crear_modelo()

    hijo2_1 = Problema((2,1), h=3)
    hijo2_2 = Problema((2,2))

    raiz.agregar_hijo(hijo2_2)
    raiz.agregar_hijo(hijo2_1)

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


    for i in range(3):
        raiz.iteracion()    
        print("\n" * 2)
        print(f"XXXXXXXXX Solucion iteracion {i} XXXXXXXXX")  
        print(raiz.problema.objVal)
        raiz.imprimir_resultado()
        print("\n" * 2)




    



