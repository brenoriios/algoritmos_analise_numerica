from dataclasses import dataclass
from enum import Enum
import os
import traceback
from sympy import sympify, symbols, N
import json
from decimal import Decimal, getcontext

getcontext().prec = 50

class StopConditionType(Enum):
    ERROR = 1
    INTERVALSIZE = 2

@dataclass
class Function:
    expression: str
    differential: str
    variable: str

@dataclass 
class StopCondition:
    type: StopConditionType
    value: Decimal

@dataclass
class InputData:
    function: Function
    starting_point: Decimal
    stop_condition: StopCondition
    
    def __init__(self, function: Function, starting_point: Decimal, stop_condition: StopCondition):
        self.function = function
        self.starting_point = starting_point
        self.stop_condition = stop_condition

    def __str__(self):
        return f'f({self.function.variable}) = {self.function.expression}; {self.function.variable} = {self.starting_point}'
    
@dataclass
class Solution:
    point: Decimal
    next_point: Decimal
    error: Decimal

class SolutionException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

def get_data_from_json(file_path: str):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    with open(f'{dir_path}/{file_path}', 'r') as json_file:
        data = json.load(json_file)

    stop_condition = StopCondition(StopConditionType.ERROR, Decimal(str(data['stop_condition']['error'])))

    return InputData(
        Function(data['function']['expression'], data['function']['differential'], data['function']['variable']),
        Decimal(data['starting_point']),
        stop_condition
    )

def get_out_file(file_path: str):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file = open(f'{dir_path}/{file_path}', 'w')

    return file

def solve_function(function: Function, variable_value: Decimal):
    symp_expression = sympify(function.expression)
    symp_variable = symbols(function.variable)
    
    return Decimal(str(N(symp_expression.evalf(subs={symp_variable: variable_value}))))

def solve_differential(function: Function, variable_value: Decimal):
    symp_expression = sympify(function.differential)
    symp_variable = symbols(function.variable)
    
    return Decimal(str(N(symp_expression.evalf(subs={symp_variable: variable_value}))))

def solve_for_nr(function: Function, value: Decimal, iteration: int):
    solution_for_function = solve_function(function, value)
    solution_for_differential = solve_differential(function, value)

    if solution_for_differential == 0:
        raise SolutionException("Não é possível dividir por 0")

    next_value = Decimal(value - (solution_for_function / solution_for_differential))

    OUTPUT_FILE.write(f'{iteration};{value:.15f};{solution_for_function:.15f};{solution_for_differential:.15f};{next_value:.15f};{abs(next_value - value):.15f} \n'.replace('.', ','))

    return Solution(value, next_value, Decimal(abs(next_value - value)))

def newton_raphson_solve(function: Function, starting_point: Decimal, stop_condition: StopCondition):
    OUTPUT_FILE.write('#;x;f(x);f\'(x);x[k+1] = x - (f(x) / f\'(x));x[k+1] - x[k] \n')
    
    iteration = 1
    solution: Solution = solve_for_nr(function, starting_point, iteration)
    
    while((abs(solution.error) > stop_condition.value) and iteration <= 9999):
        iteration += 1
        solution = solve_for_nr(function, solution.next_point, iteration)
    
    if iteration > 9999:
        raise SolutionException("Não foi possível encontrar um resultado em 9999 iterações")
    
    return solution.point

INPUT_PATH = 'input.json'
OUTPUT_PATH = 'output.csv'
OUTPUT_FILE = get_out_file(OUTPUT_PATH)

if __name__ == '__main__':
    
    try:
        data = get_data_from_json(INPUT_PATH)
        solution = newton_raphson_solve(data.function, data.starting_point, data.stop_condition)
        print(f"Solução encontrada e escrita no arquivo {OUTPUT_PATH}")
    except SolutionException as ex:
        print(ex)
    except KeyError as e:
        print(f"Formato de entrada inválido. Chave faltando: {e}")
    except Exception as e:
        print(f'Erro ao solucionar o problema: {e}')
    
    OUTPUT_FILE.close()
