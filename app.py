import streamlit as st
from openai import OpenAI

# 1. Настройка пароля (Впишите свой пароль для входа в садике)
CORRECT_PASSWORD = "1234"  

st.set_page_config(page_title="Чат с Лошадкой", layout="centered")

# Проверка авторизации пользователя
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("Вход в систему")
    password = st.text_input("Введите пароль для общения с Лошадкой:", type="password")
    if st.button("Войти"):
        if password == CORRECT_PASSWORD:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Неверный пароль!")
else:
    # Безопасное подключение ключа OpenAI из настроек Streamlit Cloud
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    st.title("🐴 Говорящая Лошадка Звёздочка!")
    st.write("Напиши что-нибудь Лошадке, и она ответит голосом!")

    # Инструкция (системный промпт) для роли говорящей лошади
    system_prompt = (
        "Ты — добрая, веселая говорящая Лошадка по имени Звёздочка. Ты общаешься "
        "с детьми из детского сада (возраст 4-6 лет). Отвечай ОЧЕНЬ коротко (всего 1-2 предложения), "
        "чтобы дети не уставали слушать. Обязательно используй лошадиные звуки: 'Иго-го!', "
        "'Фррр!', '*цокает копытами*'. Задавай детям простые вопросы про их день, друзей или игрушки."
    )

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": system_prompt}]

    # Отображение истории сообщений на экране
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    # Поле ввода сообщения от ребенка или воспитателя
    if user_input := st.chat_input("Скажи что-нибудь Лошадке..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        # Запрос ответа у языковой модели ИИ
        with st.chat_message("assistant"):
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages
            )
            ai_text = response.choices.message.content
            st.write(ai_text)
            st.session_state.messages.append({"role": "assistant", "content": ai_text})
            
            # Генерация аудио-голоса Лошадки (Text-to-Speech)
            with st.spinner("Лошадка говорит..."):
                audio_response = client.audio.speech.create(
                    model="tts-1",
                    voice="nova", # Приятный, мягкий женский/детский голос
                    input=ai_text
                )
                # Автоматическое воспроизведение звука прямо на странице сайта
                st.audio(audio_response.content, format="audio/mp3", autoplay=True)
