import copy
from dataclasses import dataclass
from decimal import Decimal
import json
import os
import numpy as np
from sympy import Eq, solve, symbols, sympify


class SolutionException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

@dataclass
class InputData:
    x: list[Decimal]
    y: list[Decimal]
    order: int
    
    def __init__(self, x: list[Decimal], y: list[Decimal], order: int):
        self.x = x
        self.y = y
        self.order = order

    def __str__(self):
        return f"x: {get_list_str(self.x)}\ny: {get_list_str(self.y)}\n"

@dataclass
class Matrix:
    matrix: list[list[Decimal]]
    variables: list[str]
    result: list[Decimal]

    def __init__(self, matrix: list[list[Decimal]], variables: list[str], result: list[Decimal]):
        self.matrix = matrix
        self.variables = variables
        self. result = result
    
    def print(self):
        print(str(self))
    
    def __str__(self, only_matrix: bool = False):
        matrix_parts = []
        for line_index in range(len(self.matrix)):
            line_parts = ['|']
            for column in self.matrix[line_index]:
                line_parts.append(self.format_value(column))

            line_parts.append('|')
            
            if not only_matrix:
                line_parts.extend([self.variables[line_index], '|', '=', self.format_value(Decimal(self.result[line_index]))])

            matrix_parts.append(' '.join(line_parts))
        
        return '\n'.join(matrix_parts)
    
    def format_value(self, value: Decimal):
        integer_part_digits_count = len(str(int(value)))

        return f'{value:>{10 if integer_part_digits_count < 10 else integer_part_digits_count}.5f}'

def get_list_str(element_list: list):
    return '[ ' + ' '.join(['{:.5f}'.format(value) for value in element_list]) + ' ]'

def get_data_from_json(file_path: str):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    with open(f'{dir_path}/{file_path}', 'r') as json_file:
        json_data = json.load(json_file)
    
    if len(json_data['x']) != len(json_data['y']): raise KeyError("Os tamanhos de x e y não são iguais")

    return InputData(
        [Decimal(value) for value in json_data['x']],
        [Decimal(value) for value in json_data['y']],
        json_data['order']
    )

def get_vectors(data: InputData):
    n = data.order + 1
    vectors = []

    for i in range(n):
        vector = [Decimal(x ** i) if i != 0 else Decimal(1) for x in data.x]
        vectors.append(vector)
    
    return vectors

def get_matrix(data: InputData, vectors: list[list[Decimal]]):
    n = data.order + 1
    matrix = np.zeros((n, n), dtype=Decimal)
    variables = [f'a{i}' for i in range(n)]
    result = np.zeros((n), dtype=Decimal)

    for i in range(n):
        for j in range(n):
             matrix[j][i] = sum([uj * ui for uj, ui in zip(vectors[j], vectors[i])])

        result[i] = sum([y * u for y, u in zip(data.y, vectors[i])])

    return Matrix(matrix, variables, result)

def solve_function(expression: str, result: float, variable: str):
    symp_expression = sympify(expression)
    symp_variable = symbols(variable)
    
    return solve(Eq(symp_expression, result), symp_variable)

def solve_matrix(data: Matrix):
    system: list[str] = []
    solutions: dict[str, Decimal] = {}
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
            
        solution = solve_function(system[line_index], data.result[line_index], variable)
        solutions[variable] = solution[0]

    solutions = reverse_dict(solutions)
    
    return solutions

def reverse_dict(dictionary: dict):
    reversed_dictionary = {}
    while dictionary:
        key, value = dictionary.popitem()
        reversed_dictionary[key] = value

    return reversed_dictionary

def get_diagonal_matrix(input_data: Matrix):
    data = copy.deepcopy(input_data)

    for iteration_line_index in range(1, len(data.matrix)):
        for line_index in range(iteration_line_index, len(data.matrix)):
            m = data.matrix[line_index][iteration_line_index - 1] / data.matrix[iteration_line_index - 1][iteration_line_index - 1]
            data.matrix[line_index][iteration_line_index - 1] = 0

            for column_index in range(iteration_line_index, len(data.matrix[iteration_line_index])):
                data.matrix[line_index][column_index] = data.matrix[line_index][column_index] - (m * data.matrix[iteration_line_index - 1][column_index])
            
            data.result[line_index] = data.result[line_index] - (m * data.result[iteration_line_index - 1])
    
    return data

def gauss_solve(data: Matrix):
    diagonal_matrix = get_diagonal_matrix(data)
    solution = solve_matrix(diagonal_matrix)

    return solution

def build_expression(solutions: list[Decimal]):
    expression_parts = []
    for i in range(len(solutions)):
        a = solutions[i]
        expression_parts.append(f'({a} * x ** {i})')
    
    return ' + '.join(expression_parts)

def get_output_file(file_path: str):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file = open(f'{dir_path}/{file_path}', 'w')

    return file

INPUT_PATH = 'input.json'
OUTPUT_PATH = 'output.txt'

if __name__ == '__main__':
    try:
        output_file = get_output_file(OUTPUT_PATH)
        input_data = get_data_from_json(INPUT_PATH)

        vectors = get_vectors(input_data)
        matrix = get_matrix(input_data, vectors)
        matrix_solution = gauss_solve(matrix)
        expression = build_expression(list(matrix_solution.values()))

        matrix.print()
        print(expression)
        
        for i in range(len(vectors)):
            output_file.writelines([f'u{i} = ', get_list_str(vectors[i]), '\n'])
        output_file.write('\n')

        output_file.writelines([str(matrix), '\n\n'])
        output_file.writelines([str(matrix_solution), '\n\n'])
        output_file.writelines([expression, '\n\n'])
        output_file.close()
    except SolutionException as ex:
        print(ex)
    except KeyError as e:
        print(f"Formato de entrada inválido. Chave faltando: {e}")
    except Exception as e:
        print(f'Erro ao solucionar o problema: {e}')