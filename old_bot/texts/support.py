"""Texts for the help section."""

from __future__ import annotations


def support_text(user_id: int, lang: str = "ru") -> str:
    """Return the help message with a user id."""
    if lang == "en":
        return (
            "❓ <b>Need help?</b>\n\n"
            "📚 We collected answers to the most common questions in the knowledge "
            "base. Take a look — your answer might already be there!\n\n"
            "✋ If not, ask right here in this chat. We are here for you! Or press "
            "the button «✏️ Ask a question».\n\n"
            "Your ID: {user_id}"
        ).format(user_id=user_id)

    return (
        "❓ <b>Нужна помощь?</b>\n\n"
        "📚 Мы собрали ответы на самые частые вопросы в базе знаний. Загляните, "
        "возможно там уже есть то, что вы ищете!\n\n"
        "✋ Если нет, задайте свой вопрос прямо в этом чате. Мы на связи! Или "
        "нажмите кнопку «✏️ Задать вопрос»\n\n"
        "Ваш ID: {user_id}"
    ).format(user_id=user_id)


def ask_question_text(lang: str = "ru") -> str:
    """Return the placeholder text for asking a question."""
    if lang == "en":
        return (
            "✏️ <b>Ask a question</b>\n\n"
            "Write your question right here. We will answer as soon as possible."
        )

    return (
        "✏️ <b>Задать вопрос</b>\n\n"
        "Напишите свой вопрос прямо в этом чате — мы ответим как можно скорее."
    )


def faq_text(lang: str = "ru") -> str:
    """Return the FAQ placeholder text."""
    if lang == "en":
        return "📚 <b>FAQ</b>\n\nFAQ will be added soon."

    return "📚 <b>FAQ</b>\n\nFAQ будет добавлен в ближайшее время."
