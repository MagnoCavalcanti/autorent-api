from django.contrib import admin

from .models import Carro, Cliente, Empresa, Usuario, Vendedor, Aluguel

admin.site.register(Carro)
admin.site.register(Cliente)
admin.site.register(Empresa)
admin.site.register(Usuario)
admin.site.register(Vendedor)
admin.site.register(Aluguel)