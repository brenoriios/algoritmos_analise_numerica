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
    variable: str

@dataclass 
class Interval:
    start: Decimal
    end: Decimal

@dataclass 
class StopCondition:
    type: StopConditionType
    value: Decimal

@dataclass
class InputData:
    function: Function
    interval: Interval
    stop_condition: StopCondition
    
    def __init__(self, function: Function, interval: Interval, stop_condition: StopCondition):
        self.function = function
        self.interval = interval
        self.stop_condition = stop_condition

    def __str__(self):
        return f'f({self.function.variable}) = {self.function.expression}; [{self.interval.start}, {self.interval.end}]'
    
@dataclass
class Solution:
    next_interval: Interval
    point: Decimal
    error: Decimal

class SolutionException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

def get_data_from_json(file_path: str):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    
    with open(f'{dir_path}/{file_path}', 'r') as json_file:
        data = json.load(json_file)

    if('error' in data['stop_condition']):
        stop_condition = StopCondition(StopConditionType.ERROR, Decimal(str(data['stop_condition']['error'])))
    elif('interval_size' in data['stop_condition']):
        stop_condition = StopCondition(StopConditionType.INTERVALSIZE, Decimal(str(data['stop_condition']['interval_size'])))
    else:
        raise(KeyError('Forneça uma condição de parada no arquivo de entrada. Valores aceitos: "error" ou "interval_size"'))

    return InputData(
        Function(data['function']['expression'], data['function']['variable']), 
        Interval(Decimal(str(data['interval']['start'])), Decimal(str(data['interval']['end']))),
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

def solve_for_pf(function: Function, interval: Interval, stop_condition: StopCondition, iteration: int):
    if (interval.end - interval.start) < 0:
        raise SolutionException('Intervalo Inválido')

    solution_interval_end = solve_function(function, interval.end)
    solution_interval_start = solve_function(function, interval.start)
    
    interval_section = ((interval.start * solution_interval_end) - (interval.end * solution_interval_start)) / (solution_interval_end - solution_interval_start)
    
    solution_interval_section = solve_function(function, interval_section)

    signal_change_for_start = (solution_interval_start * solution_interval_section) < 0
    signal_change_for_end = (solution_interval_end * solution_interval_section) < 0

    if not signal_change_for_start and not signal_change_for_end:
        raise SolutionException('Não houve mudança de sinais, não é possível encontrar uma solução!')
    
    if signal_change_for_start: new_interval = Interval(interval.start, interval_section)
    if signal_change_for_end: new_interval = Interval(interval_section, interval.end)

    OUTPUT_FILE.write(f'{iteration};{interval.start:.9f};{interval.end:.9f};{solution_interval_start:.9f};{solution_interval_end:.9f};{interval_section:.9f};{solution_interval_section:.9f} \n'.replace('.', ','))

    if(stop_condition.type == StopConditionType.ERROR):
        condition_value = abs(solution_interval_section)
    elif(stop_condition.type == StopConditionType.INTERVALSIZE):
        condition_value = new_interval.end - new_interval.start

    return Solution(new_interval, interval_section, condition_value)

def false_position_solve(function: Function, interval: Interval, stop_condition: StopCondition):
    OUTPUT_FILE.write('#;a;b;f(a);f(b);c;f(c)\n')
    if((interval.end - interval.start) == 0):
        return solve_function(function, interval.end)
    
    iteration = 1
    solution: Solution = solve_for_pf(function, interval, stop_condition, iteration)
    
    while((abs(solution.error) > stop_condition.value) and iteration <= 9999):
        iteration += 1
        solution = solve_for_pf(function, solution.next_interval, stop_condition, iteration)
    
    return solution.point

INPUT_PATH = 'input.json'
OUTPUT_PATH = 'output.csv'
OUTPUT_FILE = get_out_file(OUTPUT_PATH)

if __name__ == '__main__':
    
    try:
        data = get_data_from_json(INPUT_PATH)
        solution = false_position_solve(data.function, data.interval, data.stop_condition)
        print(f"Solução: {round(solution, 9)}")
    except SolutionException as ex:
        print(ex)
    except KeyError as e:
        print(f"Formato de entrada inválido. Chave faltando: {e}")
    except Exception:
        print('Erro ao solucionar o problema.')
    
    OUTPUT_FILE.close()
