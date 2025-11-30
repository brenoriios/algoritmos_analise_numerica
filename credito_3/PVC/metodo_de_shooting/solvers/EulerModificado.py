from decimal import Decimal, getcontext
from sympy import N, symbols, sympify
from models.Function import Function

class EulerModificado:
    label: str = "Euler Modificado"
    color: str = "darkred"
    
    getcontext().prec = 50

    def solve_function(self, function: Function, subs: dict[str, Decimal]):
        symp_expression = sympify(function.expression)

        return Decimal(str(N(symp_expression.evalf(subs=subs))))

    def get_middle_value(self, values: dict[str, Decimal], function: Function, h: Decimal):
        f_xy = self.solve_function(function, values)

        next_y = values[function.relative_to] + f_xy * (h / 2)

        return next_y
    
    def get_next_value(self, values: dict[str, Decimal], middle_values: dict[str, Decimal], function: Function, h: Decimal):
        f_middle_xy = self.solve_function(function, middle_values)

        next_y = values[function.relative_to] + f_middle_xy * h

        return next_y

    def solve(self, edos: list[Function], variables: list[str], initial_values: list[Decimal], control_variable: str, points: int, interval: list[Decimal]):
        control = Decimal(interval[0])
        solutions = [dict(zip(variables, initial_values)) | { control_variable: interval[0]}]

        x0 = Decimal(interval[0])
        h = Decimal((interval[1] - interval[0]) / points)

        for i in range(1, points + 1):
            control = x0 + h * (i - 1)
            next_control = x0 + h * i
            middle_control = control + (h / 2)

            temp_vars = { control_variable: next_control }
            temp_middle_vars = { control_variable: middle_control }
            last_values = solutions[-1]
            
            for edo in edos:
                next_value_middle = self.get_middle_value(last_values, edo, h)
                temp_middle_vars[edo.relative_to] = next_value_middle

            for edo in edos:
                next_value = self.get_next_value(last_values, temp_middle_vars, edo, h)
                temp_vars[edo.relative_to] = next_value

            solutions.append(temp_vars)
        
        return solutions