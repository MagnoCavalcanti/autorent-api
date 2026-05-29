# core/factories.py (NOVO ARQUIVO)
from abc import ABC, abstractmethod
from .models import Aluguel, Cliente
from decimal import Decimal

class AluguelFactory(ABC):
    """Factory abstrata para criar aluguéis com políticas específicas."""
    
    @abstractmethod
    def criar(self, cliente_data, carro, data_aluguel, data_devolucao_prevista, empresa, vendedor):
        """Cria um aluguel respeitando as políticas da empresa."""
        pass


class AluguelFactoryPadrao(AluguelFactory):
    """Factory padrão: usa o preço base do carro."""
    
    def criar(self, cliente_data, carro, data_aluguel, data_devolucao_prevista, empresa, vendedor):
        # Get-or-create cliente
        cliente, _ = Cliente.objects.get_or_create(
            cpf=cliente_data['cpf'],
            defaults=cliente_data
        )
        
        # Calcula dias
        dias = (data_devolucao_prevista - data_aluguel).days
        dias = max(dias, 1)  # garante pelo menos 1 dia
        
        # Calcula valor
        valor_total = Decimal(dias) * carro.preco_base_dia
        
        # Cria aluguel
        aluguel = Aluguel.objects.create(
            cliente=cliente,
            carro=carro,
            vendedor=vendedor,
            empresa=empresa,
            data_aluguel=data_aluguel,
            data_devolucao_prevista=data_devolucao_prevista,
            valor_total=valor_total,
            status_aluguel='criado'
        )
        
        # Atualiza status do carro
        carro.status = 'disponivel'
        carro.save(update_fields=['status'])
        
        return aluguel


class AluguelFactoryPremium(AluguelFactory):
    """Factory com políticas especiais: desconto para aluguéis longos."""
    
    def criar(self, cliente_data, carro, data_aluguel, data_devolucao_prevista, empresa, vendedor):
        cliente, _ = Cliente.objects.get_or_create(
            cpf=cliente_data['cpf'],
            defaults=cliente_data
        )
        
        dias = (data_devolucao_prevista - data_aluguel).days
        dias = max(dias, 1)
        
        valor_total = Decimal(dias) * carro.preco_base_dia
        
        # Política exclusiva: desconto 10% para 7+ dias
        if dias >= 7:
            valor_total *= Decimal('0.90')
        
        aluguel = Aluguel.objects.create(
            cliente=cliente,
            carro=carro,
            vendedor=vendedor,
            empresa=empresa,
            data_aluguel=data_aluguel,
            data_devolucao_prevista=data_devolucao_prevista,
            valor_total=valor_total,
            status_aluguel='criado'
        )
        
        carro.status = 'disponivel'  # Começa disponível, vai para 'alugado' ao ativar
        carro.save(update_fields=['status'])
        
        return aluguel


class AluguelFactoryComercial(AluguelFactory):
    """Factory comercial: desconto escalonado por volume de dias."""
    
    def criar(self, cliente_data, carro, data_aluguel, data_devolucao_prevista, empresa, vendedor):
        cliente, _ = Cliente.objects.get_or_create(
            cpf=cliente_data['cpf'],
            defaults=cliente_data
        )
        
        dias = (data_devolucao_prevista - data_aluguel).days
        dias = max(dias, 1)
        
        valor_total = Decimal(dias) * carro.preco_base_dia
        
        # Política comercial: desconto progressivo
        if dias >= 30:
            valor_total *= Decimal('0.80')  # 20% desconto
        elif dias >= 14:
            valor_total *= Decimal('0.85')  # 15% desconto
        elif dias >= 7:
            valor_total *= Decimal('0.90')  # 10% desconto
        
        aluguel = Aluguel.objects.create(
            cliente=cliente,
            carro=carro,
            vendedor=vendedor,
            empresa=empresa,
            data_aluguel=data_aluguel,
            data_devolucao_prevista=data_devolucao_prevista,
            valor_total=valor_total,
            status_aluguel='criado'
        )
        
        carro.status = 'disponivel'
        carro.save(update_fields=['status'])
        
        return aluguel