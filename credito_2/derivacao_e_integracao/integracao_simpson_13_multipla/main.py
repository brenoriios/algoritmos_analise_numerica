from dataclasses import dataclass
from decimal import Decimal, getcontext
import math
import traceback
import matplotlib.pyplot as plt
import json
import os

import numpy as np
import sympy as sp

getcontext().prec = 50


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
class Function:
    expression: str
    variable: str

    def __str__(self):
        return f"y = {self.expression}"

@dataclass
class Solution:
    integral_value: Decimal
    error: Decimal

    def __init__(self, integral_value: Decimal, error: Decimal):
        self.integral_value = integral_value
        self.error = error
    
    def __str__(self):
        return f"I = {self.integral_value} | Erro = {self.error}"

@dataclass
class InputData:
    function: Function
    points: list[Decimal]

    def __init__(self, function: Function, points: list[Decimal]):
        self.function = function
        self.points = points

class SolutionException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

def get_data_from_json(file_path: str):
    dir_path = os.path.dirname(os.path.realpath(__file__))

    with open(f"{dir_path}/{file_path}", "r") as json_file:
        json_data = json.load(json_file)

    if "function" not in json_data:
        raise KeyError("É necessário informar a função")
    if "points" not in json_data:
        raise KeyError("É necessário informar os pontos considerados")

    if (len(json_data["points"]) + 1) % 3 != 0:
        raise SolutionException("Para a regra de Simpson de 1/3 múltipla é necessário que seja possível formar apenas conjuntos de 3 pontos")
    if "expression" not in json_data["function"]:
        raise SolutionException("É necessário informar a expressão da função")
    if "variable" not in json_data["function"]:
        raise SolutionException("É necessário informar a variável considerada na função")

    return InputData(
        Function(json_data["function"]["expression"], json_data["function"]["variable"]),
        [Decimal(x) for x in json_data["points"]]
    )

def solve_function(function: Function, variable_value: Decimal):
    symp_expression = sp.sympify(function.expression)
    symp_variable = sp.symbols(function.variable)

    return Decimal(str(sp.N(symp_expression.evalf(subs={symp_variable: variable_value}))))

def calc_integral_by_simpson_13(function: Function, points: list[Decimal]):
    a = points[0]
    b = points[-1]
    n = len(points) - 1

    f_x0 = solve_function(function, a)
    f_xn = solve_function(function, b)
    sum_odd = sum([solve_function(function, x) for x in points[1:-1:2]])
    sum_even = sum([solve_function(function, x) for x in points[2:-2:2]])

    width = b - a
    mean_height = (f_x0 + (4 * sum_odd) + (2 * sum_even) + f_xn) / (3 * n)
    
    integral = width * mean_height
    error = calc_error(function, a, b, n)

    return Solution(integral, error)

def calc_error(function: Function, a: Decimal, b: Decimal, n: Decimal):
    diff_4th_order = Function(calc_4th_order_differential(function), function.variable)
    
    h = (b - a) / n

    mean_4th_order_diff = sum([solve_function(diff_4th_order, i * h) for i in range(1, n + 1)]) / n

    error_total = (((b - a) ** 5) / (180 * (n ** 4))) * mean_4th_order_diff
    
    return abs(error_total)

def calc_4th_order_differential(function: Function):
    symp_expression = sp.sympify(function.expression)
    symp_variable = sp.symbols(function.variable)

    differential = sp.diff(symp_expression, symp_variable, 4)

    return differential

def calc_integral(input_data: InputData):
    integral = calc_integral_by_simpson_13(input_data.function, input_data.points)
    
    print(integral)
    
    return integral


def print_list(items: list):
    print(f"[ {', '.join([str(item) for item in items])} ]")


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
        solution = calc_integral(input_data)

        output_file.close()
    except SolutionException as ex:
        print(ex)
    except KeyError as e:
        print(f"Formato de entrada inválido. {e}")
    except Exception as e:
        print(f"Erro ao solucionar o problema: {e}")
