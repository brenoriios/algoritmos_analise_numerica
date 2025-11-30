from sympy import Eq, solve, sympify, symbols
from decimal import getcontext
from models.MatrixData import MatrixData
import copy

getcontext().prec = 50

class GaussElimination:
    def solve_function(self, expression: str, result: float, variable: str):
        symp_expression = sympify(expression)
        symp_variable = symbols(variable)
        
        return solve(Eq(symp_expression, result), symp_variable)

    def solve_matrix(self, data: MatrixData):
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
                
            solution = self.solve_function(system[line_index], data.results[line_index], variable)
            solutions[variable] = solution[0]

        solutions = self.reverse_dict(solutions)
        
        return solutions

    def reverse_dict(self, dictionary: dict):
        reversed_dictionary = {}
        while dictionary:
            key, value = dictionary.popitem()
            reversed_dictionary[key] = value

        return reversed_dictionary

    def get_diagonal_matrix(self, input_data: MatrixData):
        data = copy.deepcopy(input_data)

        for iteration_line_index in range(1, len(data.matrix)):
            for line_index in range(iteration_line_index, len(data.matrix)):
                m = data.matrix[line_index][iteration_line_index - 1] / data.matrix[iteration_line_index - 1][iteration_line_index - 1]
                data.matrix[line_index][iteration_line_index - 1] = 0

                for column_index in range(iteration_line_index, len(data.matrix[iteration_line_index])):
                    data.matrix[line_index][column_index] = data.matrix[line_index][column_index] - (m * data.matrix[iteration_line_index - 1][column_index])
                
                data.results[line_index] = data.results[line_index] - (m * data.results[iteration_line_index - 1])
        
        return data

    def solve(self, data: MatrixData):
        diagonal_matrix = self.get_diagonal_matrix(data)
        solution = self.solve_matrix(diagonal_matrix)

        return solution
