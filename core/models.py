from django.db import models
from django.db.models import QuerySet
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import RegexValidator
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal
import re
import unicodedata

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

class UsuarioManager(BaseUserManager):
    """
    Manager customizado para o model Usuario.
    - create_user: cria e salva um usuário normal (usa set_password para hash).
    - create_superuser: cria um superuser com is_staff/is_superuser True.
    """
    def create_user(self, username, password=None, empresa=None, **extra_fields):
        if empresa:
            empresa = Empresa.objects.get(id=empresa)

        user = self.model(
            username=username,
            empresa=empresa,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser precisa ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser precisa ter is_superuser=True.')

        return self.create_user(username, password, **extra_fields)

# ---------- BaseModel, SoftDeleteQuerySet e Manager ----------
class SoftDeleteQuerySet(QuerySet):
    def delete(self):
        return super().update(is_deleted=True, deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()

    def restore(self):
        return super().update(is_deleted=False, deleted_at=None)

    def alive(self):
        return self.filter(is_deleted=False)

    def dead(self):
        return self.filter(is_deleted=True)


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def with_deleted(self):
        return SoftDeleteQuerySet(self.model, using=self._db)

    def only_deleted(self):
        return self.with_deleted().filter(is_deleted=True)


class BaseModel(models.Model):
    """
    Modelo abstrato com:
    - created_at / updated_at
    - soft-delete (is_deleted, deleted_at) e métodos de soft/hard delete
    - version para controle de versão simples
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    version = models.PositiveIntegerField(default=1)

    objects = SoftDeleteManager()
    all_objects = models.Manager()  # acessa todos os registros, inclusive deletados

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False, hard=False):
        if hard:
            return super().delete(using=using, keep_parents=keep_parents)
        self.is_deleted = True
        self.deleted_at = timezone.now()
        # incrementa versão antes de salvar
        self.version = (self.version or 1) + 1
        self.save(update_fields=['is_deleted', 'deleted_at', 'version'])

    def hard_delete(self):
        return super().delete()

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.version = (self.version or 1) + 1
        self.save(update_fields=['is_deleted', 'deleted_at', 'version'])

    def save(self, *args, **kwargs):
        if self.pk:
            self.version = (self.version or 1) + 1
        super().save(*args, **kwargs)

class Empresa(BaseModel):
    nome = models.CharField(max_length=100, verbose_name='Nome')
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    cnpj = models.CharField(max_length=18, unique=True, validators=cnpj_validators, verbose_name='CNPJ')
    email = models.EmailField(unique=True, verbose_name='E-mail')
    telefone = models.CharField(max_length=20, unique=True, validators=phone_validators, verbose_name='Telefone')
    cep = models.CharField(max_length=9, validators=cep_validators, verbose_name='CEP')
    
    # Factory Method: tipo de política de cálculo por empresa
    FACTORY_CHOICES = [
        ('padrao', 'Padrão'),
        ('premium', 'Premium'),
        ('comercial', 'Comercial'),
    ]
    tipo_calculo = models.CharField(
        max_length=20,
        choices=FACTORY_CHOICES,
        default='padrao',
        verbose_name='Tipo de Cálculo de Aluguel'
    )
    
    # Decorator Pattern: flags para compor políticas de preço
    aplica_acrescimo_feriado = models.BooleanField(
        default=True,
        verbose_name='Acréscimo em Feriados (20%)'
    )
    aplica_acrescimo_fim_semana = models.BooleanField(
        default=False,
        verbose_name='Acréscimo em Fim de Semana (15%)'
    )
    aplica_acrescimo_temporada_alta = models.BooleanField(
        default=False,
        verbose_name='Acréscimo Temporada Alta (25%)'
    )

    class Meta:
        db_table = 'empresa'
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

    def __str__(self):
        return self.nome
    
    def get_aluguel_factory(self):
        """Retorna a factory apropriada para esta empresa (Factory Method)."""
        from .factories import AluguelFactoryPadrao, AluguelFactoryPremium, AluguelFactoryComercial
        
        if self.tipo_calculo == 'premium':
            return AluguelFactoryPremium()
        elif self.tipo_calculo == 'comercial':
            return AluguelFactoryComercial()
        return AluguelFactoryPadrao()

    @staticmethod
    def gerar_slug(nome):
        nome_normalizado = unicodedata.normalize('NFKD', nome or '')
        nome_sem_acentos = nome_normalizado.encode('ascii', 'ignore').decode('ascii')
        slug = re.sub(r'[^a-zA-Z0-9\s]', '', nome_sem_acentos).lower()
        return re.sub(r'\s+', '', slug)

    def save(self, *args, **kwargs):
        self.slug = self.gerar_slug(self.nome)
        super().save(*args, **kwargs)

class Carro(BaseModel):
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
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name='Empresa', db_column='empresa_id')

    class Meta:
        db_table = 'carros'
        verbose_name = 'Carro'
        verbose_name_plural = 'Carros'

    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.placa}) - {self.get_status_display()}"

class Cliente(BaseModel):
    nome = models.CharField(max_length=100, verbose_name='Nome')
    cpf = models.CharField(max_length=14, unique=True, validators=cpf_validators, verbose_name='CPF')
    email = models.EmailField(unique=True, verbose_name='E-mail')
    telefone = models.CharField(max_length=20, unique=True, validators=phone_validators, verbose_name='Telefone')
    cep = models.CharField(max_length=9, validators=cep_validators, verbose_name='CEP')

    class Meta:
        db_table = 'clientes'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return self.nome



class Usuario(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=150, unique=True, verbose_name='UserName')
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.CASCADE,
        verbose_name='Empresa',
        db_column='empresa_id',
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = []
    class Meta:
        db_table = 'usuarios'
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'


class Vendedor(BaseModel):
    nome = models.CharField(max_length=100, verbose_name='Nome')
    cpf = models.CharField(max_length=14, unique=True, validators=cpf_validators, verbose_name='CPF')
    email = models.EmailField(unique=True, verbose_name='E-mail')
    telefone = models.CharField(max_length=20, unique=True, validators=phone_validators, verbose_name='Telefone')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name='Empresa', db_column='empresa_id')

    class Meta:
        db_table = 'vendedores'
        verbose_name = 'Vendedor'
        verbose_name_plural = 'Vendedores'

    def __str__(self):
        return self.nome

class Aluguel(BaseModel):
    data_aluguel = models.DateField(verbose_name='Data de Aluguel')
    data_devolucao_prevista = models.DateField(verbose_name='Data de Devolução Prevista')
    data_devolucao_real = models.DateField(null=True, blank=True, verbose_name='Data de Devolução Real')
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor Total')
    carro = models.ForeignKey(Carro, on_delete=models.CASCADE, verbose_name='Carro', db_column='carro_id')
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name='Cliente', db_column='cliente_id')
    vendedor = models.ForeignKey(Vendedor, on_delete=models.CASCADE, verbose_name='Vendedor', db_column='vendedor_id')
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name='Empresa', db_column='empresa_id')
    multa = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    # State Pattern: ciclo de vida do aluguel
    STATUS_CHOICES = [
        ('criado', 'Criado'),
        ('ativo', 'Ativo'),
        ('devolvido', 'Devolvido'),
        ('com_atraso', 'Com Atraso'),
        ('cancelado', 'Cancelado'),
    ]
    status_aluguel = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='criado',
        verbose_name='Status do Aluguel'
    )
    
    # Atributo transiente (não persiste em DB) - apenas em memória
    _estado = None

    class Meta:
        db_table = 'alugueis'
        verbose_name = 'Aluguel'
        verbose_name_plural = 'Aluguéis'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._inicializar_estado()
    
    def _inicializar_estado(self):
        """Mapeia string status_aluguel para objeto de estado (State Pattern)."""
        from .aluguel_state import (
            AluguelCriado, AluguelAtivo, AluguelDevolvido,
            AluguelComAtraso, AluguelCancelado
        )
        
        estado_map = {
            'criado': AluguelCriado(),
            'ativo': AluguelAtivo(),
            'devolvido': AluguelDevolvido(),
            'com_atraso': AluguelComAtraso(),
            'cancelado': AluguelCancelado(),
        }
        self._estado = estado_map.get(self.status_aluguel, AluguelCriado())
    
    def ativar(self):
        """Transiciona de Criado para Ativo (State Pattern)."""
        if self.status_aluguel != 'criado':
            raise Exception(
                f"Não é possível ativar um aluguel em estado '{self.status_aluguel}'."
            )
        self.status_aluguel = 'ativo'
        self._inicializar_estado()
        self.carro.status = 'alugado'
        self.carro.save(update_fields=['status'])
        self.save(update_fields=['status_aluguel'])
    
    def devolver(self):
        """Processa devolução via state pattern."""
        self._estado.devolver(self)
        # Atualiza status_aluguel baseado no estado
        from .aluguel_state import AluguelDevolvido, AluguelComAtraso
        if isinstance(self._estado, AluguelComAtraso):
            self.status_aluguel = 'com_atraso'
        elif isinstance(self._estado, AluguelDevolvido):
            self.status_aluguel = 'devolvido'
        self.save(update_fields=['status_aluguel', 'data_devolucao_real', 'multa'])
    
    def cancelar(self):
        """Cancela aluguel (apenas se criado)."""
        if self.status_aluguel != 'criado':
            raise Exception(
                f"Não é possível cancelar um aluguel em estado '{self.status_aluguel}'."
            )
        self.status_aluguel = 'cancelado'
        self._inicializar_estado()
        self.save(update_fields=['status_aluguel'])
    
    def pode_editar(self) -> bool:
        """Verifica se aluguel pode ser editado (State Pattern)."""
        return self._estado.pode_editar()
    
    def _calcular_multa(self, atraso_dias: int) -> Decimal:
        """Calcula multa por atraso (20% por dia de atraso)."""
        return atraso_dias * self.valor_total * Decimal('0.20')
    
    def calcular_preco_com_politica(self, empresa):
        """Calcula preço usando Decorator Pattern com políticas da empresa."""
        from .price_calculator import (
            PriceCalculatorBase,
            FeriadoDecorator,
            FimDeSemanDecorator,
            TemporadaAltaDecorator
        )
        
        dias = (self.data_devolucao_prevista - self.data_aluguel).days + 1
        
        # Cria calculador base
        calculator = PriceCalculatorBase()
        
        # Compõe com decorators conforme política da empresa
        if empresa.aplica_acrescimo_feriado:
            calculator = FeriadoDecorator(calculator)
        
        if empresa.aplica_acrescimo_fim_semana:
            calculator = FimDeSemanDecorator(calculator)
        
        if empresa.aplica_acrescimo_temporada_alta:
            calculator = TemporadaAltaDecorator(calculator)
        
        return calculator.calcular(
            dias=dias,
            preco_base_dia=self.carro.preco_base_dia,
            data_inicio=self.data_aluguel,
            data_fim=self.data_devolucao_prevista
        )

    def save(self, *args, **kwargs):
        if self.data_aluguel and self.data_devolucao_prevista and self.carro and self.empresa:
            self.valor_total = self.calcular_preco_com_politica(self.empresa)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Aluguel {self.id} - {self.cliente.nome} - {self.carro.modelo} ({self.get_status_aluguel_display()})"
