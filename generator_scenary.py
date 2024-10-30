<<<<<<< HEAD
from transformers import pipeline
import torch
import re


def generate_game_description(genre, theme):
    # Инициализация генератора текста с русскоязычной моделью
    generator = pipeline('text-generation',
                         model='sberbank-ai/rugpt3small_based_on_gpt2',
                         device=0 if torch.cuda.is_available() else -1)

    # Расширенный промпт с четкими инструкциями и ограничениями
    prompt = f"""
    Создай иммерсивную историю локации и ситуации для текстовой ролевой игры для двух участников.
    Следуй этим правилам:
    - Не используй ссылки на источники
    - Не упоминай авторов и правообладателей
    - Не добавляй метаинформацию
    - Обязательно учитывай что участников текстовой ролевой игры двое
    - Будь максимально креативен в создании

    Жанр: {genre}
    Тема: {theme}

    Вы находитесь в месте, где
    """

    try:
        # Генерация описания с настроенными параметрами
        result = generator(prompt,
                           max_length=250,
                           num_return_sequences=1,
                           temperature=0.7,
                           do_sample=True,
                           no_repeat_ngram_size=3,
                           top_k=50,
                           top_p=0.9,
                           repetition_penalty=1.2)

        # Обработка результата
        generated_text = result[0]['generated_text']

        # Извлечение только описания, удаление промпта и инструкций
        clean_text = generated_text.split("Вы находитесь в месте, где")[-1].strip()

        # Очистка от нежелательного контента
        clean_text = re.sub(r'\[.*?\]', '', clean_text)  # Удаление текста в скобках
        clean_text = re.sub(r'\(.*?\)', '', clean_text)
        clean_text = re.sub(r'http\S+', '', clean_text)
        clean_text = re.sub(r'источник:.*', '', clean_text, flags=re.IGNORECASE)
        clean_text = re.sub(r'автор:.*', '', clean_text, flags=re.IGNORECASE)
        clean_text = re.sub(r'правообладатель:.*', '', clean_text, flags=re.IGNORECASE)
        clean_text = re.sub(r'игрок.*?:', '', clean_text, flags=re.IGNORECASE)

        # Замена некоторых шаблонных фраз
        clean_text = clean_text.replace("В этой игре", "")
        clean_text = clean_text.replace("В данной игре", "")
        clean_text = clean_text.replace("В игре", "")

        return "Вы находитесь в месте, где " + clean_text

    except Exception as e:
        return f"Произошла ошибка при генерации текста: {str(e)}"


def format_description(text):
    """Форматирование текста для лучшей читаемости"""
    # Очистка от множественных пробелов и переносов строк
    text = re.sub(r'\s+', ' ', text).strip()

    # Разделение на предложения с учётом сокращений
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)

    formatted_text = ''
    for i, sentence in enumerate(sentences):
        if i > 0 and i % 2 == 0:  # Новый абзац каждые два предложения
            formatted_text += '\n\n'
        formatted_text += sentence.strip() + ' '

    return formatted_text.strip()


def main(genre, theme):
    try:
        description = generate_game_description(genre, theme)
        formatted_description = format_description(description)

        return formatted_description
    except Exception as e:
        return f"Произошла ошибка: {str(e)}"


if __name__ == "__main__":
=======
from transformers import pipeline
import torch
import re


def generate_game_description(genre, theme):
    # Инициализация генератора текста с русскоязычной моделью
    generator = pipeline('text-generation',
                         model='sberbank-ai/rugpt3small_based_on_gpt2',
                         device=0 if torch.cuda.is_available() else -1)

    # Формирование промпта на русском языке
    prompt = f"""
    Жанр: {genre}
    Тема: {theme}

    Описание игровой обстановки и текущей ситуации:
    Вы находитесь в мире, где
    """

    try:
        # Генерация описания
        result = generator(prompt,
                           max_length=250,
                           num_return_sequences=1,
                           temperature=0.8,
                           do_sample=True,
                           no_repeat_ngram_size=2)

        # Обработка результата
        generated_text = result[0]['generated_text']
        # Очистка от лишних пробелов и форматирование
        generated_text = re.sub(r'\s+', ' ', generated_text).strip()
        return generated_text

    except Exception as e:
        return f"Произошла ошибка при генерации текста: {str(e)}"


def format_description(text):
    """Форматирование текста для лучшей читаемости"""
    paragraphs = text.split('. ')
    formatted_text = ''
    for i, paragraph in enumerate(paragraphs):
        if i > 0 and i % 2 == 0:  # Каждые два предложения - новый абзац
            formatted_text += '\n\n'
        formatted_text += paragraph.strip() + '. '
    return formatted_text


def main(genre, theme):
    #print("Генератор сцен для ролевой игры")
    #print("=" * 40)

    # Словарь подсказок для жанров
    #genre_hints = """
    #Доступные жанры:
    #- Фэнтези
    #- Научная фантастика
    #- Постапокалипсис
    #- Киберпанк
    #- Стимпанк
    #- Ужасы
    #- Детектив
    #"""

    #print(genre_hints)

    # Получение входных данных
    # while True:
    #     genre = input("\nВведите жанр: ").strip()
    #     if genre:
    #         break
    #     print("Жанр не может быть пустым!")
    #
    # while True:
    #     theme = input("Введите тему или сеттинг: ").strip()
    #     if theme:
    #         break
    #     print("Тема не может быть пустой!")
    #
    # print("\nГенерация описания...")
    # print("-" * 40)

    try:
        # Генерация и форматирование описания
        description = generate_game_description(genre, theme)
        formatted_description = format_description(description)

        #print("\nСгенерированное описание сцены:")
        #print("=" * 40)
        #print(formatted_description)
        return formatted_description

    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")


if __name__ == "__main__":
>>>>>>> origin/main
    main()