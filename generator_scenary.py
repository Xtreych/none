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

    try:
        # Генерация и форматирование описания
        description = generate_game_description(genre, theme)
        formatted_description = format_description(description)

        return formatted_description

    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")


if __name__ == "__main__":
    main()