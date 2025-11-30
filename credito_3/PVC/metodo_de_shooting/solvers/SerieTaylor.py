from decimal import Decimal, getcontext
from sympy import N, diff, symbols, sympify
from models.Function import Function

class SerieTaylor:
    label: str = "Série de Taylor"
    color: str = "fuchsia"

    getcontext().prec = 50

    def solve_function(self, function: Function, subs: dict[str, Decimal]):
        symp_expression = sympify(function.expression)
        return Decimal(str(N(symp_expression.evalf(subs=subs))))

    def diff_y(self, function: Function, control_variable: str):
        diff_x = diff(function.expression, control_variable)
        diff_y = diff(function.expression, function.relative_to)
        expression = f'({diff_x}) + (({diff_y}) * ({function.expression}))'

        return Function(expression, function.relative_to)

    def diff_yy(self, function: Function, control_variable: str):
        x = control_variable
        y = function.relative_to

        diff_x = diff(function.expression, x)
        diff_y = diff(function.expression, y)

        diff_xx = diff(diff_x, x)
        diff_yy = diff(diff_y, y)
        diff_xy = diff(diff_x, y)

        expression = f'({diff_xx}) + (2 * ({diff_xy}) * ({function.expression})) + (({diff_yy}) * (({function.expression}) ** 2)) + (({diff_x}) * ({diff_y})) + ((({diff_y}) ** 2) * ({function.expression}))'

        return Function(expression, function.relative_to)
    
    def get_next_value(self, values: dict[str, Decimal], function: Function, diffs: dict[str, Function], h: Decimal):
        sol_f_xy = self.solve_function(function, values)
        sol_diff_y = self.solve_function(diffs["y"], values)
        sol_diff_yy = self.solve_function(diffs["yy"], values)

        part_1 = values[function.relative_to] + (sol_f_xy * h)
        part_2 = (sol_diff_y / 2) * (h ** 2)
        part_3 = (sol_diff_yy / 6) * (h ** 3)
        next_value = part_1 + part_2 + part_3

        return next_value

    def solve(self, edos: list[Function], variables: list[str], initial_values: list[Decimal], control_variable: str, points: int, interval: list[Decimal]):
        solutions = [dict(zip(variables, initial_values))]
        diffs = {}

        #TODO - Testar com função própria
        for edo in edos:
            diffs[edo.relative_to] = {}
            
            diffs[edo.relative_to]["y"] = self.diff_y(edo, control_variable)
            diffs[edo.relative_to]["yy"] = self.diff_yy(edo, control_variable)

        h = Decimal((interval[1] - interval[0]) / points)

        for i in range(points):
            control = Decimal(interval[0]) + h * i
            temp_vars = { control_variable: control }
            last_values = solutions[-1]
            
            for edo in edos:                
                next_value = self.get_next_value(last_values, edo, diffs[edo.relative_to], h)
                temp_vars[edo.relative_to] = next_value

            solutions.append(temp_vars)
        
        return solutions