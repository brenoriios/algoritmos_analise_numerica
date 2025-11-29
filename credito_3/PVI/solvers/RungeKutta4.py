from decimal import Decimal, getcontext
from sympy import N, sympify
from models.Function import Function

class RungeKutta4:
    label: str = "Runge Kutta de 4° ordem"
    color: str = "darkcyan"

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
    
    def get_k3(self, function: Function, values: dict[str, Decimal], k2: dict[str, Decimal], control_variable: str, relative_to: str, h: Decimal):
        x = values[control_variable] + (Decimal(1/2) * h)
        y = values[relative_to] + (Decimal(1/2) * k2[relative_to] * h)

        return self.solve_function(function, values | { control_variable: x, relative_to: y})
    
    def get_k4(self, function: Function, values: dict[str, Decimal], k3: dict[str, Decimal], control_variable: str, relative_to: str, h: Decimal):
        x = values[control_variable] + h
        y = values[relative_to] + (k3[relative_to] * h)

        return self.solve_function(function, values | { control_variable: x, relative_to: y})

    def get_next_value(self, values: dict[str, Decimal], k1: dict[str, Decimal], k2: dict[str, Decimal], k3: dict[str, Decimal], k4: dict[str, Decimal], function: Function, h: Decimal):
        next_value = values[function.relative_to] + (Decimal(1 / 6) * (k1[function.relative_to] + (2 * k2[function.relative_to]) + (2 * k3[function.relative_to]) + k4[function.relative_to]) * h)

        return next_value

    def solve(self, edos: list[Function], variables: list[str], initial_values: list[Decimal], control_variable: str, h: Decimal, interval: list[Decimal]):
        solutions = [dict(zip(variables, initial_values)) | { control_variable: Decimal(interval[0]) }]
        n_steps = int((Decimal(interval[1]) - Decimal(interval[0])) / h)

        for i in range(1, n_steps + 1):
            control = Decimal(interval[0]) + h * i
            k1_dict = { }
            k2_dict = { }
            k3_dict = { }
            k4_dict = { }
            solution_dict = { control_variable: control }

            last_values = solutions[-1]
            
            for edo in edos:
                k1 = self.get_k1(edo, last_values)
                k1_dict[edo.relative_to] = k1
            
            for edo in edos:
                k2 = self.get_k2(edo, last_values, k1_dict, control_variable, edo.relative_to, h)
                k2_dict[edo.relative_to] = k2

            for edo in edos:
                k3 = self.get_k3(edo, last_values, k2_dict, control_variable, edo.relative_to, h)
                k3_dict[edo.relative_to] = k3

            for edo in edos:
                k4 = self.get_k4(edo, last_values, k3_dict, control_variable, edo.relative_to, h)
                k4_dict[edo.relative_to] = k4

            for edo in edos:
                next_value = self.get_next_value(last_values, k1_dict, k2_dict, k3_dict, k4_dict, edo, h)
                solution_dict[edo.relative_to] = next_value

            solutions.append(solution_dict)
        
        return solutions