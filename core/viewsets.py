from rest_framework import viewsets
from .models import Carro, Cliente, Empresa, Usuario, Vendedor, Aluguel
from .serializers import (
    CarroSerializer,
    ClienteSerializer,
    EmpresaSerializer,
    UsuarioSerializer,
    VendedorSerializer,
    AluguelSerializer
)


class CarroViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações CRUD de Carro
    """
    queryset = Carro.objects.all()
    serializer_class = CarroSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtro opcional por status
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        return queryset


class ClienteViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações CRUD de Cliente
    """
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtro opcional por CPF
        cpf = self.request.query_params.get('cpf', None)
        if cpf:
            queryset = queryset.filter(cpf=cpf)
        return queryset


class EmpresaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações CRUD de Empresa
    """
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações CRUD de Usuario
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # Filtro opcional por empresa
        empresa_id = self.request.query_params.get('empresa_id', None)
        if empresa_id:
            queryset = queryset.filter(empresa_id=empresa_id)
        return queryset


class VendedorViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações CRUD de Vendedor
    """
    queryset = Vendedor.objects.all()
    serializer_class = VendedorSerializer


class AluguelViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações CRUD de Aluguel
    """
    queryset = Aluguel.objects.all()
    serializer_class = AluguelSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros opcionais
        cliente_id = self.request.query_params.get('cliente_id', None)
        carro_id = self.request.query_params.get('carro_id', None)
        empresa_id = self.request.query_params.get('empresa_id', None)
        
        if cliente_id:
            queryset = queryset.filter(cliente_id=cliente_id)
        if carro_id:
            queryset = queryset.filter(carro_id=carro_id)
        if empresa_id:
            queryset = queryset.filter(empresa_id=empresa_id)
            
        return queryset.order_by('-data_aluguel')
