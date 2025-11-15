from dataclasses import dataclass
from decimal import Decimal
import json
import os
import sys

from matplotlib import pyplot as plt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from metodo_de_euler import main as Euler
from metodo_de_euler_modificado import main as EulerModificado
from metodo_de_heun import main as Heun

@dataclass
class Function:
    expression: str
    variables: list[str]
    
@dataclass
class Point:
    x: Decimal
    y: Decimal

    def __init__(self, x: Decimal, y: Decimal):
        self.x = x
        self.y = y

    def __str__(self):
        return f"({self.x:.9f}, {self.y:.9f})"

@dataclass
class InputData:
    diff: Function
    first_point: Point
    h: Decimal
    interval: list[Decimal]

    def __init__(self, diff: Function, first_point: Point, h: Decimal, interval: list[Decimal]):
        self.diff = diff
        self.first_point = first_point
        self.h = h
        self.interval = interval

def get_data_from_json(file_path: str):
    dir_path = os.path.dirname(os.path.realpath(__file__))

    with open(f"{dir_path}/{file_path}", "r") as json_file:
        json_data = json.load(json_file)

    if "differential" not in json_data:
        raise KeyError("É necessário informar derivada")
    if "firstPoint" not in json_data:
        raise KeyError("É necessário informar o ponto inicial")
    if "h" not in json_data:
        raise KeyError("É necessário informar o valor de h")
    if "interval" not in json_data:
        raise KeyError("É necessário informar o intervalo")
    
    if "expression" not in json_data["differential"]:
        raise KeyError("É necessário informar a expressão da derivada")
    if "variables" not in json_data["differential"]:
        raise KeyError("É necessário informar a variável da expressão da derivada")
    if len(json_data["differential"]["variables"]) > 2:
        raise KeyError("É necessário informar no máximo 2 variáveis")
    if len(json_data["interval"]) != 2:
        raise KeyError("É necessário informar o inicio e fim do intervalo")
    if json_data["interval"][1] < json_data["interval"][0]:
        raise KeyError("O início do intervalo deve ser anterior ao fim")

    return InputData(
        Function(json_data["differential"]["expression"], json_data["differential"]["variables"]),
        Point(json_data["firstPoint"]["x"], json_data["firstPoint"]["y"]),
        Decimal(json_data["h"]),
        json_data["interval"]
    )

def plot_points(solutionsEuler: list[Point], solutionsHeun: list[Point], solutionsEulerModificado: list[Point]):
    plt.plot(
        [p.x for p in solutionsEuler],
        [p.y for p in solutionsEuler],
        color="blue",
        linestyle="-",
        marker="o",
        label="Método de Euler"
    )
   
    plt.plot(
        [p.x for p in solutionsHeun],
        [p.y for p in solutionsHeun],
        color="red",
        linestyle="-",
        marker="o",
        label="Método de Heun"
    )

    plt.plot(
        [p.x for p in solutionsEulerModificado],
        [p.y for p in solutionsEulerModificado],
        color="green",
        linestyle="-",
        marker="o",
        label="Método de Euler Modificado"
    )

    plt.xlabel("x")
    plt.ylabel("y")
    plt.grid(True)
    plt.legend()

    plt.savefig(f"{os.path.dirname(os.path.realpath(__file__))}/output")
    plt.show()

INPUT_PATH = "input.json"
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    try:
        input_data = get_data_from_json(INPUT_PATH)
        solutionsEuler = Euler.solve(input_data)
        solutionsEulerModificado = EulerModificado.solve(input_data)
        solutionsHeun = Heun.solve(input_data)
        plot_points(solutionsEuler, solutionsEulerModificado, solutionsHeun)
    except KeyError as e:
        print(f"Formato de entrada inválido. {e}")
    except Exception as e:
        print(f"Erro ao solucionar o problema: {e}")