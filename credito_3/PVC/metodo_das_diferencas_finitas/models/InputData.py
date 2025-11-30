from dataclasses import dataclass
from decimal import Decimal
from models.Function import Function

@dataclass
class InputData:
    edo: str
    solution_variable: str
    initial_value: Decimal
    target_value: Decimal
    interval: list[Decimal]
    nodes: int
    analytical_solution: str