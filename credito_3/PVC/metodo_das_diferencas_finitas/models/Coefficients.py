from dataclasses import dataclass


@dataclass
class Coefficients:
    prev: str
    diag: str
    next: str
    rhs: str