from rest_framework.pagination import PageNumberPagination

class FiveResultsPagination(PageNumberPagination):
    """
    Paginação personalizada: 5 itens por página por padrão.
    Permite ?page_size=N (até max_page_size) se necessário.
    """
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50