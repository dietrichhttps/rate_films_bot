import wikipedia
import difflib

from services.link_service import shorten_url


def search_films(query: str, max_results: int = 10) -> dict[str, str] | None:
    wikipedia.set_lang('ru')

    # Используем функцию wikipedia.search для поиска страниц по запросу
    search_results = wikipedia.search(query, results=max_results)

    # Создаем словарь для хранения результатов поиска
    suggestions: dict[str, str] = {}

    # Перебираем результаты поиска и получаем ссылки на страницы Википедии
    if search_results:
        for title in search_results:
            if query.lower() == title.lower():
                page = wikipedia.page(title)
                suggestions[page.title] = shorten_url(page.url)
            # Если нет полного соответствия, проверяем
            # на схожесть с помощью difflib
            elif difflib.SequenceMatcher(
                    None, query.lower(), title.lower()).ratio() > 0.9:
                page = wikipedia.page(title)
                suggestions[page.title] = shorten_url(page.url)
            elif query in title and '(фильм,' in title:
                page = wikipedia.page(title)
                suggestions[page.title] = shorten_url(page.url)

        return suggestions
