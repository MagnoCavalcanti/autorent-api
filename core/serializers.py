from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Carro, Cliente, Empresa, Vendedor, Aluguel, Usuario
from django.contrib.auth import authenticate

class CarroSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carro
        fields = '__all__'

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = '__all__'


class VendedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendedor
        fields = '__all__'
        
class AluguelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aluguel
        fields = '__all__'

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
