from bizdays import Calendar
from . import feriados_br
from datetime import datetime, date
import pandas as pd

bcb = Calendar(feriados_br.bacen, ['Saturday', 'Sunday'])
b3 = Calendar(feriados_br.b3, ['Saturday', 'Sunday'])


def calcular_du(dt_inicio: datetime | date | list[date | datetime] | pd.DatetimeIndex,
                dt_fim: datetime | date | list[date | datetime] | pd.DatetimeIndex,
                calendario: Calendar = bcb) -> int:
    return calendario.bizdays(dt_inicio, dt_fim)


def eh_dia_util(data: datetime, calendario: Calendar) -> bool:
    return calendario.isbizday(data)


def obter_ultimo_dia_util(data: datetime, calendario: Calendar, delta_du_offset=1):
    """Obtem o último dia útil dada uma data inicial (inclusive) e um calendario"""
    data = calendario.offset(data, -delta_du_offset)
    while not eh_dia_util(data, calendario=calendario):
        data = calendario.offset(data, -1)
    return data


def obter_proximo_dia_util(data: datetime | date, calendario: Calendar = bcb, delta_du_offset=1):
    """Obtem o próximo dia útil dada uma data inicial (inclusive) e um calendario"""
    data = calendario.offset(data, delta_du_offset)
    while not eh_dia_util(data, calendario=calendario):
        data = calendario.offset(data, 1)
    return data
