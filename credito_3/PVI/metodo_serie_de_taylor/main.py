

from dataclasses import dataclass
from decimal import Decimal, getcontext
import json
import os

from matplotlib import pyplot as plt
from sympy import *

getcontext().prec = 50

class SolutionException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

@dataclass
class Function:
    expression: str
    variables: list[str]

    def __str__(self):
        return f"f({self.variable}) = {self.expression}"
    
@dataclass
class Point:
    x: Decimal
    y: Decimal

    def __init__(self, x: Decimal, y: Decimal):
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x:.9f}, {self.y:.9f})"

@dataclass
class InputData:
    edo: Function
    first_point: Point
    h: Decimal
    interval: list[Decimal]

    def __init__(self, edo: Function, first_point: Point, h: Decimal, interval: list[Decimal]):
        self.edo = edo
        self.first_point = first_point
        self.h = h
        self.interval = interval


def solve_function(function: Function, variable_values: list[Decimal]):
    symp_expression = sympify(function.expression)
    symp_variables = symbols(function.variables)

    return Decimal(str(N(symp_expression.evalf(subs=dict(zip(symp_variables, variable_values))))))

def get_data_from_json(file_path: str):
    dir_path = os.path.dirname(os.path.realpath(__file__))

    with open(f"{dir_path}/{file_path}", "r") as json_file:
        json_data = json.load(json_file)

    if "edo" not in json_data:
        raise KeyError("É necessário informar a equação diferencial ordinária (EDO)")
    if "firstPoint" not in json_data:
        raise KeyError("É necessário informar o ponto inicial")
    if "h" not in json_data:
        raise KeyError("É necessário informar o valor de h")
    if "interval" not in json_data:
        raise KeyError("É necessário informar o intervalo")
    
    if "expression" not in json_data["edo"]:
        raise KeyError("É necessário informar a expressão da equação diferencial ordinária (EDO)")
    if "variables" not in json_data["edo"]:
        raise KeyError("É necessário informar as variáveis da expressão da equação diferencial ordinária (EDO)")
    if len(json_data["edo"]["variables"]) > 2:
        raise KeyError("É necessário informar no máximo 2 variáveis")
    if len(json_data["interval"]) != 2:
        raise KeyError("É necessário informar o inicio e fim do intervalo")
    if json_data["interval"][1] < json_data["interval"][0]:
        raise KeyError("O início do intervalo deve ser anterior ao fim")

    return InputData(
        Function(json_data["edo"]["expression"], json_data["edo"]["variables"]),
        Point(json_data["firstPoint"]["x"], json_data["firstPoint"]["y"]),
        Decimal(json_data["h"]),
        json_data["interval"]
    )


def diff_y(function: Function):
    diff_x = diff(function.expression, function.variables[0])
    diff_y = diff(function.expression, function.variables[1])
    expression = f'({diff_x}) + (({diff_y}) * ({function.expression}))'

    return Function(expression, function.variables)

def diff_yy(function: Function):
    x = function.variables[0]
    y = function.variables[1]

    diff_x = diff(function.expression, x)
    diff_y = diff(function.expression, y)

    diff_xx = diff(diff_x, x)
    diff_yy = diff(diff_y, y)
    diff_xy = diff(diff_x, y)

    expression = f'({diff_xx}) + (2 * ({diff_xy}) * ({function.expression})) + (({diff_yy}) * (({function.expression}) ** 2)) + (({diff_x}) * ({diff_y})) + ((({diff_y}) ** 2) * ({function.expression}))'

    return Function(expression, function.variables)

def solve(input_data: InputData):
    solutions = [ input_data.first_point ]

    h = input_data.h
    x = input_data.first_point.x
    point = input_data.first_point

    #TODO - Testar com função própria
    edo_diff_y = diff_y(input_data.edo)
    edo_diff_yy = diff_yy(input_data.edo)

    while(x < input_data.interval[1]):
        sol_f_xy = solve_function(input_data.edo, [point.x, point.y])
        sol_diff_y = solve_function(edo_diff_y, [point.x, point.y])
        sol_diff_yy = solve_function(edo_diff_yy, [point.x, point.y])

        next_x = x + h
        part_1 = point.y + (sol_f_xy * h)
        part_2 = (sol_diff_y / 2) * (h ** 2)
        part_3 = (sol_diff_yy / 6) * (h ** 3)
        next_y = part_1 + part_2 + part_3

        point = Point(next_x, next_y)
        solutions.append(point)
        x = next_x
    
    return solutions

def plot_points(solutions: list[Point]):
    plt.plot(
        [p.x for p in solutions],
        [p.y for p in solutions],
        color="blue",
        linestyle="-",
        marker="o",
    )

    plt.xlabel("x")
    plt.ylabel("y")
    plt.grid(True)

    plt.savefig(f"{os.path.dirname(os.path.realpath(__file__))}/output")
    plt.show()

def get_output_file(file_path: str):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file = open(f"{dir_path}/{file_path}", "w")

    return file

INPUT_PATH = "input.json"
OUTPUT_PATH = "output.txt"

if __name__ == "__main__":
    try:
        output_file = get_output_file(OUTPUT_PATH)
        input_data = get_data_from_json(INPUT_PATH)
        solutions = solve(input_data)
        plot_points(solutions)

        for solution in solutions:
            print(str(solution))

        output_file.close()
    except SolutionException as ex:
        print(ex)
    except KeyError as e:
        print(f"Formato de entrada inválido. {e}")
    except Exception as e:
        print(f"Erro ao solucionar o problema: {e}")