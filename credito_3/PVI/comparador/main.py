from dataclasses import dataclass
from decimal import Decimal
from io import TextIOWrapper
import json
import os
import sys
import traceback

from matplotlib import pyplot as plt
import numpy as np
from sympy import N, sympify

from models.InputData import InputData
from models.Function import Function
from models.Point import Point
from enums.MethodEnum import MethodEnum

def get_data_from_json(file_path: str):
    dir_path = os.path.dirname(os.path.realpath(__file__))

    with open(f"{dir_path}/{file_path}", "r") as json_file:
        json_data = json.load(json_file)

    validate_input(json_data)
    
    return InputData(
        [Function(edo["expression"], edo["relative_to"]) for edo in json_data["edos"]],
        json_data["variables"],
        [Decimal(value) for value in json_data["initial_values"]],
        json_data["control_variable"],
        Decimal(json_data["h"]),
        json_data["interval"],
        json_data["analytical_solution"] if "analytical_solution" in json_data else None,
        json_data["method"] if "method" in json_data else None
    )

def validate_input(json_data):
    if "edos" not in json_data or len(json_data["edos"]) < 1:
        raise KeyError("É necessário informar as equações diferenciais ordinárias (EDOs)")
    if "variables" not in json_data:
        raise KeyError("É necessário informar as variáveis do sistema")
    if "initial_values" not in json_data:
        raise KeyError("É necessário informar os valores iniciais das variáveis do sistema")
    if "control_variable" not in json_data:
        raise KeyError("É necessário informar qual o nome da variável incremental do sistema")
    if "h" not in json_data:
        raise KeyError("É necessário informar o valor de h")
    if "interval" not in json_data:
        raise KeyError("É necessário informar o intervalo")
    
    for edo in json_data["edos"]:
        if "expression" not in edo:
            raise KeyError("É necessário informar a expressão de todas as equações diferenciais ordinárias (EDOs)")
        if "relative_to" not in edo:
            raise KeyError("É necessário informar quem a equação diferencial ordinária (EDO) representa no sistema")

    if len(json_data["variables"]) != len(json_data["initial_values"]):
        raise KeyError("Todas as variáveis devem possuir um valor inicial")
    if len(json_data["interval"]) != 2:
        raise KeyError("É necessário informar o inicio e fim do intervalo")
    if json_data["interval"][1] < json_data["interval"][0]:
        raise KeyError("O início do intervalo deve ser anterior ao fim")

def create_directory_if_not_exists(directory: str):
    base = f"{os.path.dirname(os.path.realpath(__file__))}/output"
    path = f"{base}/{directory}"

    if not os.path.exists(base):
        os.makedirs(base)

    if not os.path.exists(path):
        os.makedirs(path)
    
    return path

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
        marker="" if len(solution) < 52 else "",
        label=label,
    )

    if (single):
        plt_save(control, relative_to, label)

def get_file_name(label: str, relative_to: str | None = None, control: str | None = None):
    return f'{label.lower()} {(control + relative_to) if relative_to != None and control != None else ""}'.replace(' ', '_')

def create_points(solution: list[dict[str, Decimal]], variable: str, control_start: Decimal, h: Decimal):
    points = []
    for i in range(len(solution)):
        point = Point(control_start + (h * i), solution[i][variable])
        points.append(point)
    
    return points

def create_analytical_solution_points(input_data: InputData):
    points = []

    x = input_data.interval[0]
    while x <= input_data.interval[1]:
        points.append(Point(x, Decimal(str(N(sympify(input_data.analytical_solution).evalf(subs={input_data.control_variable: x}))))))
        x += input_data.h
    
    return points

def plot_each(solution, analytical_solution, label: str, color: str, input_data: InputData):
    for edo in input_data.edos:
        if analytical_solution != None:
            plot_points(analytical_solution, "Solução Analítica", "black", input_data.control_variable, edo.relative_to, single=False)

        points = create_points(solution, edo.relative_to, input_data.interval[0], input_data.h)
        plot_points(points, label, color, input_data.control_variable, edo.relative_to, single=False)

        plt_save(input_data.control_variable, edo.relative_to, label)

def plot_compare(solutions, analytical_solution, input_data: InputData):
    for edo in input_data.edos:
        if analytical_solution != None:
            plot_points(analytical_solution, "Solução Analítica", "black", input_data.control_variable, edo.relative_to)

        for method in MethodEnum:
            method_instance = method.value()
            solution = solutions[method.name]
            
            points = create_points(solution, edo.relative_to, input_data.interval[0], input_data.h)
            plot_points(points, method_instance.label, method_instance.color, input_data.control_variable, edo.relative_to, single=False)

        plt_save(input_data.control_variable, edo.relative_to, "comparativo")

def get_out_file(filename: str):
    directory = create_directory_if_not_exists("iteration_logs")
    file = open(f'{directory}/{filename}', 'w')

    return file

def write_solution(output_file: TextIOWrapper, solution_list: dict[str, Decimal], relative_to: str, analytic_solution: list[Point] | None):
    for i in range(len(solution_list)):
        solution_dict = solution_list[i]
        line_parts = []

        for variable in solution_dict:
            line_parts.append(f"{variable}: {solution_dict[variable]}")

        if (analytic_solution != None):
            line_parts.append(f"Erro: {abs(analytic_solution[i].y) - solution_dict[relative_to]}")

        output_file.write(" | ".join(line_parts) + "\n")
    

INPUT_PATH = "input.json"
OUTPUT_FILENAME = 'output.txt'

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    try:
        input_data = get_data_from_json(INPUT_PATH)
        analytical_solution = create_analytical_solution_points(input_data)

        if (input_data.method is None):
            solutions = {}
            for method in MethodEnum:
                method_instance = method.value()
                output_file = get_out_file(f"{get_file_name(method_instance.label)}_{OUTPUT_FILENAME}")

                solutions[method.name] = method_instance.solve(input_data.edos, input_data.variables, input_data.initial_values, input_data.control_variable, input_data.h, input_data.interval)
                plot_each(solutions[method.name], analytical_solution, method_instance.label, method_instance.color, input_data)
                write_solution(output_file, solutions[method.name], input_data.edos[-1].relative_to, analytical_solution)

            plot_compare(solutions, analytical_solution, input_data)
        else:
            method_instance = MethodEnum[input_data.method].value()
            output_file = get_out_file(f"{method_instance.label}_{OUTPUT_FILENAME}")

            solution = method_instance.solve(input_data.edos, input_data.variables, input_data.initial_values, input_data.control_variable, input_data.h, input_data.interval)
            plot_each(solution, analytical_solution, method_instance.label, method_instance.color, input_data)
            write_solution(output_file, solution, input_data.edos[-1].relative_to, analytical_solution)

    except KeyError as e:
        print(f"Formato de entrada inválido. {e}")
    except Exception as e:
        print(f"Erro ao solucionar o problema: {e}")
