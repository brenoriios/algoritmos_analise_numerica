from dataclasses import dataclass
from decimal import Decimal

@dataclass
class Point:
    x: Decimal
    y: Decimal