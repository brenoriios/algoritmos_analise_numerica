from dataclasses import dataclass
from decimal import Decimal
import json
import os
import random
import sys
import traceback

from matplotlib import pyplot as plt
import numpy as np

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
        [Decimal(value) for value in json_data["guesses"]] if "guesses" in json_data else [random.randint(1, 20), random.randint(21, 40)],
        json_data["guesses_for"],
        Decimal(json_data["target_value"]),
        json_data["target_for"],
        json_data["control_variable"],
        Decimal(json_data["h"]),
        json_data["interval"],
        json_data["method"] if "method" in json_data else None
    )

def validate_input(json_data):
    if "edos" not in json_data or len(json_data["edos"]) < 1:
        raise KeyError("É necessário informar as equações diferenciais ordinárias (EDOs)")
    if "variables" not in json_data:
        raise KeyError("É necessário informar as variáveis do sistema")
    if "guesses_for" not in json_data:
        raise KeyError("É necessário informar para qual variável os 'chutes' são")
    if "target_value" not in json_data:
        raise KeyError("É necessário informar o valor alvo")
    if "target_for" not in json_data:
        raise KeyError("É necessário informar para qual variável é o valor alvo")
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

    if len(json_data["guesses"]) != 2:
        raise KeyError("Informe apenas 2 'chutes'")
    if len(json_data["interval"]) != 2:
        raise KeyError("É necessário informar o inicio e fim do intervalo")
    if json_data["interval"][1] < json_data["interval"][0]:
        raise KeyError("O início do intervalo deve ser anterior ao fim")

def create_directory_if_not_exists(path: str):
    base = f"{os.path.dirname(os.path.realpath(__file__))}/output"
    directory = f"{base}/{path}"

    if not os.path.exists(base):
        os.makedirs(base)

    if not os.path.exists(directory):
        os.makedirs(directory)
    
    return directory

def plt_save(control: str, relative_to: str, label: str):
    plt.xlabel(control)
    plt.ylabel(relative_to)
    plt.grid(True)
    plt.legend()

    directory = create_directory_if_not_exists("figures")

    plt.savefig(f"{directory}/{get_file_name(label, relative_to, control)}", dpi=300)
    plt.close()

def plot_points(solution: list[Point], label: str, control: str, relative_to: str, single: bool = True):
    plt.plot(
        [p.x for p in solution],
        [p.y for p in solution],
        color=tuple(np.random.rand(3) * 0.8),
        linestyle="-",
        marker="o" if len(solution) < 52 else "",
        label=label,
    )

    if (single):
        plt_save(control, relative_to, label)

def get_file_name(label: str, relative_to: str, control: str):
    return f'{label.lower()} {control}{relative_to}'.replace(' ', '_')

def create_points(solution: list[dict[str, Decimal]], variable: str, control_start: Decimal, h: Decimal):
    points = []
    for i in range(len(solution)):
        point = Point(control_start + (h * i), solution[i][variable])
        points.append(point)
    
    return points

def plot_each(solution, label: str, edos: list[Function], control_variable: str, start: Decimal, h: Decimal):
    for edo in edos:
        points = create_points(solution, edo.relative_to, start, h)
        plot_points(points, label, control_variable, edo.relative_to)

def get_out_file(filename: str):
    directory = create_directory_if_not_exists("")
    file = open(f'{directory}/{filename}', 'w')

    return file

def write_iteration(file, iteration, guess_for, guess, guess_solution, target_for, target_value):
    file.writelines([
        str(iteration),
        ' | ',
        f'{guess_for}: {guess}',
        ' | ',
        f'{target_for}: {guess_solution:.9f}',
        ' | ',
        f'Erro: {abs(target_value - guess_solution):.9f}'
        '\n'])

INPUT_PATH = "input.json"
OUTPUT_PATH = 'output.txt'

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    try:
        input_data = get_data_from_json(INPUT_PATH)
        output_file = get_out_file(OUTPUT_PATH)
        
        first_guess = input_data.guesses[0]
        second_guess = input_data.guesses[1]

        iteration = 1
        solution = []
        method_instance = MethodEnum[input_data.method].value()

        input_data.initial_values[input_data.variables.index(input_data.guesses_for)] = first_guess
        first_guess_solution = method_instance.solve(input_data.edos, input_data.variables, input_data.initial_values, input_data.control_variable, input_data.h, input_data.interval)
        
        input_data.initial_values[input_data.variables.index(input_data.guesses_for)] = second_guess
        second_guess_solution = method_instance.solve(input_data.edos, input_data.variables, input_data.initial_values, input_data.control_variable, input_data.h, input_data.interval)
        
        solution.append(first_guess_solution)
        solution.append(second_guess_solution)

        output_file.writelines([f'Alvo: {input_data.target_for} = {input_data.target_value}', ' | ', f'Intervalo: [{input_data.interval[0]}, {input_data.interval[1]}]', '\n'])
        write_iteration(output_file, "Primeiro Chute", input_data.guesses_for, first_guess, first_guess_solution[-1][input_data.target_for], input_data.target_for, input_data.target_value)
        write_iteration(output_file, "Segundo Chute", input_data.guesses_for, second_guess, second_guess_solution[-1][input_data.target_for], input_data.target_for, input_data.target_value)

        last_guess = first_guess
        current_guess = second_guess
        while((solution[-1][-1][input_data.target_for] - solution[-2][-1][input_data.target_for]) > 0.01 and iteration < 9999):
            next_guess = last_guess + (input_data.target_value - solution[-2][-1][input_data.target_for]) * (current_guess - last_guess) / (solution[-1][-1][input_data.target_for] - solution[-2][-1][input_data.target_for])
            
            input_data.initial_values[input_data.variables.index(input_data.guesses_for)] = next_guess
            next_guess_solution = method_instance.solve(input_data.edos, input_data.variables, input_data.initial_values, input_data.control_variable, input_data.h, input_data.interval)
            solution.append(next_guess_solution)

            write_iteration(output_file, iteration, input_data.guesses_for, next_guess, next_guess_solution[-1][input_data.target_for], input_data.target_for, input_data.target_value)

            last_guess = current_guess
            current_guess = next_guess
            iteration += 1
            
        plot_each(solution[-1], method_instance.label, input_data.edos, input_data.control_variable, input_data.interval[0], input_data.h)

    except KeyError as e:
        print(f"Formato de entrada inválido. {e}")
    except Exception as e:
        print(f"Erro ao solucionar o problema: {e}")
