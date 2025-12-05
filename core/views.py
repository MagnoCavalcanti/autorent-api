from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer, RegistroUsuarioSerializer

class MyTokenObtainPairView(TokenObtainPairView):
    """
    View para obter token JWT.
    POST /api/v1/auth/login/
    Body: { "username": "joao", "password": "senha123" }
    """
    serializer_class = MyTokenObtainPairSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def registro_usuario(request):
    """
    Endpoint para registrar novo usuário.
    POST /api/v1/auth/registro/
    
    Body esperado:
    {
        "username": "joao",
        "password": "senha123",
        "nome_empresa": "AutoRent Brasil",
        "email": "joao@email.com"  # opcional
    }
    
    Retorno sucesso (201):
    {
        "message": "Usuário criado com sucesso!",
        "usuario": {
            "username": "joao",
            "email": "joao@email.com"
        }
    }
    """
    serializer = RegistroUsuarioSerializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        return Response({
            'message': 'Usuário criado com sucesso!',
            'usuario': {
                'username': serializer.validated_data['username'],
                'email': serializer.validated_data.get('email', '')
            }
        }, status=status.HTTP_201_CREATED)
    
    # retorna erros de validação
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
