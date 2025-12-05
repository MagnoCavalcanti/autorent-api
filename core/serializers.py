from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Carro, Cliente, Empresa, Vendedor, Aluguel, Usuario
from .mixins import EmpresaFromURLMixin
from django.contrib.auth import authenticate
from django.utils import timezone
from datetime import date
from decimal import Decimal

class CarroSerializer(EmpresaFromURLMixin, serializers.ModelSerializer):
    class Meta:
        model = Carro
        fields = ['marca', 'modelo', 'ano', 'placa', 'status', 'preco_base_dia']
        read_only_fields = ['empresa']

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['nome', 'cpf', 'email', 'telefone', 'cep']

class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = ['nome', 'cep', 'telefone', 'email', 'cnpj']


class VendedorSerializer(EmpresaFromURLMixin, serializers.ModelSerializer):
    class Meta:
        model = Vendedor
        fields = ['nome', 'cpf', 'email', 'telefone']
        read_only_fields = ['empresa']
        
class AluguelSerializer(EmpresaFromURLMixin, serializers.ModelSerializer):
    cliente = ClienteSerializer()

    class Meta:
        model = Aluguel
        fields = ['carro', 'cliente', 'vendedor', 'data_aluguel', 'data_devolucao_prevista', 'valor_total'
        ]
        read_only_fields = ['valor_total', 'empresa']
    
    def validate(self, attrs):
            carro = attrs.get('carro')

            if carro.status != 'disponivel':
                raise serializers.ValidationError(
                    {"carro": "Este carro não está disponível para aluguel."}
                )

            return attrs
    
    def create(self, validated_data):
        request = self.context["request"]
        empresa_slug = self.context["view"].kwargs["empresa"]  # nome da empresa recebido na URL

        # Busca a empresa pelo nome
        try:
            empresa = Empresa.objects.get(nome=empresa_slug)
        except Empresa.DoesNotExist:
            raise serializers.ValidationError({"empresa": "Empresa não encontrada."})
        cliente_data = validated_data.pop('cliente')

        # cliente existente ou não
        cliente, created = Cliente.objects.get_or_create(
            cpf=cliente_data['cpf'],
            defaults=cliente_data
        )

        carro  = validated_data['carro']

        # DATAS
        data_aluguel = validated_data['data_aluguel']
        data_prevista = validated_data['data_devolucao_prevista']
        # Cálculo de dias
        dias = (data_prevista - data_aluguel).days
        if dias <= 0:
            dias = 1  # garante pelo menos 1 diária

        # Cálculo do valor total
        valor_total = dias * carro.preco_base_dia

        # Criar o aluguel
        aluguel = Aluguel.objects.create(
            cliente=cliente,
            valor_total=valor_total,
            empresa=empresa,
            **validated_data
        )

        # Atualiza status do carro
        carro.status = 'alugado'
        carro.save()

        return aluguel

    
class DevolucaoSerializer(serializers.Serializer):
    aluguel_id = serializers.IntegerField()

    def validate_aluguel_id(self, value):
        try:
            aluguel = Aluguel.objects.get(id=value)
        except Aluguel.DoesNotExist:
            raise serializers.ValidationError("Aluguel não encontrado.")

        if aluguel.devolvido:
            raise serializers.ValidationError("Este aluguel já foi devolvido.")

        return value

    def save(self):
        aluguel = Aluguel.objects.get(id=self.validated_data['aluguel_id'])
        veiculo = aluguel.veiculo

        hoje = date.today()
        aluguel.data_devolucao_real = hoje

        # Calcular atraso
        atraso = (hoje - aluguel.data_devolucao_prevista).days

        if atraso > 0:
            # multa = dias * valor_diaria * 20%
            aluguel.multa = atraso * aluguel.valor_total * Decimal("0.20")
        else:
            aluguel.multa = 0

        
        aluguel.save()

        # Deixar veículo disponível
        veiculo.status = 'disponivel'
        veiculo.save()

        return aluguel


class RegistroUsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer para registrar novo usuário.
    Recebe: nome_usuario, password, nome_empresa
    Retorna: nome_usuario, email (sem password)
    """
    nome_empresa = serializers.CharField(write_only=True, required=True, label='Nome da Empresa')
    password = serializers.CharField(write_only=True, required=True, min_length=6, label='Senha')
    
    class Meta:
        model = Usuario
        fields = ['username', 'password', 'nome_empresa']
        extra_kwargs = {
            'username': {'required': True}
        }
    
    def validate_nome_usuario(self, value):
        """Valida se nome_usuario já existe"""
        if Usuario.objects.filter(username=value).exists():
            raise serializers.ValidationError('Este nome de usuário já está em uso.')
        return value
    
    def validate_nome_empresa(self, value):
        """Valida se empresa existe e retorna o objeto"""
        try:
            empresa = Empresa.objects.get(nome=value)
        except Empresa.DoesNotExist:
            raise serializers.ValidationError(f"Empresa '{value}' não encontrada.")
        return empresa
    
    def create(self, validated_data):
        """Cria o usuário com a senha hasheada"""
        empresa = validated_data.pop('nome_empresa')  # remove e pega a empresa
        password = validated_data.pop('password')  # remove e pega a senha
        
        # cria usuário com create_user do manager (que faz o hash)
        user = Usuario.objects.create_user(
            username=validated_data['username'],
            password=password,
            empresa=empresa,
        )
        return user


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer customizado para obter token JWT.
    Usa username como campo de login.
    """
    username_field = 'username'

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # adiciona informações extras ao token
        token['username'] = user.username
        token['empresa_id'] = user.empresa_id
        return token

    def validate(self, attrs):
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            'password': attrs['password'],
        }
        try:
            authenticate_user = authenticate(**authenticate_kwargs)
        except TypeError:
            raise serializers.ValidationError('Nome de usuário ou senha inválidos.')

        if authenticate_user is None or not authenticate_user.is_active:
            raise serializers.ValidationError('Nenhuma conta ativa encontrada com essas credenciais.')

        return super().validate(attrs)
