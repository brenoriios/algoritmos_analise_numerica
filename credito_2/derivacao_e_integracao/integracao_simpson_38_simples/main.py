from dataclasses import dataclass
from decimal import Decimal, getcontext
import traceback
import json
import os


getcontext().prec = 50


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
    points: list[Decimal]

    def __init__(self, points: list[Point]):
        self.points = points

class SolutionException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

def get_data_from_json(file_path: str):
    dir_path = os.path.dirname(os.path.realpath(__file__))

    with open(f"{dir_path}/{file_path}", "r") as json_file:
        json_data = json.load(json_file)

    if "points" not in json_data:
        raise KeyError("É necessário informar os pontos considerados")

    if len(json_data["points"]["x"]) != 4:
        raise SolutionException("Para a regra de Simpson de 3/8 simples é necessário informar apenas 4 pontos")
    
    return InputData(
        [Point(Decimal(x), Decimal(y)) for x, y in zip(json_data["points"]["x"], json_data["points"]["y"])]
    )


def calc_integral_by_simpson_38(points: list[Point]):
    width = points[-1].x - points[0].x

    mean_height = (points[0].y + (3 * points[1].y) + (3 * points[2].y) + points[-1].y) / 8
    
    integral = width * mean_height

    return integral

def calc_integral(input_data: InputData):
    integral = calc_integral_by_simpson_38(input_data.points)
    
    print(integral)
    
    return integral


def print_list(items: list):
    print(f"[ {', '.join([str(item) for item in items])} ]")


def get_output_file(file_path: str):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file = open(f"{dir_path}/{file_path}", "w")

    return file


INPUT_PATH = "input.json"
OUTPUT_PATH = "output.txt"

if __name__ == "__main__":
    try:
        output_file = get_output_file(OUTPUT_PATH)
        input_data = get_data_from_json(INPUT_PATH)
        solution = calc_integral(input_data)

        output_file.close()
    except SolutionException as ex:
        print(ex)
    except KeyError as e:
        print(f"Formato de entrada inválido. {e}")
    except Exception as e:
        print(f"Erro ao solucionar o problema: {e}")
        traceback.print_exc()
