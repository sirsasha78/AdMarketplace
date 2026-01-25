from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """Пользовательская пагинация для управления постраничным выводом данных.
    Этот класс наследуется от `PageNumberPagination` и позволяет клиенту API
    самому выбирать количество элементов на странице с помощью параметра `page_size`
    в URL-запросе. Установлено ограничение на максимальное количество элементов,
    чтобы предотвратить слишком большие ответы и нагрузку на сервер."""

    page_size_query_param = "page_size"
    max_page_size = 100
