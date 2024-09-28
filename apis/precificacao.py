from dataclasses import dataclass, field
from calendario.calendario import *


# Todo
@dataclass()
class TituloCDI:
    pu_compra: float
    quantidade: float
    vna: float
    dt_compra: datetime
    dt_vencimento: datetime

    def taxa_adquirida(self):
        return (self.vna/self.pu_compra) ** (252/calcular_du(dt_inicio=self.dt_compra, dt_fim=self.dt_vencimento))

    def marcar_curva(self, data: datetime):
        """Considera que o CDI não mudou"""
        return self.pu_compra * (1+self.taxa_adquirida()) ** (calcular_du(dt_inicio=self.dt_compra, dt_fim=data)/252)

    def marcar_mercado(self, data: datetime):
        return self.pu_compra * (1 + self.taxa_adquirida()) ** (calcular_du(dt_inicio=self.dt_compra, dt_fim=data)/252)
