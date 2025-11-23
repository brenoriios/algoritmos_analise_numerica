from dataclasses import dataclass
from enum import Enum
from solvers.Euler import Euler
from solvers.EulerModificado import EulerModificado
from solvers.Heun import Heun
from solvers.RungeKutta2 import RungeKutta2
from solvers.RungeKutta3 import RungeKutta3
from solvers.RungeKutta4 import RungeKutta4
from solvers.RungeKutta6 import RungeKutta6
from solvers.SerieTaylor import SerieTaylor


@dataclass
class MethodEnum(Enum):
    euler = Euler
    euler_modificado = EulerModificado
    heun = Heun
    runge_kutta_2 = RungeKutta2
    runge_kutta_3 = RungeKutta3
    runge_kutta_4 = RungeKutta4
    runge_kutta_6 = RungeKutta6
    serie_taylor = SerieTaylor