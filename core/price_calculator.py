# core/price_calculator.py (NOVO ARQUIVO)
from abc import ABC, abstractmethod
from datetime import timedelta, date
from decimal import Decimal
from .models import FERIADOS


class PriceCalculator(ABC):
    """Interface para calculadores de preço."""
    
    @abstractmethod
    def calcular(self, dias: int, preco_base_dia: Decimal, data_inicio: date, data_fim: date) -> Decimal:
        pass


class PriceCalculatorBase(PriceCalculator):
    """Calculador base: apenas dias × preço base."""
    
    def calcular(self, dias: int, preco_base_dia: Decimal, data_inicio: date, data_fim: date) -> Decimal:
        return Decimal(dias) * preco_base_dia


class PriceCalculatorDecorator(PriceCalculator):
    """Decorator base para decoradores de preço."""
    
    def __init__(self, calculator: PriceCalculator):
        self._calculator = calculator
    
    def calcular(self, dias: int, preco_base_dia: Decimal, data_inicio: date, data_fim: date) -> Decimal:
        return self._calculator.calcular(dias, preco_base_dia, data_inicio, data_fim)


class FeriadoDecorator(PriceCalculatorDecorator):
    """Adiciona +20% se houver feriado no período."""
    
    ACRESCIMO = Decimal('1.20')
    
    def calcular(self, dias: int, preco_base_dia: Decimal, data_inicio: date, data_fim: date) -> Decimal:
        preco = super().calcular(dias, preco_base_dia, data_inicio, data_fim)
        
        # Verifica feriado
        data_atual = data_inicio
        while data_atual <= data_fim:
            if data_atual in FERIADOS:
                return preco * self.ACRESCIMO
            data_atual += timedelta(days=1)
        
        return preco


class FimDeSemanDecorator(PriceCalculatorDecorator):
    """Adiciona +15% se houver fim de semana no período."""
    
    ACRESCIMO = Decimal('1.15')
    
    def calcular(self, dias: int, preco_base_dia: Decimal, data_inicio: date, data_fim: date) -> Decimal:
        preco = super().calcular(dias, preco_base_dia, data_inicio, data_fim)
        
        # Verifica fim de semana (6=sábado, 5=sexta)
        data_atual = data_inicio
        while data_atual <= data_fim:
            if data_atual.weekday() in [5, 6]:  # sábado, domingo
                return preco * self.ACRESCIMO
            data_atual += timedelta(days=1)
        
        return preco


class TemporadaAltaDecorator(PriceCalculatorDecorator):
    """Adiciona +25% para períodos de alta demanda."""
    
    ACRESCIMO = Decimal('1.25')
    MESES_ALTA = [7, 12]  # julho, dezembro
    
    def calcular(self, dias: int, preco_base_dia: Decimal, data_inicio: date, data_fim: date) -> Decimal:
        preco = super().calcular(dias, preco_base_dia, data_inicio, data_fim)
        
        # Verifica se período está em temporada alta
        if data_inicio.month in self.MESES_ALTA or data_fim.month in self.MESES_ALTA:
            return preco * self.ACRESCIMO
        
        return preco


