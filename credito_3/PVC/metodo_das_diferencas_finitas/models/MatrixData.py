from dataclasses import dataclass


@dataclass
class MatrixData:
    matrix: list[list[float]]
    variables: list[str]
    results: list[float]