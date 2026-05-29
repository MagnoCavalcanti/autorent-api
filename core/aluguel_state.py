# core/aluguel_state.py (NOVO ARQUIVO)
from abc import ABC, abstractmethod
from django.utils import timezone
from datetime import date
from decimal import Decimal


class AluguelState(ABC):
    """Interface para estados de um aluguel."""
    
    @abstractmethod
    def devolver(self, aluguel):
        """Processa a devolução do aluguel."""
        pass
    
    @abstractmethod
    def pode_editar(self) -> bool:
        """Verifica se aluguel pode ser editado."""
        pass
    
    @abstractmethod
    def nome(self) -> str:
        """Retorna o nome do estado."""
        pass


class AluguelCriado(AluguelState):
    """Estado inicial: aluguel foi criado mas ainda não ativado."""
    
    def devolver(self, aluguel):
        raise Exception("Não é possível devolver um aluguel que ainda não foi ativado.")
    
    def pode_editar(self) -> bool:
        return True
    
    def nome(self) -> str:
        return "criado"


class AluguelAtivo(AluguelState):
    """Estado ativo: carro está alugado, em uso."""
    
    def devolver(self, aluguel):
        """Processa a devolução e transiciona para Devolvido ou ComAtraso."""
        hoje = date.today()
        aluguel.data_devolucao_real = hoje
        
        # Calcula atraso
        atraso_dias = (hoje - aluguel.data_devolucao_prevista).days
        
        if atraso_dias > 0:
            # Transitiona para ComAtraso e calcula multa
            aluguel._estado = AluguelComAtraso()
            aluguel.multa = aluguel._calcular_multa(atraso_dias)
        else:
            # Transitiona para Devolvido
            aluguel._estado = AluguelDevolvido()
            aluguel.multa = Decimal('0.00')
        
        # Atualiza carro
        aluguel.carro.status = 'disponivel'
        aluguel.carro.save(update_fields=['status'])
        
        return aluguel
    
    def pode_editar(self) -> bool:
        return False
    
    def nome(self) -> str:
        return "ativo"


class AluguelDevolvido(AluguelState):
    """Estado final: aluguel devolvido sem atraso."""
    
    def devolver(self, aluguel):
        raise Exception("Aluguel já foi devolvido.")
    
    def pode_editar(self) -> bool:
        return False
    
    def nome(self) -> str:
        return "devolvido"


class AluguelComAtraso(AluguelState):
    """Estado final: aluguel devolvido com atraso e multa gerada."""
    
    def devolver(self, aluguel):
        raise Exception("Aluguel já foi devolvido com atraso.")
    
    def pode_editar(self) -> bool:
        return False
    
    def nome(self) -> str:
        return "com_atraso"


class AluguelCancelado(AluguelState):
    """Estado: aluguel foi cancelado antes de ser ativado."""
    
    def devolver(self, aluguel):
        raise Exception("Aluguel cancelado não pode ser devolvido.")
    
    def pode_editar(self) -> bool:
        return False
    

    def nome(self) -> str:
        return "cancelado"