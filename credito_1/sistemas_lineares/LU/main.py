from dataclasses import dataclass
from enum import Enum
from io import TextIOWrapper
import os
import traceback
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

def print_matrix(data: MatrixData):
    for line_index in range(len(data.matrix)):
        line_parts = ['|']
        for column in data.matrix[line_index]:
            line_parts.append(str(column))

        line_parts.extend(['|', data.variables[line_index], '|', '=', str(data.results[line_index])])

        print(' '.join(line_parts))
        
def write_matrix(data: MatrixData, file: TextIOWrapper):
    for line_index in range(len(data.matrix)):
        line_parts = ['|']
        for column in data.matrix[line_index]:
            line_parts.append('{:.5f}'.format(column))

        line_parts.extend(['|', data.variables[line_index], '|', '=', '{:.5f}'.format(data.results[line_index]), '\n'])

        file.write(' '.join(line_parts))

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
        print(f'{variable} = {solution[0]}')
        print(system[line_index])

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

    matrix = input_data.matrix
    upper_matrix = clear_matrix(copy.deepcopy(input_data))
    lower_matrix = clear_matrix(copy.deepcopy(input_data))

    upper_matrix.matrix[0] = matrix[0]

    for line_index in range(len(lower_matrix.matrix)):
        lower_matrix.matrix[line_index][0] = matrix[line_index][0] / matrix[0][0]

    for line_index in range(len(matrix)):
        for column_index in range(len(matrix[line_index])):
            if line_index == column_index:
                lower_matrix.matrix[line_index][column_index] = 1
            
            if line_index <= column_index:
                upper_matrix.matrix[line_index][column_index] = calc_upper_value(matrix, upper_matrix.matrix, lower_matrix.matrix, line_index, column_index)
            else:
                lower_matrix.matrix[line_index][column_index] = calc_lower_value(matrix, upper_matrix.matrix, lower_matrix.matrix, line_index, column_index)


    # for iteration_line_index in range(1, len(upper_matrix.matrix)):
    #         m = upper_matrix.matrix[line_index][iteration_line_index - 1] / upper_matrix.matrix[iteration_line_index - 1][iteration_line_index - 1]
    #         upper_matrix.matrix[line_index][iteration_line_index - 1] = 0

    #             upper_matrix.matrix[line_index][column_index] = upper_matrix.matrix[line_index][column_index] - (m * upper_matrix.matrix[iteration_line_index - 1][column_index])
            
    #         upper_matrix.results[line_index] = upper_matrix.results[line_index] - (m * upper_matrix.results[iteration_line_index - 1])
    
    print_matrix(upper_matrix)
    print('----------------')
    print_matrix(lower_matrix)
    
    return upper_matrix

def calc_upper_value(matrix: list[list[float]], upper: list[list[float]], lower: list[list[float]], line_index: int, column_index: int):
    sum = 0

    for k in range(1, (line_index - 1)):
        sum += lower[line_index][k] * upper[k][column_index]
    
    return matrix[line_index][column_index] - sum

def calc_lower_value(matrix: list[list[float]], upper: list[list[float]], lower: list[list[float]], line_index: int, column_index: int):
    sum = 0

    for k in range(1, (column_index - 1)):
        sum += lower[line_index][k] * upper[k][column_index]
    
    return (matrix[line_index][column_index] - sum) / upper[column_index][column_index]

def clear_matrix(matrix_data: MatrixData):
    for line_index in range(len(matrix_data.matrix)):
        for column_index in range(len(matrix_data.matrix[line_index])):
            matrix_data.matrix[line_index][column_index] = 0
    
        matrix_data.results[line_index] = 0
    
    return matrix_data

def gauss_solve(data: MatrixData):
    diagonal_matrix = get_diagonal_matrix(data)
    # solution = solve_matrix(diagonal_matrix)

    # OUTPUT_FILE.write("Matriz Original\n")
    # write_matrix(data, OUTPUT_FILE)
    # OUTPUT_FILE.write("\nMatriz Diagonal\n")
    # write_matrix(diagonal_matrix, OUTPUT_FILE)
    # OUTPUT_FILE.write("\nSolução\n")
    # write_dict(solution, OUTPUT_FILE)

INPUT_PATH = 'input.json'
OUTPUT_PATH = 'output.txt'
OUTPUT_FILE = get_out_file(OUTPUT_PATH)

if __name__ == '__main__':
    try:
        data = get_data_from_json(INPUT_PATH)
        solution = gauss_solve(data)
    except SolutionException as ex:
        print(ex)
    except KeyError as e:
        print(f"Formato de entrada inválido. Chave faltando: {e}")
    except Exception as e:
        print(f'Erro ao solucionar o problema: {e}')
        traceback.print_exc()
    
    OUTPUT_FILE.close()
