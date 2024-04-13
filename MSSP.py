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
            self.problema.update()

            self.problema.optimize()
            print(f"Tetha{self.nodo} = {self.tetha.X}", f"X{self.nodo} = {self.x.X}")
        

    @property
    def variables_duales(self):

        if self.nodo == (2,1):
            for i in self.problema.getConstrs():
                print(i.Pi)

        return (self.problema.getConstrByName("c1").Pi, self.problema.getConstrByName("NV").Pi)

    


    def calcular_coeficinetes(self):
        print("Variables duales:")
        print(self.hijos[0].variables_duales)
        print(self.hijos[1].variables_duales)
        coeffs = (sum((1/2) * (hijo.h * hijo.variables_duales[0]) for hijo in self.hijos), -sum((1/2) * hijo.variables_duales[0] for hijo in self.hijos))
        return coeffs
    
    def agregar_corte(self, coeffs):
        self.problema.addConstr(coeffs[0] + coeffs[1] * self.x <= self.tetha, name="corte")
        print(f"************Corte de optimalidad en {self.nodo}: {coeffs[0]} + {coeffs[1]}x <= theta*************")
        #self.problema.addConstr(gp.quicksum(((1/2) * (hijo.h - self.x) * hijo.variables_duales[0]) for hijo in self.hijos) <= self.tetha, name="corte")



        self.problema.update()

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


    for i in range(3):
        raiz.iteracion()    
        print("\n" * 2)
        print(f"XXXXXXXXX Solucion iteracion {i} XXXXXXXXX")  
        print(raiz.problema.objVal)
        raiz.imprimir_resultado()
        print("\n" * 2)




    



