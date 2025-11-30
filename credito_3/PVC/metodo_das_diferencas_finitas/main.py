from decimal import Decimal
import sys
from matplotlib import pyplot as plt
import json
import os

import numpy as np
from sympy import N, collect, expand, simplify, symbols, sympify

from models.Point import Point
from models.Coefficients import Coefficients
from models.InputData import InputData
from models.MatrixData import MatrixData
from solvers.GaussElimination import GaussElimination


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_data_from_json(file_path: str):
    dir_path = os.path.dirname(os.path.realpath(__file__))

    with open(f"{dir_path}/{file_path}", "r") as json_file:
        json_data = json.load(json_file)

    validate_input(json_data)
    
    return InputData(
        json_data["edo"],
        json_data["solution_variable"],
        Decimal(json_data["initial_value"]),
        Decimal(json_data["target_value"]),
        [Decimal(value) for value in json_data["interval"]],
        json_data["nodes"],
        json_data["analytical_solution"] if "analytical_solution" in json_data else None
    )

def validate_input(json_data):
    if "edo" not in json_data:
        raise KeyError("É necessário informar a equação diferencial ordinária (EDO)")
    if "solution_variable" not in json_data:
        raise KeyError("É necessário informar para qual variável será a solução final")
    if "target_value" not in json_data:
        raise KeyError("É necessário informar o valor alvo")
    if "interval" not in json_data:
        raise KeyError("É necessário informar o intervalo")
    if "nodes" not in json_data:
        raise KeyError("É necessário informar quantos pontos internos devem ser considerados")

def get_file_name(label: str, relative_to: str | None = None, control: str | None = None):
    return f'{label.lower()} {(control + relative_to) if relative_to != None and control != None else ""}'.replace(' ', '_')

def plt_save(control: str, relative_to: str, label: str):
    plt.xlabel(control)
    plt.ylabel(relative_to)
    plt.grid(True)
    plt.legend()

    directory = create_directory_if_not_exists("figures")

    plt.savefig(f"{directory}/{get_file_name(label, relative_to, control)}", dpi=300)
    plt.close()

def plot_points(solution: list[Point], label: str, color: str, control: str, relative_to: str, single: bool = True):
    plt.plot(
        [p.x for p in solution],
        [p.y for p in solution],
        color=color,
        linestyle="-",
        label=label,
    )

    if (single):
        plt_save(control, relative_to, label)

def create_directory_if_not_exists(path: str):
    base = f"{os.path.dirname(os.path.realpath(__file__))}/output"
    directory = f"{base}/{path}"

    if not os.path.exists(base):
        os.makedirs(base)

    if not os.path.exists(directory):
        os.makedirs(directory)
    
    return directory

def get_out_file(filename: str):
    directory = create_directory_if_not_exists("")
    file = open(f'{directory}/{filename}', 'w')

    return file

def create_points(solution: list[dict[str, Decimal]], variable: str, control_start: Decimal, h: Decimal):
    points = []
    for i in range(len(solution)):
        point = Point(control_start + (h * i), solution[i][variable])
        points.append(point)
    
    return points

def create_analytical_solution_points(input_data: InputData):
    points = []

    n = int((Decimal(input_data.interval[1]) - Decimal(input_data.interval[0])) / input_data.h)

    for i in range(n + 1):
        x = Decimal(input_data.interval[0]) + input_data.h * i
        points.append(Point(x, Decimal(str(N(sympify(input_data.analytical_solution).evalf(subs={input_data.control_variable: x}))))))
    
    return points

def print_system(matrix: list[list[Decimal]], results: list[Decimal], solution_variable: str):
    n = len(matrix)
    col_width = 5

    print("\nSistema Linear:\n")

    for i in range(n):
        row_str = "[ "
        for j in range(n):
            row_str += f"{matrix[i][j]:>{col_width}.4f} "
        row_str += "]"

        var_str = f"   {f"{solution_variable}{i}":>{col_width}}   "
        b_str = f"{results[i]:>.4f}"

        print(f"{row_str}  {var_str} = {b_str}")

    print()

def print_linear_system(matrix: list[list[Decimal]], results: list[Decimal], solution_variable: str):
    n = len(matrix)
    precision = 4
    col_width = len(str(round(max(np.concatenate(matrix).ravel().tolist() + results.tolist()), precision)))

    for i in range(n):
        row_str = "[ "
        for j in range(n):
            row_str += f"{matrix[i][j]:>{col_width}.{precision}f} "
        row_str += "]"

        var_str = f"   {f"{solution_variable}{i}":>{len(str(n)) + 1}}   "
        b_str = f"{results[i]:>{col_width}.{precision}f}"

        print(f"{row_str}  {var_str} = {b_str}")

def extract_coefficients(function: str, solution_variable: str, h: Decimal):
    var_prev, var_curr, var_next = symbols(f'{solution_variable}0 {solution_variable} {solution_variable}2')

    exp = f"({var_next} - (2 * {var_curr}) + {var_prev}) / ({h ** 2}) - ({function})"
    exp = f"({exp}) * -({h ** 2})"
    exp = expand(exp)

    coef_T_I0  = simplify(collect(exp, var_prev).coeff(var_prev))
    coef_T_I   = simplify(collect(exp, var_curr).coeff(var_curr))
    coef_T_I2  = simplify(collect(exp, var_next).coeff(var_next))
    rhs = simplify(exp - (coef_T_I * var_curr + coef_T_I0 * var_prev + coef_T_I2 * var_next))

    return Coefficients (
        coef_T_I0,
        coef_T_I,
        coef_T_I2,
        rhs
    )

def solve(input_data: InputData):
    function = input_data.edo
    solution_variable = input_data.solution_variable
    initial_value = input_data.initial_value
    target_value = input_data.target_value
    node_count = input_data.nodes
    a = input_data.interval[0]
    b = input_data.interval[1]
    h = (b - a) / (node_count + 1)

    coefficients = extract_coefficients(function, solution_variable, h)

    system_matrix = np.zeros((node_count, node_count))
    system_values = np.full(node_count, -coefficients.rhs, dtype=Decimal)

    for i in range(node_count):
        system_matrix[i, i] = coefficients.diag
        if i > 0:
            system_matrix[i, i - 1] = coefficients.prev
        if i < node_count - 1:
            system_matrix[i, i + 1] = coefficients.next
    
    system_values[0]  -= coefficients.prev * initial_value
    system_values[-1] -= coefficients.next * target_value

    solution = GaussElimination().solve(MatrixData(
        system_matrix,
        [f"{solution_variable}{i}" for i in range(len(system_matrix))],
        system_values
    ))

    print_linear_system(system_matrix, system_values, solution_variable)

    return solution

INPUT_PATH = "input.json"
OUTPUT_PATH = 'output.txt'

if __name__ == "__main__":
    try:
        input_data = get_data_from_json(INPUT_PATH)
        output_file = get_out_file(get_file_name("solution") + OUTPUT_PATH)

        solution = solve(input_data)

        print(solution)

    except KeyError as e:
        print(f"Formato de entrada inválido. {e}")
    except Exception as e:
        print(f"Erro ao solucionar o problema: {e}")