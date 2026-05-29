from rest_framework.exceptions import NotFound
from .models import Empresa

class EmpresaFromURLMixin:
    def get_empresa(self):
        empresa_slug = self.kwargs.get('empresa')

        try:
            return Empresa.objects.get(slug=empresa_slug)
        except Empresa.DoesNotExist:
            raise NotFound("Empresa não encontrada.")
