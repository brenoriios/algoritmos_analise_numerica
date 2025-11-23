from decimal import Decimal, getcontext
from sympy import N, sympify
from models.Function import Function

class Euler:
    label: str = "Euler"
    color: str = "red"
    
    getcontext().prec = 50

    def solve_function(self, function: Function, subs: dict[str, Decimal]):
        symp_expression = sympify(function.expression)

        return Decimal(str(N(symp_expression.evalf(subs=subs))))

    def get_next_value(self, values: dict[str, Decimal], function: Function, h: Decimal):
        f_xy = self.solve_function(function, values)
        next_y = values[function.relative_to] + f_xy * h

        return next_y

    def solve(self, edos: list[Function], variables: list[str], initial_values: list[Decimal], control_variable: str, h: Decimal, interval: list[Decimal]):
        control = interval[0]
        solutions = [dict(zip(variables, initial_values))]

        while(control < interval[1]):
            next_control = control + h
            temp_vars = { control_variable: next_control }
            last_values = solutions[-1]
            
            for edo in edos:                
                next_value = self.get_next_value(last_values, edo, h)
                temp_vars[edo.relative_to] = next_value

            solutions.append(temp_vars)
            control = next_control
        
        return solutions