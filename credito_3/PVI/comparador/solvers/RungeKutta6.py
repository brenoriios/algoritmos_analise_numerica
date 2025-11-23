from decimal import Decimal, getcontext
from sympy import N, symbols, sympify
from models.Function import Function

class RungeKutta6:
    label: str = "Runge Kutta de 6° ordem"
    color: str = "deepskyblue"

    getcontext().prec = 50

    def solve_function(self, function: Function, subs: dict[str, Decimal]):
        symp_expression = sympify(function.expression)
        return Decimal(str(N(symp_expression.evalf(subs=subs))))
    
    def get_k1(self, function: Function, values: dict[str, Decimal]):
        return self.solve_function(function, values)
    
    def get_k2(self, function: Function, values: dict[str, Decimal], k1: dict[str, Decimal], control_variable: str, relative_to: str, h: Decimal):
        x = values[control_variable] + (Decimal(1/4) * h)
        y = values[relative_to] + (Decimal(1/4) * k1[relative_to] * h)

        return self.solve_function(function, values | { control_variable: x, relative_to: y})

    def get_k3(self, function: Function, values: dict[str, Decimal], k1: dict[str, Decimal], k2: dict[str, Decimal], control_variable: str, relative_to: str, h: Decimal):
        y_k1_part = Decimal(1/8) * k1[relative_to] * h
        y_k2_part = Decimal(1/8) * k2[relative_to] * h

        x = values[control_variable] + (Decimal(1/4) * h)
        y = values[relative_to] + (y_k1_part) + (y_k2_part)

        return self.solve_function(function, values | { control_variable: x, relative_to: y})

    def get_k4(self, function: Function, values: dict[str, Decimal], k2: dict[str, Decimal], k3: dict[str, Decimal], control_variable: str, relative_to: str, h: Decimal):
        y_k2_part = Decimal(1/2) * k2[relative_to] * h
        y_k3_part = k3[relative_to] * h

        x = values[control_variable] + (Decimal(1/2) * h)
        y = values[relative_to] - (y_k2_part) + (y_k3_part)

        return self.solve_function(function, values | { control_variable: x, relative_to: y})

    def get_k5(self, function: Function, values: dict[str, Decimal], k1: dict[str, Decimal], k4: dict[str, Decimal], control_variable: str, relative_to: str, h: Decimal):
        y_k1_part = Decimal(3/16) * k1[relative_to] * h
        y_k4_part = Decimal(9/16) * k4[relative_to] * h

        x = values[control_variable] + (Decimal(3/4) * h)
        y = values[relative_to] + (y_k1_part) + (y_k4_part)

        return self.solve_function(function, values | { control_variable: x, relative_to: y})

    def get_k6(self, function: Function, values: dict[str, Decimal], k1: dict[str, Decimal], k2: dict[str, Decimal], k3: dict[str, Decimal], k4: dict[str, Decimal], k5: dict[str, Decimal], control_variable: str, relative_to: str, h: Decimal):
        y_k1_part = Decimal(3/7) * k1[relative_to] * h
        y_k2_part = Decimal(2/7) * k2[relative_to] * h
        y_k3_part = Decimal(12/7) * k3[relative_to] * h
        y_k4_part = Decimal(12/7) * k4[relative_to] * h
        y_k5_part = Decimal(8/7) * k5[relative_to] * h

        x = values[control_variable] + h
        y = values[relative_to] - (y_k1_part) + (y_k2_part) + (y_k3_part) - (y_k4_part) + (y_k5_part)

        return self.solve_function(function, values | { control_variable: x, relative_to: y})

    def get_next_value(self, values: dict[str, Decimal], k1: dict[str, Decimal], k3: dict[str, Decimal], k4: dict[str, Decimal], k5: dict[str, Decimal], k6: dict[str, Decimal], function: Function, h: Decimal):
        k1_part = 7 * k1[function.relative_to]
        k3_part = 32 * k3[function.relative_to]
        k4_part = 12 * k4[function.relative_to]
        k5_part = 32 * k5[function.relative_to]
        k6_part = 7 * k6[function.relative_to]

        next_value = values[function.relative_to] + (Decimal(1 / 90) * (k1_part + k3_part + k4_part + k5_part + k6_part) * h)

        return next_value

    def solve(self, edos: list[Function], variables: list[str], initial_values: list[Decimal], control_variable: str, h: Decimal, interval: list[Decimal]):
        control = interval[0]
        solutions = [dict(zip(variables, initial_values)) | { control_variable: control }]

        while(control < interval[1]):
            next_control = control + h
            k1_dict = { }
            k2_dict = { }
            k3_dict = { }
            k4_dict = { }
            k5_dict = { }
            k6_dict = { }
            solution_dict = { control_variable: next_control }

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
                k4 = self.get_k4(edo, last_values, k2_dict, k3_dict, control_variable, edo.relative_to, h)
                k4_dict[edo.relative_to] = k4

            for edo in edos:
                k5 = self.get_k5(edo, last_values, k1_dict, k4_dict, control_variable, edo.relative_to, h)
                k5_dict[edo.relative_to] = k5
            
            for edo in edos:
                k6 = self.get_k6(edo, last_values, k1_dict, k2_dict, k3_dict, k4_dict, k5_dict, control_variable, edo.relative_to, h)
                k6_dict[edo.relative_to] = k6

            for edo in edos:
                next_value = self.get_next_value(last_values, k1_dict, k3_dict, k4_dict, k5_dict, k6_dict, edo, h)
                solution_dict[edo.relative_to] = next_value

            solutions.append(solution_dict)
            control = next_control
        
        return solutions
