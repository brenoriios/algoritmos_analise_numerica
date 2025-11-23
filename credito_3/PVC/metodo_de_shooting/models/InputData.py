from dataclasses import dataclass
from decimal import Decimal
from models.Function import Function

@dataclass
class InputData:
    edos: list[Function]
    variables: list[str]
    initial_values: list[Decimal]
    guesses: list[Decimal]
    guesses_for: str
    target_value: Decimal
    target_for: str
    control_variable: str
    h: Decimal
    interval: list[Decimal]
    method: str