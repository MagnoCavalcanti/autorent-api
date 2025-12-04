import random
from datetime import date, timedelta
from decimal import Decimal
from faker import Faker

from core.models import Empresa, Usuario, Cliente, Vendedor, Carro, Aluguel

fake = Faker("pt_BR")

print("Limpando tabelas...")
Aluguel.objects.all().delete()
Carro.objects.all().delete()
Cliente.objects.all().delete()
Vendedor.objects.all().delete()
Usuario.objects.all().delete()
Empresa.objects.all().delete()

# -----------------------------------------------------
# Dados reais para carros
# -----------------------------------------------------
CARROS_REAIS = [
    ("Toyota", "Corolla"), ("Toyota", "Yaris"),
    ("Honda", "Civic"), ("Honda", "Fit"),
    ("Chevrolet", "Onix"), ("Chevrolet", "Cruze"),
    ("Volkswagen", "Gol"), ("Volkswagen", "Polo"),
    ("Hyundai", "HB20"), ("Hyundai", "Creta"),
    ("Fiat", "Argo"), ("Fiat", "Cronos"),
    ("Renault", "Kwid"),
    ("Nissan", "Kicks"),
    ("Jeep", "Renegade"),
]

print("Criando empresas...")
print(fake.cellphone_number())
empresas = []
for _ in range(10):
    nome = fake.company()
    empresa = Empresa.objects.create(
        nome=nome,
        cnpj=fake.cnpj(),
        email=fake.company_email(),
        telefone=fake.cellphone_number(),
        cep=fake.postcode()
    )
    empresas.append(empresa)

print("Criando usuários das empresas...")
for empresa in empresas:
    Usuario.objects.create(
        nome_usuario=empresa.nome.split()[0].lower(),
        senha="123456",
        empresa=empresa
    )

print("Criando clientes...")
clientes = []
for _ in range(200):
    nome = fake.name()
    cliente = Cliente.objects.create(
        nome=nome,
        cpf=fake.cpf(),
        email=fake.email(),
        telefone=fake.cellphone_number(),
        cep=fake.postcode()
    )
    clientes.append(cliente)

print("Criando vendedores...")
vendedores = []
for _ in range(60):
    nome = fake.name()
    vendedor = Vendedor.objects.create(
        nome=nome,
        cpf=fake.cpf(),
        email=fake.company_email(),
        telefone=fake.cellphone_number(),
        empresa=random.choice(empresas)
    )
    vendedores.append(vendedor)

print("Criando carros...")
carros = []
for _ in range(100):
    marca, modelo = random.choice(CARROS_REAIS)
    carro = Carro.objects.create(
        placa=fake.license_plate(),
        modelo=modelo,
        marca=marca,
        ano=random.randint(2015, 2024),
        preco_base_dia=random.choice([80, 100, 120, 150, 180]),
        status="disponivel",
        empresa=random.choice(empresas),
    )
    carros.append(carro)

print("Criando aluguéis sem conflito de datas...")
contador = 0

while contador < 1000:
    carro = random.choice(carros)
    cliente = random.choice(clientes)
    vendedor = random.choice(vendedores)
    empresa = carro.empresa

    # datas válidas
    inicio = date(2024, random.randint(1, 12), random.randint(1, 28))
    fim = inicio + timedelta(days=random.randint(1, 10))

    # verificar conflito de datas para o mesmo carro
    existe_conflito = Aluguel.objects.filter(
        carro=carro,
        data_devolucao_prevista__gte=inicio,
        data_aluguel__lte=fim,
    ).exists()

    if existe_conflito:
        continue

    # cria aluguel
    Aluguel.objects.create(
        data_aluguel=inicio,
        data_devolucao_prevista=fim,
        carro=carro,
        cliente=cliente,
        vendedor=vendedor,
        empresa=empresa,
        valor_total=Decimal("0.00"),
    )

    contador += 1

print("Finalizado com sucesso!")
