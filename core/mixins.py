from rest_framework.exceptions import NotFound
from .models import Empresa

class EmpresaFromURLMixin:
    def get_empresa(self):
        nome_empresa = self.kwargs.get('empresa')

        try:
            return Empresa.objects.get(nome=nome_empresa)
        except Empresa.DoesNotExist:
            raise NotFound("Empresa não encontrada.")
