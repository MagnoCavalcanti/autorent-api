from django.db import models

plate_validators = [
    models.validators.RegexValidator(
        regex=r'^(?:[A-Z]{3}\-\d{4}|[A-Z]{3}\d[A-Z]\d{2})$',
        message='Placa deve ser nesse formato: XXX-0000 ou ABC1D23'
        )
]

cpf_validators = [
    models.validators.RegexValidator(
        regex=r'^\d{3}\.\d{3}\.\d{3}\-\d{2}$',
        message='CPF deve ser nesse formato: XXX.XXX.XXX-XX'
        )
]

phone_validators = [
    models.validators.RegexValidator(
        regex=r'^\(\d{2}\) \d{4,5}\-\d{4}$',
        message='Telefone deve ser nesse formato: (XX) XXXXX-XXXX'
        )
]

cep_validators = [
    models.validators.RegexValidator(
        regex=r'^\d{5}\-\d{3}$',
        message='CEP deve ser nesse formato: XXXXX-XXX'
        )
]

cnpj_validators = [
    models.validators.RegexValidator(
        regex=r'^\d{2}\.\d{3}\.\d{3}/\d{4}\-\d{2}$',
        message='CNPJ deve ser nesse formato: XX.XXX.XXX/XXXX-XX'
        )
]

class Car(models.Model):
    plate=models.CharField(max_length=10, unique=True, validators=plate_validators)
    model=models.CharField(max_length=50)
    brand=models.CharField(max_length=50)
    year=models.PositiveIntegerField()
    status=models.CharField(max_length=20, choices=[('disponivel', 'Disponível'), ('indisponivel', 'Indisponível'), ('manutenção', 'Manutenção')], default='disponivel')

    def __str__(self):
        return f"{self.brand} {self.model} ({self.plate}) - {self.status}"
    
class Customer(models.Model):
    name=models.CharField(max_length=100)
    cpf=models.CharField(max_length=14, unique=True, validators=cpf_validators)
    email=models.EmailField(unique=True)
    phone=models.CharField(max_length=15, unique=True, validators=phone_validators)
    cep=models.CharField(max_length=9, validators=cep_validators)


    def __str__(self):
        return self.name
    
class Enterprise(models.Model):
    name=models.CharField(max_length=100)
    cnpj=models.CharField(max_length=18, unique=True, validators=cnpj_validators)
    email=models.EmailField(unique=True)
    phone=models.CharField(max_length=15, unique=True, validators=phone_validators)
    cep=models.CharField(max_length=9, validators=cep_validators)

    def __str__(self):
        return self.name
    
class User(models.Model):
    username=models.CharField(max_length=50, unique=True)
    password=models.CharField(max_length=128)
    enterprise=models.ForeignKey(Enterprise, on_delete=models.CASCADE)

    def __str__(self):
        return self.username
    
class Seller(models.Model):
    name=models.CharField(max_length=100)
    cpf=models.CharField(max_length=14, unique=True, validators=cpf_validators)
    email=models.EmailField(unique=True)
    phone=models.CharField(max_length=15, unique=True, validators=phone_validators)

    def __str__(self):
        return self.name
    
class Rental(models.Model):
    date_rent=models.DateField()
    date_return_predicted=models.DateField()
    date_return_real=models.DateField(null=True, blank=True)
    total_value=models.DecimalField(max_digits=10, decimal_places=2)
    car=models.ForeignKey(Car, on_delete=models.CASCADE)
    customer=models.ForeignKey(Customer, on_delete=models.CASCADE)
    seller=models.ForeignKey(Seller, on_delete=models.CASCADE)
    enterprise=models.ForeignKey(Enterprise, on_delete=models.CASCADE)
