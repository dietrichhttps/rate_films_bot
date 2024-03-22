import requests


def shorten_url(long_url: str) -> str:
    try:
        response = requests.get(
            f'http://tinyurl.com/api-create.php?url={long_url}')
        if response.status_code == 200:
            return response.text
    except Exception as e:
        print(f"Error occurred while shortening URL: {e}")
    return long_url  # Возвращаем исходную URL в случае ошибки
