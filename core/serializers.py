from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings
from .models import Carro, Cliente, Empresa, Vendedor, Aluguel, Usuario
from .mixins import EmpresaFromURLMixin
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.db import transaction, IntegrityError
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
        fields = ['nome', 'slug', 'cep', 'telefone', 'email', 'cnpj']
        read_only_fields = ['slug']


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

        # Busca a empresa pelo slug
        try:
            empresa = Empresa.objects.get(slug=empresa_slug)
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


class EmpresaRegistroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = ['nome', 'cep', 'telefone', 'email', 'cnpj']


class RegistroUsuarioSerializer(serializers.Serializer):
    username = serializers.CharField(required=True, max_length=150)
    password = serializers.CharField(write_only=True, required=True, min_length=6)
    empresa = EmpresaRegistroSerializer(required=True)

    def validate(self, attrs):
        empresa_data = attrs.get('empresa')
        if not isinstance(empresa_data, dict):
            raise serializers.ValidationError({
                'empresa': 'Campo empresa é obrigatório e deve ser um objeto válido.'
            })
        if Usuario.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({'username': 'Este nome de usuário já está em uso.'})
        if Empresa.objects.filter(email=empresa_data.get('email')).exists():
            raise serializers.ValidationError({'empresa': {'email': 'Este email já está cadastrado.'}})
        if Empresa.objects.filter(cnpj=empresa_data.get('cnpj')).exists():
            raise serializers.ValidationError({'empresa': {'cnpj': 'Este CNPJ já está cadastrado.'}})
        return attrs

    def create(self, validated_data):
        empresa_data = validated_data.pop('empresa')
        password = validated_data.pop('password')

        try:
            with transaction.atomic():
                empresa = Empresa.objects.create(**empresa_data)
                usuario = Usuario.objects.create_user(
                    username=validated_data['username'],
                    password=password,
                    empresa=empresa,
                )
                return usuario
        except IntegrityError as exc:
            mensagem = str(exc).lower()
            if 'empresa.email' in mensagem or 'email' in mensagem:
                raise serializers.ValidationError({'empresa': {'email': 'Este email já está cadastrado.'}})
            if 'empresa.cnpj' in mensagem or 'cnpj' in mensagem:
                raise serializers.ValidationError({'empresa': {'cnpj': 'Este CNPJ já está cadastrado.'}})
            raise serializers.ValidationError({'detail': 'Não foi possível concluir o registro.'})


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer customizado para obter token JWT.
    Usa username como campo de login.
    """
    username_field = 'username'
    empresa = serializers.CharField(write_only=True, required=False, allow_null=True)

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # adiciona informações extras ao token
        token['username'] = user.username
        token['empresa'] = getattr(user, '_empresa_slug_token', None)
        return token

    def validate(self, attrs):
        empresa_slug = attrs.get('empresa', None)
        authenticate_kwargs = {
            self.username_field: attrs[self.username_field],
            'password': attrs['password'],
        }
        try:
            authenticate_user = authenticate(**authenticate_kwargs)
        except TypeError:
            raise AuthenticationFailed('Credenciais inválidas.')

        if authenticate_user is None or not authenticate_user.is_active:
            raise AuthenticationFailed('Credenciais inválidas.')

        if not (authenticate_user.is_staff or authenticate_user.is_superuser):
            if not empresa_slug:
                raise serializers.ValidationError({'detail': 'O campo empresa é obrigatório.'})
            if not authenticate_user.empresa or authenticate_user.empresa.slug != empresa_slug:
                raise AuthenticationFailed('Credenciais inválidas.')

        authenticate_user._empresa_slug_token = empresa_slug or None
        refresh = self.get_token(authenticate_user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, authenticate_user)
        return data
