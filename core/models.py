from django.db import models
from django.db.models import QuerySet
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import RegexValidator
from django.utils import timezone
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

class UsuarioManager(BaseUserManager):
    """
    Manager customizado para o model Usuario.
    - create_user: cria e salva um usuário normal (usa set_password para hash).
    - create_superuser: cria um superuser com is_staff/is_superuser True.
    """
    def create_user(self, username, password=None, empresa=None, **extra_fields):
        if not username:
            raise ValueError('O campo username é obrigatório')
        # se empresa vier em extra_fields, usa e remove
        if empresa is None and 'empresa' in extra_fields:
            empresa = extra_fields.pop('empresa')
        user = self.model(username=username, empresa=empresa, **extra_fields)
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
    cnpj = models.CharField(max_length=18, unique=True, validators=cnpj_validators, verbose_name='CNPJ')
    email = models.EmailField(unique=True, verbose_name='E-mail')
    telefone = models.CharField(max_length=20, unique=True, validators=phone_validators, verbose_name='Telefone')
    cep = models.CharField(max_length=9, validators=cep_validators, verbose_name='CEP')

    class Meta:
        db_table = 'empresa'
        verbose_name = 'Empresa'
        verbose_name_plural = 'Empresas'

    def __str__(self):
        return self.nome

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
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE, verbose_name='Empresa', db_column='empresa_id')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['empresa']
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
        db_table = 'alugueis'
        verbose_name = 'Aluguel'
        verbose_name_plural = 'Aluguéis'

    def __str__(self):
        return f"Aluguel {self.id} - {self.cliente.nome} - {self.carro.modelo}"
