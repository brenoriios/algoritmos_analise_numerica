from dataclasses import dataclass
from enum import Enum
from io import TextIOWrapper
import os
from sympy import Eq, solve, sympify, symbols, N
import json
from decimal import Decimal, getcontext
import copy

getcontext().prec = 50

@dataclass
class MatrixData:
    matrix: list[list[float]]
    variables: list[str]
    results: list[float]

class SolutionException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

def get_data_from_json(file_path: str):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    with open(f'{dir_path}/{file_path}', 'r') as json_file:
        data = json.load(json_file)

    return MatrixData(
        data['matrix'],
        data['variables'],
        data['results']
    )

def get_out_file(file_path: str):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file = open(f'{dir_path}/{file_path}', 'w', encoding='UTF-8')

    return file

def print_matrix(data: MatrixData, only_matrix: bool = False):
    for line_index in range(len(data.matrix)):
        line_parts = ['|']
        for column in data.matrix[line_index]:
            line_parts.append(format_value(column))

        line_parts.append('|')
        
        if not only_matrix:
            line_parts.extend([data.variables[line_index], '|', '=', format_value(Decimal(data.results[line_index]))])

        print(' '.join(line_parts))
        
def write_matrix(data: MatrixData, file: TextIOWrapper, only_matrix: bool = False):
    for line_index in range(len(data.matrix)):
        line_parts = ['|']
        for column in data.matrix[line_index]:
            line_parts.append(format_value(column))

        line_parts.append('|')
        
        if not only_matrix:
            line_parts.extend([data.variables[line_index], '|', '=', format_value(Decimal(data.results[line_index]))])

        file.write(f'{' '.join(line_parts)}\n')

def format_value(value: Decimal):
    integer_part_digits_count = len(str(int(value)))

    return f'{value:>{15 if integer_part_digits_count < 15 else integer_part_digits_count}.10f}'

def write_dict(dictionary: dict, file: TextIOWrapper):
    for key, value in dictionary.items():
        file.write(f'{key} = {value}\n')

def solve_function(expression: str, result: float, variable: str):
    symp_expression = sympify(expression)
    symp_variable = symbols(variable)
    
    return solve(Eq(symp_expression, result), symp_variable)

def solve_matrix(data: MatrixData):
    invalid_matrix = check_invalid_matrix_by_input(data)
    if(invalid_matrix):
        raise(SolutionException(f'Erro: {invalid_matrix}'))

    system: list[str] = []
    solutions: dict = {}
    for line_index in range(len(data.matrix)):
        expression_parts = []
        for column_index in range(len(data.matrix[line_index])):
            expression_parts.append(f'({data.matrix[line_index][column_index]} * {data.variables[column_index]})')
        expression = ' + '.join(expression_parts)
        system.append(expression)
    
    for line_index in range(len(data.matrix) - 1, -1, -1):
        variable = data.variables[line_index]
        for key, value in solutions.items():
            system[line_index] = system[line_index].replace(key, str(value))
            
        solution = solve_function(system[line_index], data.results[line_index], variable)
        solutions[variable] = solution[0]

    solutions = reverse_dict(solutions)
    
    return solutions

def reverse_dict(dictionary: dict):
    reversed_dictionary = {}
    while dictionary:
        key, value = dictionary.popitem()
        reversed_dictionary[key] = value

    return reversed_dictionary

def check_invalid_matrix(matrix: list):
    if not matrix:
        return "Matriz vazia"
    
    num_rows = len(matrix)
    num_cols = len(matrix[0])
    
    for row in matrix:
        if len(row) != num_cols:
            return "Matriz mal formada"
    
    if num_rows != num_cols:
        return "Matriz não é quadrada"
    
    return False

def check_invalid_matrix_by_input(data: MatrixData):
    invalid_matrix = check_invalid_matrix(data.matrix)
    if invalid_matrix:
        return invalid_matrix
    if(len(data.matrix) != len(data.results) or len(data.matrix) != len(data.variables)):
        return 'Matriz mal formada'

def get_diagonal_matrix(input_data: MatrixData):
    invalid_matrix = check_invalid_matrix(input_data.matrix)
    if(invalid_matrix):
        raise(SolutionException(f'Erro: {invalid_matrix}'))

    data = copy.deepcopy(input_data)

    for iteration_line_index in range(1, len(data.matrix)):
        for line_index in range(iteration_line_index, len(data.matrix)):
            m = data.matrix[line_index][iteration_line_index - 1] / data.matrix[iteration_line_index - 1][iteration_line_index - 1]
            data.matrix[line_index][iteration_line_index - 1] = 0

            for column_index in range(iteration_line_index, len(data.matrix[iteration_line_index])):
                data.matrix[line_index][column_index] = data.matrix[line_index][column_index] - (m * data.matrix[iteration_line_index - 1][column_index])
            
            data.results[line_index] = data.results[line_index] - (m * data.results[iteration_line_index - 1])
    
    return data

def gauss_solve(data: MatrixData):
    diagonal_matrix = get_diagonal_matrix(data)
    solution = solve_matrix(diagonal_matrix)

    OUTPUT_FILE.write("Matriz Original\n")
    write_matrix(data, OUTPUT_FILE)
    OUTPUT_FILE.write("\nMatriz Diagonal\n")
    write_matrix(diagonal_matrix, OUTPUT_FILE)
    OUTPUT_FILE.write("\nSolução\n")
    write_dict(solution, OUTPUT_FILE)

INPUT_PATH = 'input.json'
OUTPUT_PATH = 'output.txt'
OUTPUT_FILE = get_out_file(OUTPUT_PATH)

if __name__ == '__main__':
    try:
        data = get_data_from_json(INPUT_PATH)
        solution = gauss_solve(data)
        print(f"Solução encontrada e escrita no arquivo {OUTPUT_PATH}")
    except SolutionException as ex:
        print(ex)
    except KeyError as e:
        print(f"Formato de entrada inválido. Chave faltando: {e}")
    except Exception as e:
        print(f'Erro ao solucionar o problema: {e}')
    
    OUTPUT_FILE.close()
