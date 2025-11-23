from dataclasses import dataclass
from decimal import Decimal
from models.Function import Function

@dataclass
class InputData:
    edos: list[Function]
    variables: list[str]
    initial_values: list[Decimal]
    control_variable: str
    h: Decimal
    interval: list[Decimal]
    analytical_solution: str | None
    method: str