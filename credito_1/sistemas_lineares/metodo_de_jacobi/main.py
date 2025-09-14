from dataclasses import dataclass
from enum import Enum
from io import TextIOWrapper
import math
import os
import traceback
from sympy import Eq, evalf, solve, sympify, symbols, N
import json
from decimal import Decimal, getcontext
import copy

getcontext().prec = 50

@dataclass
class InputData:
    system: list[str]
    variables: list[str]
    initial_values: list[Decimal]
    tolerated_variation: Decimal

@dataclass
class SystemData:
    expressions: list[str]
    variables: list[str]

class SolutionException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

def get_data_from_json(file_path: str):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    with open(f'{dir_path}/{file_path}', 'r') as json_file:
        data = json.load(json_file)

    return InputData(
        data['system'], 
        data['variables'], 
        [Decimal(value) for value in data['initial_values']],
        Decimal(data['tolerated_variation'])
    )

def get_out_file(file_path: str):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file = open(f'{dir_path}/{file_path}', 'w', encoding='UTF-8')

    return file

def format_value(value: Decimal):
    integer_part_digits_count = len(str(int(value)))

    return f'{value:>{15 if integer_part_digits_count < 15 else integer_part_digits_count}.10f}'

def write_dict(dictionary: dict, file: TextIOWrapper):
    for key, value in dictionary.items():
        file.write(f'{key} = {value}\n')

def solve_function(expression: str, variables: dict[str, Decimal]):
    for key, value in variables.items():
        expression = expression.replace(key, str(value))

    left, right = expression.split("=")
    
    left_symp = sympify(left)
    right_symp = sympify(right)
    
    symp_expression = Eq(left_symp, right_symp)
    
    solutions_sympy = solve(symp_expression)

    decimal_solutions = [Decimal(str(sol)) for sol in solutions_sympy]
    
    return decimal_solutions

def reverse_dict(dictionary: dict):
    reversed_dictionary = {}
    while dictionary:
        key, value = dictionary.popitem()
        reversed_dictionary[key] = value

    return reversed_dictionary

def solve_for_jacobi(data: SystemData, values: dict[str, Decimal]):
    solution: dict[str, Decimal] = {}

    for i in range(len(data.expressions)):
        filtered_values = copy.deepcopy(values)
        expression = data.expressions[i]
        variable = data.variables[i]
        filtered_values.pop(variable)
        solution[variable] = solve_function(expression, filtered_values)[0]
    
    return solution

def jacobi_solve(data: InputData):
    old_values: dict[str, Decimal] = dict(zip(data.variables, data.initial_values))
    values = old_values
    system: SystemData = SystemData(data.system, data.variables)
    abs_variation = [math.inf for _ in system.expressions]
    rel_variation = [math.inf for _ in system.expressions]

    OUTPUT_FILE.write('Valores Iniciais\n')
    write_dict(old_values, OUTPUT_FILE)
    iteration = 1
    while((max(abs_variation) > data.tolerated_variation or max(rel_variation) > data.tolerated_variation and iteration <= MAX_ITERATIONS)):
        values = solve_for_jacobi(system, values)
        abs_variation = calc_abs_variation(old_values, values)
        rel_variation = calc_rel_variation(old_values, values)
        old_values = values
        OUTPUT_FILE.write(f'\nIteração {iteration}\n')
        OUTPUT_FILE.write('\nSolução\n')
        write_dict(values, OUTPUT_FILE)
        OUTPUT_FILE.write('\nVariação Absoluta\n')
        OUTPUT_FILE.write(f'[{', '.join([str(value) for value in abs_variation])}]')
        OUTPUT_FILE.write(f'\nMaior variação absoluta:\n{max(abs_variation)}')
        OUTPUT_FILE.write('\n\nVariação Relativa\n')
        OUTPUT_FILE.write(f'[{', '.join([str(value) for value in rel_variation])}]')
        OUTPUT_FILE.write(f'\nMaior variação relativa:\n{max(rel_variation)}')
        OUTPUT_FILE.write('\n\n----------------------------------------------------------\n')

        print([f'{key}: {str(value)}' for key, value in values.items()])
        iteration += 1
    
    if(iteration > MAX_ITERATIONS):
        OUTPUT_FILE.write(f'\nNão foi possível convergir em {MAX_ITERATIONS} iterações\n')
    else:
        OUTPUT_FILE.write(f'\nVariação menor do que a tolerada, resultado encontrado na iteração {iteration - 1}\n')    
    
def calc_abs_variation(old_solution: dict[str, Decimal], current_solution: dict[str, Decimal]):
    return [abs(old_solution[key] - current_solution[key]) for key in current_solution.keys()]

def calc_rel_variation(old_solution: dict[str, Decimal], current_solution: dict[str, Decimal]):
    if (0 in current_solution.values()):
        return 0
    return [abs((current_solution[key] - old_solution[key]) / current_solution[key]) for key in current_solution.keys()]

INPUT_PATH = 'input.json'
OUTPUT_PATH = 'output.txt'
OUTPUT_FILE = get_out_file(OUTPUT_PATH)
MAX_ITERATIONS = 9999

if __name__ == '__main__':
    try:
        data = get_data_from_json(INPUT_PATH)
        solution = jacobi_solve(data)
    except SolutionException as ex:
        print(ex)
    except KeyError as e:
        print(f"Formato de entrada inválido. Chave faltando: {e}")
    except Exception as e:
        print(f'Erro ao solucionar o problema: {e}')
        traceback.print_exc()
    
    OUTPUT_FILE.close()
