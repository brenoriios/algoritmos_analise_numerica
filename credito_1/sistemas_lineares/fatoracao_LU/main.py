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
    matrix: list[list[Decimal]]
    variables: list[str]
    results: list[Decimal]

@dataclass 
class LUSolution:
    lower: MatrixData
    upper: MatrixData

class SolutionException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

def get_data_from_json(file_path: str):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    with open(f'{dir_path}/{file_path}', 'r') as json_file:
        data = json.load(json_file)

    decimal_matrix = [[Decimal(str(val)) for val in row] for row in data['matrix']]
    decimal_results = [Decimal(str(val)) for val in data['results']]

    return MatrixData(
        decimal_matrix,
        data['variables'],
        decimal_results
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

def solve_function(expression: str, result: Decimal, variable: str):
    symp_expression = sympify(N(expression, 50))
    symp_variable = symbols(variable)
    
    solutions_sympy = solve(Eq(symp_expression, result), symp_variable)
    decimal_solutions = [Decimal(str(sol)) for sol in solutions_sympy]
    
    return decimal_solutions

def solve_matrix(data: MatrixData, lower: bool = False):
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
    
    for line_index in (range(len(data.matrix) - 1, -1, -1) if not lower else range(len(data.matrix))):
        current_expression = system[line_index]
        variable = data.variables[line_index]

        for key, value in solutions.items():
            current_expression = current_expression.replace(key, str(value))
            
        solution = solve_function(current_expression, data.results[line_index], variable)
        solutions[variable] = solution[0]

        print(f'{variable} = {solution[0]}')
        print(current_expression)
    
    return reverse_dict(solutions) if not lower else solutions

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

def get_LU_matrices(data: MatrixData):
    invalid_matrix = check_invalid_matrix(data.matrix)
    if(invalid_matrix):
        raise(SolutionException(f'Erro: {invalid_matrix}'))

    matrix = data.matrix
    upper_matrix = clear_matrix(copy.deepcopy(data))
    lower_matrix = clear_matrix(copy.deepcopy(data))

    upper_matrix.matrix[0] = matrix[0]

    for line_index in range(len(lower_matrix.matrix)):
        lower_matrix.matrix[line_index][line_index] = Decimal(1)
        lower_matrix.matrix[line_index][0] = matrix[line_index][0] / matrix[0][0]

    for line_index in range(len(matrix)):
        for column_index in range(len(matrix[line_index])):            
            if line_index <= column_index:
                upper_matrix.matrix[line_index][column_index] = calc_upper_value(matrix, upper_matrix.matrix, lower_matrix.matrix, line_index, column_index)
            else:
                lower_matrix.matrix[line_index][column_index] = calc_lower_value(matrix, upper_matrix.matrix, lower_matrix.matrix, line_index, column_index)

    return LUSolution(lower_matrix, upper_matrix)

def calc_upper_value(matrix: list[list[Decimal]], upper: list[list[Decimal]], lower: list[list[Decimal]], line_index: int, column_index: int):
    sum = Decimal(0)

    for k in range(line_index):
        sum += lower[line_index][k] * upper[k][column_index]
    
    return matrix[line_index][column_index] - sum

def calc_lower_value(matrix: list[list[Decimal]], upper: list[list[Decimal]], lower: list[list[Decimal]], line_index: int, column_index: int):
    sum = Decimal(0)

    for k in range(column_index):
        sum += lower[line_index][k] * upper[k][column_index]
    
    if upper[column_index][column_index] == 0:
        raise SolutionException("Divisão por zero, a decomposição LU não é possível para esta matriz.")
    
    return (matrix[line_index][column_index] - sum) / upper[column_index][column_index]

def clear_matrix(matrix_data: MatrixData):
    for line_index in range(len(matrix_data.matrix)):
        for column_index in range(len(matrix_data.matrix[line_index])):
            matrix_data.matrix[line_index][column_index] = Decimal(0)
    
        matrix_data.results[line_index] = Decimal(0)
    
    return matrix_data

def LU_solve(data: MatrixData):
    matrices = get_LU_matrices(data)

    matrices.lower.results = data.results

    OUTPUT_FILE.write('Matriz Original:\n')
    write_matrix(data, OUTPUT_FILE)
    
    OUTPUT_FILE.write('\nMatriz Inferior:\n')
    write_matrix(matrices.lower, OUTPUT_FILE, only_matrix=True)
    
    OUTPUT_FILE.write('\nMatriz Superior:\n')
    write_matrix(matrices.upper, OUTPUT_FILE, only_matrix=True)

    OUTPUT_FILE.write('\n----------------------------------------------------------------------------------------\n')
    
    OUTPUT_FILE.write(f'\nSolucionando para o conjunto: {[str(value) for value in data.results]}\n')

    lower_solution = solve_matrix(matrices.lower, lower=True)
    OUTPUT_FILE.write(f'\nMatriz Inferior:\n')
    write_matrix(matrices.lower, OUTPUT_FILE)
    OUTPUT_FILE.write('\nSolução:\n')
    write_dict(lower_solution, OUTPUT_FILE)

    matrices.upper.results = list(lower_solution.values())
    upper_solution = solve_matrix(matrices.upper)
    OUTPUT_FILE.write(f'\nMatriz Superior:\n')
    write_matrix(matrices.upper, OUTPUT_FILE)
    OUTPUT_FILE.write('\nSolução:\n')
    write_dict(upper_solution, OUTPUT_FILE)

INPUT_PATH = 'input.json'
OUTPUT_PATH = 'output.txt'
OUTPUT_FILE = get_out_file(OUTPUT_PATH)

if __name__ == '__main__':
    try:
        data = get_data_from_json(INPUT_PATH)
        solution = LU_solve(data)
    except SolutionException as ex:
        print(ex)
    except KeyError as e:
        print(f"Formato de entrada inválido. Chave faltando: {e}")
    except Exception as e:
        print(f'Erro ao solucionar o problema: {e}')
        traceback.print_exc()
    
    OUTPUT_FILE.close()
