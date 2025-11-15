

from dataclasses import dataclass
from decimal import Decimal
import json
import os
import traceback

from matplotlib import pyplot as plt
from sympy import N, symbols, sympify

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
    diff: Function
    first_point: Point
    h: Decimal
    interval: list[Decimal]

    def __init__(self, diff: Function, first_point: Point, h: Decimal, interval: list[Decimal]):
        self.diff = diff
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

    if "differential" not in json_data:
        raise KeyError("É necessário informar derivada")
    if "firstPoint" not in json_data:
        raise KeyError("É necessário informar o ponto inicial")
    if "h" not in json_data:
        raise KeyError("É necessário informar o valor de h")
    if "interval" not in json_data:
        raise KeyError("É necessário informar o intervalo")
    
    if "expression" not in json_data["differential"]:
        raise KeyError("É necessário informar a expressão da derivada")
    if "variables" not in json_data["differential"]:
        raise KeyError("É necessário informar a variável da expressão da derivada")
    if len(json_data["differential"]["variables"]) > 2:
        raise KeyError("É necessário informar no máximo 2 variáveis")
    if len(json_data["interval"]) != 2:
        raise KeyError("É necessário informar o inicio e fim do intervalo")
    if json_data["interval"][1] < json_data["interval"][0]:
        raise KeyError("O início do intervalo deve ser anterior ao fim")

    return InputData(
        Function(json_data["differential"]["expression"], json_data["differential"]["variables"]),
        Point(json_data["firstPoint"]["x"], json_data["firstPoint"]["y"]),
        Decimal(json_data["h"]),
        json_data["interval"]
    )

def predict_next_y(point: Point, differential: Function, h: Decimal):  
    f_xy = solve_function(differential, [point.x, point.y])
    next_y = point.y + f_xy * h

    return next_y

def get_next_y(point: Point, predicted_point: Point, differential: Function, h: Decimal):
    f_xy = solve_function(differential, [point.x, point.y])
    next_f_xy_predicted = solve_function(differential, [predicted_point.x, predicted_point.y])

    next_y = point.y + ((f_xy + next_f_xy_predicted) / 2) * h

    return next_y
    

def solve(input_data: InputData):
    solutions = [ input_data.first_point ]

    x = input_data.first_point.x
    point = input_data.first_point
    while(x < input_data.interval[1]):
        next_x = x + input_data.h

        next_y_predicted = predict_next_y(point, input_data.diff, input_data.h)
        next_y = get_next_y(point, Point(next_x, next_y_predicted), input_data.diff, input_data.h)

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