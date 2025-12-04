from django.db import models
from django.core.validators import RegexValidator
from datetime import timedelta, date
from decimal import Decimal

# ------------------------
# LISTA DE FERIADOS
# ------------------------
FERIADOS = [
    date(2025, 1, 1),   # Ano Novo
    date(2025, 4, 21),  # Tiradentes
    date(2025, 5, 1),   # Dia do Trabalho
    date(2025, 9, 7),   # Independência
    date(2025, 10, 12), # Nossa Senhora Aparecida
    date(2025, 11, 2),  # Finados
    date(2025, 11, 15), # Proclamação da República
    date(2025, 12, 25), # Natal
]

plate_validators = [
    RegexValidator(
        regex=r'^(?:[A-Z]{3}\-\d{4}|[A-Z]{3}\d[A-Z]\d{2})$',
        message='Placa deve ser nesse formato: XXX-0000 ou ABC1D23'
        )
]

cpf_validators = [
    RegexValidator(
        regex=r'^\d{3}\.\d{3}\.\d{3}\-\d{2}$',
        message='CPF deve ser nesse formato: XXX.XXX.XXX-XX'
        )
]

phone_validators = [
    RegexValidator(
        regex=r'^\(\d{2}\) \d{4,5}\-\d{4}$',
        message='Telefone deve ser nesse formato: (XX) XXXXX-XXXX'
        )
]

cep_validators = [
    RegexValidator(
        regex=r'^\d{5}\-\d{3}$',
        message='CEP deve ser nesse formato: XXXXX-XXX'
        )
]

cnpj_validators = [
    RegexValidator(
        regex=r'^\d{2}\.\d{3}\.\d{3}/\d{4}\-\d{2}$',
        message='CNPJ deve ser nesse formato: XX.XXX.XXX/XXXX-XX'
        )
]

class Carro(models.Model):
    placa = models.CharField(max_length=10, unique=True, validators=plate_validators, verbose_name='Placa')
    modelo = models.CharField(max_length=50, verbose_name='Modelo')
    marca = models.CharField(max_length=50, verbose_name='Marca')
    ano = models.PositiveIntegerField(verbose_name='Ano')
    preco_base_dia = models.DecimalField(max_digits=10, 
    decimal_places=2, verbose_name='Preço Base por Dia', default=100.00)
    status = models.CharField(
        max_length=20, 
        choices=[('disponivel', 'Disponível'), ('indisponivel', 'Indisponível'), ('manutencao', 'Manutenção')], 
        default='disponivel',
        verbose_name='Status'
    )

    class Meta:
        db_table = 'carro'
        verbose_name = 'Carro'
        verbose_name_plural = 'Carros'

    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.placa}) - {self.get_status_display()}"

class Cliente(models.Model):
    nome = models.CharField(max_length=100, verbose_name='Nome')
    cpf = models.CharField(max_length=14, unique=True, validators=cpf_validators, verbose_name='CPF')
    email = models.EmailField(unique=True, verbose_name='E-mail')
    telefone = models.CharField(max_length=15, unique=True, validators=phone_validators, verbose_name='Telefone')
    cep = models.CharField(max_length=9, validators=cep_validators, verbose_name='CEP')

    class Meta:
        db_table = 'cliente'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return self.nome

class Empresa(models.Model):
    nome = models.CharField(max_length=100, verbose_name='Nome')
    cnpj = models.CharField(max_length=18, unique=True, validators=cnpj_validators, verbose_name='CNPJ')
    email = models.EmailField(unique=True, verbose_name='E-mail')
    telefone = models.CharField(max_length=15, unique=True, validators=phone_validators, verbose_name='Telefone')
    cep = models.CharField(max_length=9, validators=cep_validators, verbose_name='CEP')

    class Meta:
        db_table = 'empresa'
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

    def __str__(self):
        return self.nome

class Usuario(models.Model):
    nome_usuario = models.CharField(max_length=50, unique=True, verbose_name='Nome de Usuário')
    senha = models.CharField(max_length=128, verbose_name='Senha')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name='Empresa', db_column='empresa_id')

    class Meta:
        db_table = 'usuario'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'

    def __str__(self):
        return self.nome_usuario

class Vendedor(models.Model):
    nome = models.CharField(max_length=100, verbose_name='Nome')
    cpf = models.CharField(max_length=14, unique=True, validators=cpf_validators, verbose_name='CPF')
    email = models.EmailField(unique=True, verbose_name='E-mail')
    telefone = models.CharField(max_length=15, unique=True, validators=phone_validators, verbose_name='Telefone')

    class Meta:
        db_table = 'vendedor'
        verbose_name = 'Vendedor'
        verbose_name_plural = 'Vendedores'

    def __str__(self):
        return self.nome

class Aluguel(models.Model):
    data_aluguel = models.DateField(verbose_name='Data de Aluguel')
    data_devolucao_prevista = models.DateField(verbose_name='Data de Devolução Prevista')
    data_devolucao_real = models.DateField(null=True, blank=True, verbose_name='Data de Devolução Real')
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor Total')
    carro = models.ForeignKey(Carro, on_delete=models.CASCADE, verbose_name='Carro', db_column='carro_id')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name='Cliente', db_column='cliente_id')
    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE, verbose_name='Vendedor', db_column='vendedor_id')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name='Empresa', db_column='empresa_id')

    def calcular_preco(self):
        dias = (self.data_devolucao_prevista - self.data_aluguel).days + 1
        total = Decimal(dias) * self.carro.preco_base_dia

        # verifica se há feriado no intervalo
        data_atual = self.data_aluguel
        aumento_por_feriado = False

        while data_atual <= self.data_devolucao_prevista:
            if data_atual in FERIADOS:
                aumento_por_feriado = True
                break
            data_atual += timedelta(days=1)

        if aumento_por_feriado:
            total *= Decimal('1.20')  # +20%

        return total

    def save(self, *args, **kwargs):
        if self.data_aluguel and self.data_devolucao_prevista and self.carro:
            self.valor_total = self.calcular_preco()
        super().save(*args, **kwargs)    

    class Meta:
        db_table = 'aluguel'
        verbose_name = 'Aluguel'
        verbose_name_plural = 'Aluguéis'

    def __str__(self):
        return f"Aluguel {self.id} - {self.cliente.nome} - {self.carro.modelo}"
