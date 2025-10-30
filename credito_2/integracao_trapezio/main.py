from dataclasses import dataclass
from decimal import Decimal, getcontext
import math
import traceback
import matplotlib.pyplot as plt
import json
import os

import numpy as np
from sympy import N, sqrt, symbols, sympify

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

    def __init__(self, integral_value, error):
        self.integral_value = integral_value
        self.error = error
    
    def __str__(self):
        return f"I = {self.integral_value} | Erro = {self.error}"

@dataclass
class InputData:
    function: Function
    a: Decimal
    b: Decimal
    error: Decimal

    def __init__(self, function: Function, a: Decimal, b: Decimal, error: Decimal):
        self.function = function
        self.a = a
        self.b = b
        self.error = error

    def __str__(self):
        return f"f({self.function.variable}) = {self.function.expression} | {self.a} <= x <= {self.b}"

class SolutionException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

def get_data_from_json(file_path: str):
    dir_path = os.path.dirname(os.path.realpath(__file__))

    with open(f"{dir_path}/{file_path}", "r") as json_file:
        json_data = json.load(json_file)

    if "a" not in json_data or "b" not in json_data:
        raise KeyError("É necessário informar os pontos 'a' e 'b'")
    if "function" not in json_data:
        raise KeyError("É necessário informar a função")
    if "error" not in json_data:
        raise KeyError("É necessário informar o erro tolerado")

    if "expression" not in json_data["function"]:
        raise SolutionException("É necessário informar a expressão da função")
    if "variable" not in json_data["function"]:
        raise SolutionException("É necessário informar a variável considerada na função")

    return InputData(
        Function(json_data["function"]["expression"], json_data["function"]["variable"]),
        Decimal(json_data["a"]),
        Decimal(json_data["b"]),
        Decimal(json_data["error"])
    )

def solve_function(function: Function, variable_value: Decimal):
    symp_expression = sympify(function.expression)
    symp_variable = symbols(function.variable)

    return Decimal(str(N(symp_expression.evalf(subs={symp_variable: variable_value}))))

def calc_integral_by_trapeziums(function: Function, points: list[Decimal], n: Decimal):
    a = points[0]
    b = points[-1]

    f_x0 = solve_function(function, a)
    f_xn = solve_function(function, b)
    sum_f_xi = sum([solve_function(function, x) for x in points[1:-1]])

    mean_height = (f_x0 + 2 * sum_f_xi + f_xn) / (2 * n)
    width = b - a
    integral = width * mean_height
    error = calc_error(function, a, b, n)

    return Solution(integral, error)

def calc_error(function: Function, a: Decimal, b: Decimal, n: Decimal):
    h = (b - a) / n
    
    sum_2nd_order_diff = sum([
        calc_2nd_order_differential([
            Point((i - 1) * h, solve_function(function, (i - 1) * h)),
            Point((i * h), solve_function(function, (i * h))),
            Point((i + 1) * h, solve_function(function, (i + 1) * h))
        ], h) for i in range(n + 1)])

    error_total = ((b - a) ** 3) / (12 * (n ** 3)) * sum_2nd_order_diff
    
    return abs(error_total)

def calc_2nd_order_differential(points: list[Point], h: Decimal):
    p0 = points[-3]
    p1 = points[-2]
    p2 = points[-1]

    differential = (p2.y - (2 * p1.y) + p0.y) / (h ** 2)

    return differential

def calc_integral(input_data: InputData):
    n = 1
    error = math.inf
    solutions = []

    while(error > input_data.error and n < 100):
        points = get_points(input_data.a, input_data.b, n)
        solution = calc_integral_by_trapeziums(input_data.function, points, n)
        print(f"{n} | {str(solution)}")
        solutions.append(solution)

        error = solution.error
        n += 1
    
    return solutions

def get_points(a: Decimal, b: Decimal, n: int):
    h = (b - a) / n
    points = []

    current_point = a
    while current_point < b:
        points.append(current_point)
        current_point += h
    
    return points


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
        traceback.print_exc()
