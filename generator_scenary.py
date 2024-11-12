from transformers import pipeline
import torch
import re
import logging
from typing import Optional


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


def format_description(text: str) -> str:
    """Улучшенное форматирование текста"""
    if not text:
        return ""
    
    # Сохраняем сокращения
    abbreviations = {
        "т.д.": "__TD__",
        "т.п.": "__TP__",
        "и т.д.": "__ITD__",
        "и т.п.": "__ITP__"
    }
    
    for abbr, placeholder in abbreviations.items():
        text = text.replace(abbr, placeholder)
    
    # Разбиваем на предложения
    sentences = re.split(r'(?<=[.!?])\s+', text)
    formatted_text = []
    
    for i, sentence in enumerate(sentences):
        # Восстанавливаем сокращения
        for abbr, placeholder in abbreviations.items():
            sentence = sentence.replace(placeholder, abbr)
            
        formatted_text.append(sentence.strip())
        if i > 0 and i % 2 == 0:
            formatted_text.append("\n\n")
    
    return " ".join(formatted_text)


def main(genre: str, theme: str) -> Optional[str]:
    """Основная функция генерации сценария"""
    try:
        description = generate_game_description(genre, theme)
        if not description:
            logging.error("Empty description generated")
            return "Произошла ошибка при генерации сценария. Попробуйте еще раз."
            
        formatted_description = format_description(description)
        return formatted_description

    except ValueError as ve:
        logging.error(f"Validation error in scenario generation: {ve}")
        return "Неверные параметры для генерации сценария."
    except Exception as e:
        logging.error(f"Error in scenario generation: {e}")
        return "Произошла ошибка при генерации сценария. Попробуйте еще раз."


if __name__ == "__main__":
    main()