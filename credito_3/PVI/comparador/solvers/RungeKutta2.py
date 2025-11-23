from decimal import Decimal, getcontext
from sympy import N, sympify
from models.Function import Function

class RungeKutta2:
    label: str = "Runge Kutta de 2° ordem"
    color: str = "midnightblue"

    getcontext().prec = 50

    def solve_function(self, function: Function, subs: dict[str, Decimal]):
        symp_expression = sympify(function.expression)
        return Decimal(str(N(symp_expression.evalf(subs=subs))))

    def get_k1(self, function: Function, values: dict[str, Decimal]):
        return self.solve_function(function, values)
    
    def get_k2(self, function: Function, values: dict[str, Decimal], k1: dict[str, Decimal], control_variable: str, relative_to: str, h: Decimal):
        x = values[control_variable] + (Decimal(3/4) * h)
        y = values[relative_to] + (Decimal(3/4) * k1[relative_to] * h)

        return self.solve_function(function, values | { control_variable: x, relative_to: y})

    def get_next_value(self, values: dict[str, Decimal], k1: dict[str, Decimal], k2: dict[str, Decimal], function: Function, h: Decimal):
        next_y = values[function.relative_to] + ((Decimal(1 / 3) * k1[function.relative_to]) + (Decimal(2 / 3) * k2[function.relative_to])) * h

        return next_y

    def solve(self, edos: list[Function], variables: list[str], initial_values: list[Decimal], control_variable: str, h: Decimal, interval: list[Decimal]):
        control = interval[0]
        solutions = [dict(zip(variables, initial_values)) | { control_variable: control }]

        while(control < interval[1]):
            next_control = control + h
            k1_dict = { }
            k2_dict = { }
            solution_dict = { control_variable: next_control }

            last_values = solutions[-1]
            
            for edo in edos:
                k1 = self.get_k1(edo, last_values)
                k1_dict[edo.relative_to] = k1
            
            for edo in edos:
                k2 = self.get_k2(edo, last_values, k1_dict, control_variable, edo.relative_to, h)
                k2_dict[edo.relative_to] = k2

            for edo in edos:
                next_value = self.get_next_value(last_values, k1_dict, k2_dict, edo, h)
                solution_dict[edo.relative_to] = next_value

            solutions.append(solution_dict)
            control = next_control
        
        return solutions