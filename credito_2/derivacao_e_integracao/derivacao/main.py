from dataclasses import dataclass
from decimal import Decimal, getcontext
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
class InputData:
    x_start: Decimal
    h: Decimal
    function: Function
    x_max: Decimal | None

    def __init__(
        self, x_start: Decimal, h: Decimal, function: Function, x_max: Decimal | None
    ):
        self.x_start = x_start
        self.h = h
        self.function = function
        self.x_max = x_max

    def __str__(self):
        data_parts = [
            f"{self.x_start} <= {self.function.variable} <= {self.x_max}",
            f"h (incremento de {self.function.variable}): {self.h}",
            f"f({self.function.variable}) = {self.function.expression}",
        ]

        return "\n".join(data_parts)


@dataclass
class Solution:
    original_function: list[Point]
    first_order_differentials: list[Point]
    second_order_differentials: list[Point]

    def __init__(
        self,
        original_function: list[Decimal],
        first_order_differentials: list[Decimal],
        second_order_differentials: list[Decimal],
    ):
        self.original_function = original_function
        self.first_order_differentials = first_order_differentials
        self.second_order_differentials = second_order_differentials


class SolutionException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


def get_data_from_json(file_path: str):
    dir_path = os.path.dirname(os.path.realpath(__file__))

    with open(f"{dir_path}/{file_path}", "r") as json_file:
        json_data = json.load(json_file)

    if "x_start" not in json_data:
        raise KeyError("É necessário informar o primeiro valor de x")
    if "h" not in json_data:
        raise KeyError("É necessário informar o incremento de x")
    if "function" not in json_data:
        raise KeyError("É necessário informar a função")

    if "expression" not in json_data["function"]:
        raise SolutionException("É necessário informar a expressão da função")
    if "variable" not in json_data["function"]:
        raise SolutionException(
            "É necessário informar a variável considerada na função"
        )

    return InputData(
        Decimal(json_data["x_start"]),
        Decimal(json_data["h"]),
        Function(
            json_data["function"]["expression"], json_data["function"]["variable"]
        ),
        Decimal(json_data["x_max"]) if "x_max" in json_data else None,
    )


def solve_function(function: Function, variable_value: Decimal):
    symp_expression = sympify(function.expression)
    symp_variable = symbols(function.variable)

    return Decimal(str(N(symp_expression.evalf(subs={symp_variable: variable_value}))))


def calc_1st_order_differential(points: list[Point], h: Decimal):
    p0 = points[-3]
    p2 = points[-1]

    return (p2.y - p0.y) / (2 * h)


def calc_2nd_order_differential(points: list[Point], h: Decimal):
    p0 = points[-3]
    p1 = points[-2]
    p2 = points[-1]

    return (p2.y - (2 * p1.y) + p0.y) / (h ** 2)


def get_differentials(input_data: InputData):
    x_start = input_data.x_start
    function = input_data.function
    h = input_data.h

    if h == 0:
        raise SolutionException("O valor de h não pode ser 0")

    p0 = Point(x_start - h, solve_function(function, x_start - h))
    p1 = Point(x_start, solve_function(function, x_start))

    input_data.x_max = (
        Decimal(p0.x + (h * 100)) if input_data.x_max is None else input_data.x_max
    )

    points = [p0, p1]
    first_order_differentials = []
    second_order_differentials = []
    x = p1.x

    while x < input_data.x_max:
        next_x = x + h
        points.append(Point(next_x, solve_function(function, next_x)))
        first_order_y = calc_1st_order_differential(points, h)
        second_order_y = calc_2nd_order_differential(points, h)

        first_order_differentials.append(Point(x, first_order_y))
        second_order_differentials.append(Point(x, second_order_y))

        x = next_x

    return Solution(points[1:], first_order_differentials, second_order_differentials)


def plot_points(solution: Solution):
    plt.plot(
        [p.x for p in solution.original_function],
        [p.y for p in solution.original_function],
        color="blue",
        linestyle="--",
        label="Função original",
    )

    plt.plot(
        [p.x for p in solution.first_order_differentials],
        [p.y for p in solution.first_order_differentials],
        color="orange",
        linestyle="--",
        label="Derivada de primeira ordem",
    )

    plt.plot(
        [p.x for p in solution.second_order_differentials],
        [p.y for p in solution.second_order_differentials],
        color="green",
        linestyle="--",
        label="Derivada de segunda ordem",
    )

    plt.title("Derivadas")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.grid(True)
    plt.legend()

    plt.savefig(f"{os.path.dirname(os.path.realpath(__file__))}/output")
    plt.show()


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
        solution = get_differentials(input_data)
        plot_points(solution)

        output_file.close()
    except SolutionException as ex:
        print(ex)
    except KeyError as e:
        print(f"Formato de entrada inválido. Chave faltando: {e}")
    except Exception as e:
        print(f"Erro ao solucionar o problema: {e}")
