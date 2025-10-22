from dataclasses import dataclass
from decimal import Decimal, getcontext
import json
import os

from sympy import N, sqrt, symbols, sympify

getcontext().prec = 50

@dataclass
class KeyValuePair:
    key: Decimal
    value: Decimal

    def __init__(self, key: Decimal, value: Decimal):
        self.key = key
        self.value = value

    def __str__(self):
        return f'{self.key}: {self.value}'
    
@dataclass
class Function:
    expression: str
    variable: str

    def __str__(self):
        return f'y = {self.expression}'

@dataclass
class InputData:
    values: list[KeyValuePair]
    target: Decimal
    
    def __init__(self, values: list[KeyValuePair], target: Decimal):
        self.values = values
        self.target = target

    def __str__(self):
        return '\n'.join([str(value) for value in self.values])

class SolutionException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

def get_data_from_json(file_path: str):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    with open(f'{dir_path}/{file_path}', 'r') as json_file:
        json_data = json.load(json_file)
    
    if len(json_data['x']) != len(json_data['y']): raise KeyError("Os tamanhos de x e y não são iguais")

    return InputData(
        [KeyValuePair(Decimal(x), Decimal(y)) for x, y in zip(json_data['x'], json_data['y'])],
        json_data['target']
    )

def solve_function(function: Function, variable_value: Decimal):
    symp_expression = sympify(function.expression)
    symp_variable = symbols(function.variable)

    return Decimal(str(N(symp_expression.evalf(subs={symp_variable: variable_value}))))

def linear_regression(key_value_pairs: list[KeyValuePair]):
    n: int = len(key_value_pairs)
    sum_x: Decimal = Decimal(0)
    sum_y: Decimal = Decimal(0)
    sum_xy: Decimal = Decimal(0)
    sum_x_square: Decimal = Decimal(0)
    sum_y_square: Decimal = Decimal(0)

    for key_value_pair in key_value_pairs:
        sum_x += key_value_pair.key
        sum_y += key_value_pair.value
        sum_xy += key_value_pair.key * key_value_pair.value
        sum_x_square += key_value_pair.key ** 2
        sum_y_square += key_value_pair.value ** 2        

    mean_x: Decimal = Decimal(sum_x / n)
    mean_y: Decimal = Decimal(sum_y / n)

    if ((n * sum_x_square) - (sum_x ** 2)) == 0:
        raise SolutionException("Não é possível realizar divisão por zero")

    a1 = ((n * sum_xy) - (sum_x * sum_y)) / ((n * sum_x_square) - (sum_x ** 2))
    a0 = mean_y - (a1 * mean_x)
    
    solution = Function(f'{a0:.10f} + {a1:.10f} * x', 'x')

    correlation_coefficient = ((n * sum_xy) - sum_x * sum_y) / (sqrt(n * sum_x_square - sum_x ** 2) * sqrt(n * sum_y_square - sum_y ** 2))

    output_file.writelines([f'a0 = {a0}\n', f'a1 = {a1}\n', f'r = {correlation_coefficient}\n', f'{str(solution)}\n'])

    return solution

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

        function = linear_regression(input_data.values)
        result = solve_function(function, input_data.target)
        output_file.writelines([f'f({input_data.target}) = {result}\n'])

        output_file.close()
    except SolutionException as ex:
        print(ex)
    except KeyError as e:
        print(f"Formato de entrada inválido. Chave faltando: {e}")
    except Exception as e:
        print(f'Erro ao solucionar o problema: {e}')