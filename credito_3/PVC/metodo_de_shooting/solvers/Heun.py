from decimal import Decimal, getcontext
from sympy import N, symbols, sympify
from models.Function import Function

class Heun:
    label: str = "Heun"
    color: str = "orange"

    getcontext().prec = 50

    def solve_function(self, function: Function, subs: dict[str, Decimal]):
        symp_expression = sympify(function.expression)

        return Decimal(str(N(symp_expression.evalf(subs=subs))))


    def predict_next_value(self, values: dict[str, Decimal], function: Function, h: Decimal):  
        f_xy = self.solve_function(function, values)
        next_y = values[function.relative_to] + f_xy * h

        return next_y

    def get_next_value(self, values: dict[str, Decimal], predicted_values: dict[str, Decimal], function: Function, h: Decimal):
        f_xy = self.solve_function(function, values)
        f_next_xy_predicted = self.solve_function(function, predicted_values)

        next_y = values[function.relative_to] + ((f_xy + f_next_xy_predicted) / 2) * h

        return next_y

    def solve(self, edos: list[Function], variables: list[str], initial_values: list[Decimal], control_variable: str, points: int, interval: list[Decimal]):
        solutions = [dict(zip(variables, initial_values)) | { control_variable: interval[0]}]
        h = Decimal((interval[1] - interval[0]) / points)

        for i in range(1, points + 1):
            control = Decimal(interval[0]) + h * i

            temp_vars = { control_variable: control }
            predicted_vars = { control_variable: control }
            last_values = solutions[-1]
            
            for edo in edos:
                predicted_next_value = self.predict_next_value(last_values, edo, h)
                predicted_vars[edo.relative_to] = predicted_next_value
            
            for edo in edos:
                next_value = self.get_next_value(last_values, predicted_vars, edo, h)
                temp_vars[edo.relative_to] = next_value

            solutions.append(temp_vars)
        
        return solutions