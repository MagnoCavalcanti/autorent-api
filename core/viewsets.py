from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Carro, Cliente, Empresa, Vendedor, Aluguel
from rest_framework.exceptions import ValidationError
from .serializers import (
    CarroSerializer,
    ClienteSerializer,
    EmpresaSerializer,
    VendedorSerializer,
    AluguelSerializer
)
from rest_framework import permissions
from .pagination import FiveResultsPagination  # <-- adicionado



class EmpresaBaseViewSet(viewsets.ModelViewSet):

    def get_empresa(self):
        empresa_slug = self.kwargs.get("empresa")

        try:
            return Empresa.objects.get(nome=empresa_slug)
        except Empresa.DoesNotExist:
            raise ValidationError({"empresa": "Empresa não encontrada."})

    def get_queryset(self):
        empresa = self.get_empresa()
        return super().get_queryset().filter(empresa=empresa)

    def perform_create(self, serializer):
        empresa = self.get_empresa()
        serializer.save(empresa=empresa)


class CarroViewSet(EmpresaBaseViewSet, viewsets.ModelViewSet):
    """
    ViewSet para operações CRUD de Carro
    """
    queryset = Carro.objects.all()
    serializer_class = CarroSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = FiveResultsPagination  # <-- adicionado
    
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
    permission_classes = [IsAuthenticated]
    pagination_class = FiveResultsPagination  # <-- adicionado
    
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
    pagination_class = FiveResultsPagination  # <-- adicionado
    permission_classes = [permissions.AllowAny]



class VendedorViewSet(EmpresaBaseViewSet, viewsets.ModelViewSet):
    """
    ViewSet para operações CRUD de Vendedor
    """
    queryset = Vendedor.objects.all()
    serializer_class = VendedorSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = FiveResultsPagination  # <-- adicionado


class AluguelViewSet(EmpresaBaseViewSet):
    """
    ViewSet para operações CRUD de Aluguel
    """
    queryset = Aluguel.objects.all()
    serializer_class = AluguelSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = FiveResultsPagination  # <-- adicionado
    

    def perform_create(self, serializer):
        empresa = self.get_empresa()
        serializer.save(empresa=empresa)
