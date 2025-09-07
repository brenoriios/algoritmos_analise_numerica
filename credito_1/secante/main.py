from dataclasses import dataclass
from enum import Enum
import os
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
    x0: Decimal
    x1: Decimal
    stop_condition: StopCondition
    
    def __init__(self, function: Function, x0: Decimal, x1: Decimal, stop_condition: StopCondition):
        self.function = function
        self.x0 = x0
        self.x1 = x1
        self.stop_condition = stop_condition

    def __str__(self):
        return f'f({self.function.variable}) = {self.function.expression}; {self.function.variable} = {self.x0}'
    
@dataclass
class Solution:
    value: Decimal
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
        Decimal(data['x0']),
        Decimal(data['x1']),
        stop_condition
    )

def get_out_file(file_path: str):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file = open(f'{dir_path}/{file_path}', 'w')

    return file

def solve_function(function: Function, variable_value: Decimal):
    symp_expression = sympify(function.expression)
    symp_variable = symbols(function.variable)
    
    return N(symp_expression.evalf(subs={symp_variable: variable_value}))

def solve_differential(function: Function, variable_value: Decimal):
    symp_expression = sympify(function.differential)
    symp_variable = symbols(function.variable)
    
    return N(symp_expression.evalf(subs={symp_variable: variable_value}))

def solve_for_nr(function: Function, point: Decimal, previous_solution_for_function: Decimal, previous_point: Decimal, iteration: int):
    solution_for_function = solve_function(function, point)

    next_point = ((solution_for_function * previous_point) - (previous_solution_for_function * point)) / (solution_for_function - previous_solution_for_function)

    OUTPUT_FILE.write(f'{iteration};{point:.50f};{solution_for_function:.50f};{previous_solution_for_function:.50f};{next_point:.50f} \n'.replace('.', ','))

    return Solution(solution_for_function, next_point, abs(next_point - point))

def newton_raphson_solve(function: Function, x0: Decimal, x1: Decimal, stop_condition: StopCondition):
    OUTPUT_FILE.write('#;x[k];f(x[k]);f(x[k-1]);x[k+1] \n')
    
    previous_point = x0
    previous_solution: Solution = solve_function(function, previous_point)
    point = x1
    OUTPUT_FILE.write(f'1;{previous_point:.50f};{previous_solution:.50f}; - ;{point:.50f} \n'.replace('.', ','))

    iteration = 2
    solution: Solution = solve_for_nr(function, point, previous_solution, previous_point, iteration)
    
    while((abs(solution.error) > stop_condition.value) and iteration <= 9999):
        iteration += 1
        previous_point = point
        previous_solution = solution.value
        point = solution.next_point
        solution = solve_for_nr(function, point, previous_solution, previous_point, iteration)
    
    return previous_point

INPUT_PATH = 'input.json'
OUTPUT_PATH = 'output.csv'
OUTPUT_FILE = get_out_file(OUTPUT_PATH)

if __name__ == '__main__':
    
    try:
        data = get_data_from_json(INPUT_PATH)
        solution = newton_raphson_solve(data.function, data.x0, data.x1, data.stop_condition)
        print(f"Solução: {round(solution, getcontext().prec)}")
    except SolutionException as ex:
        print(ex)
    except KeyError as e:
        print(f"Formato de entrada inválido. Chave faltando: {e}")
    except Exception as e:
        print(f'Erro ao solucionar o problema: {e}')
    
    OUTPUT_FILE.close()
