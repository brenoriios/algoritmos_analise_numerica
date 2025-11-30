from dataclasses import dataclass
from decimal import Decimal
from models.MatrixData import MatrixData


@dataclass
class Solution:
    system: MatrixData
    solution: dict[str, Decimal]