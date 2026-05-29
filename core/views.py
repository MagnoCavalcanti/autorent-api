from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer, RegistroUsuarioSerializer
from .permissions import IsSuperuserOrStaff
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiResponse,
    extend_schema,
    extend_schema_view,
    inline_serializer,
)

@extend_schema_view(
    post=extend_schema(
        tags=['Autenticação'],
        summary='Login com validação de empresa',
        description=(
            'Autentica usuário por `username`, `password` e opcionalmente `empresa` (slug). '
            'Para usuários comuns, o campo empresa é obrigatório e deve coincidir com a vinculada ao usuário. '
            'Para staff/superuser, `empresa` é opcional; quando não enviada, o token retorna `empresa: null`.'
        ),
        request=MyTokenObtainPairSerializer,
        responses={
            200: inline_serializer(
                name='LoginResponse',
                fields={
                    'refresh': serializers.CharField(),
                    'access': serializers.CharField(),
                },
            ),
            400: OpenApiResponse(description='Campo empresa ausente para usuário comum.'),
            401: OpenApiResponse(description='Credenciais inválidas.'),
        },
        examples=[
            OpenApiExample(
                'Body do login com empresa',
                value={
                    'username': 'joao',
                    'password': 'senha123',
                    'empresa': 'autorentbrasil',
                },
                request_only=True,
            ),
            OpenApiExample(
                'Body do login sem empresa (staff/superuser)',
                value={
                    'username': 'admin',
                    'password': 'admin123',
                },
                request_only=True,
            )
        ],
    )
)
class MyTokenObtainPairView(TokenObtainPairView):
    """
    View para obter token JWT.
    POST /api/v1/auth/login/
    Body: { "username": "joao", "password": "senha123", "empresa": "autorentbrasil" }
    """
    serializer_class = MyTokenObtainPairSerializer


@extend_schema(
    tags=['Autenticação'],
    summary='Registrar usuário com empresa',
    description=(
        'Cria usuário e empresa de forma atômica em uma única requisição. '
        'Requer autenticação JWT e permissão de staff ou superuser.'
    ),
    request=RegistroUsuarioSerializer,
    responses={
        201: inline_serializer(
            name='RegistroUsuarioResponse',
            fields={
                'message': serializers.CharField(),
                'usuario': inline_serializer(
                    name='RegistroUsuarioResponseUsuario',
                    fields={'username': serializers.CharField()},
                ),
                'empresa': inline_serializer(
                    name='RegistroUsuarioResponseEmpresa',
                    fields={
                        'nome': serializers.CharField(),
                        'slug': serializers.CharField(),
                    },
                ),
            },
        ),
        400: OpenApiResponse(description='Dados inválidos ou campo duplicado (email/cnpj).'),
        403: OpenApiResponse(description='Usuário autenticado sem permissão (não staff/superuser).'),
    },
    examples=[
        OpenApiExample(
            'Body de registro',
            value={
                'username': 'joao',
                'password': 'senha123',
                'empresa': {
                    'nome': 'AutoRent Brasil',
                    'cep': '01234-567',
                    'telefone': '(11) 99999-9999',
                    'email': 'contato@autorent.com',
                    'cnpj': '12.345.678/0001-90',
                },
            },
            request_only=True,
        ),
        OpenApiExample(
            'Resposta de sucesso',
            value={
                'message': 'Usuário criado com sucesso!',
                'usuario': {'username': 'joao'},
                'empresa': {
                    'nome': 'AutoRent Brasil',
                    'slug': 'autorentbrasil',
                },
            },
            response_only=True,
            status_codes=['201'],
        ),
    ],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSuperuserOrStaff])
def registro_usuario(request):
    """
    Endpoint para registrar novo usuário.
    POST /api/v1/auth/registro/
    
    Body esperado:
    {
        "username": "joao",
        "password": "senha123",
        "empresa": {
            "nome": "AutoRent Brasil",
            "cep": "01234-567",
            "telefone": "(11) 99999-9999",
            "email": "contato@autorent.com",
            "cnpj": "12.345.678/0001-90"
        }
    }
    
    Retorno sucesso (201):
    {
        "message": "Usuário criado com sucesso!",
        "usuario": {
            "username": "joao"
        },
        "empresa": {
            "nome": "AutoRent Brasil",
            "slug": "autorentbrasil"
        }
    }
    """
    serializer = RegistroUsuarioSerializer(data=request.data)
    
    if serializer.is_valid():
        usuario = serializer.save()
        return Response({
            'message': 'Usuário criado com sucesso!',
            'usuario': {
                'username': usuario.username,
            },
            'empresa': {
                'nome': usuario.empresa.nome,
                'slug': usuario.empresa.slug,
            }
        }, status=status.HTTP_201_CREATED)
    
    # retorna erros de validação
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
