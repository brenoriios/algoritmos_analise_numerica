from decimal import Decimal, getcontext
from sympy import N, sympify
from models.Function import Function

class RungeKutta3:
    label: str = "Runge Kutta de 3° ordem"
    color: str = "darkgreen"

    getcontext().prec = 50

    def solve_function(self, function: Function, subs: dict[str, Decimal]):
        symp_expression = sympify(function.expression)
        return Decimal(str(N(symp_expression.evalf(subs=subs))))
    
    def get_k1(self, function: Function, values: dict[str, Decimal]):
        return self.solve_function(function, values)
    
    def get_k2(self, function: Function, values: dict[str, Decimal], k1: dict[str, Decimal], control_variable: str, relative_to: str, h: Decimal):
        x = values[control_variable] + (Decimal(1/2) * h)
        y = values[relative_to] + (Decimal(1/2) * k1[relative_to] * h)

        return self.solve_function(function, values | { control_variable: x, relative_to: y})
    
    def get_k3(self, function: Function, values: dict[str, Decimal], k1: dict[str, Decimal], k2: dict[str, Decimal], control_variable: str, relative_to: str, h: Decimal):
        x = values[control_variable] +  h
        y = values[relative_to] - (k1[relative_to] * h) + (Decimal(2) * k2[relative_to] * h)

        return self.solve_function(function, values | { control_variable: x, relative_to: y})

    def get_next_value(self, values: dict[str, Decimal], k1: dict[str, Decimal], k2: dict[str, Decimal], k3: dict[str, Decimal], function: Function, h: Decimal):
        next_value = values[function.relative_to] + (Decimal(1 / 6) * (k1[function.relative_to] + (4 * k2[function.relative_to]) + k3[function.relative_to]) * h)

        return next_value

    def solve(self, edos: list[Function], variables: list[str], initial_values: list[Decimal], control_variable: str, points: int, interval: list[Decimal]):
        solutions = [dict(zip(variables, initial_values)) | { control_variable: Decimal(interval[0]) }]
        h = Decimal((interval[1] - interval[0]) / points)

        for i in range(points):
            control = Decimal(interval[0]) + h * i
            k1_dict = { }
            k2_dict = { }
            k3_dict = { }
            solution_dict = { control_variable: control }

            last_values = solutions[-1]
            
            for edo in edos:
                k1 = self.get_k1(edo, last_values)
                k1_dict[edo.relative_to] = k1
            
            for edo in edos:
                k2 = self.get_k2(edo, last_values, k1_dict, control_variable, edo.relative_to, h)
                k2_dict[edo.relative_to] = k2

            for edo in edos:
                k3 = self.get_k3(edo, last_values, k1_dict, k2_dict, control_variable, edo.relative_to, h)
                k3_dict[edo.relative_to] = k3

            for edo in edos:
                next_value = self.get_next_value(last_values, k1_dict, k2_dict, k3_dict, edo, h)
                solution_dict[edo.relative_to] = next_value

            solutions.append(solution_dict)
        
        return solutions