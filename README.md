📝 NotesAI

NotesAI — веб-приложение для управления задачами с поддержкой искусственного интеллекта.
Создавай, выполняй, удаляй задачи и получай персонализированные советы от AI по их эффективному выполнению.

⚠️ Проект находится в разработке, некоторые функции будут улучшены в будущем.

⸻

🚀 Основные функции

🔑 Аутентификация пользователей

Вход через логин с безопасной аутентификацией (JWT + secure cookies)

📝 Управление задачами
	•	Создание новых задач
	•	Просмотр списка задач
	•	Отметка задачи как выполненной
	•	Удаление задач

🤖 AI Advice
	•	Анализирует задачи пользователя
	•	Выдаёт конкретные советы по выполнению задач


⸻

💻 Технологии
	•	Backend: FastAPI, SQLAlchemy, PostgreSQL
	•	Frontend: приватно
	•	AI-сервис: анализ задач и генерация рекомендаций
	•	Безопасность: хеширование паролей, JWT access + refresh токены, secure cookies

⸻

📂 Структура проекта

<pre>

notesai/
├── api/                     # Основные маршруты и точка входа backend
│   ├── routers/             # Файлы с маршрутизаторами для разных endpoint
│   ├── __init__.py
│   ├── dependencies.py      # Общие зависимости для FastAPI (DB, Auth и т.д.)
│   └── main.py              # Запуск FastAPI приложения
│
├── core/                    # Конфигурация и базовые сервисы
│   ├── __init__.py
│   ├── config.py            # Настройки приложения (env, секреты)
│   ├── database.py          # Подключение и управление БД
│   ├── openai_client.py     # Класс для работы с OpenAI API
│   └── security.py          # JWT, хеширование паролей, secure cookies
│
├── services/                # Бизнес-логика приложения
│   ├── ai_service.py        # Логика анализа задач и генерации AI советов
│   └── __init__.py
│
├── main.py                  # Основной запуск backend (если без api/main)
├── models.py                # SQLAlchemy модели
├── schemas.py               # Pydantic схемы для валидации данных
├── compose.yaml             # Docker Compose конфигурация
├── .env                     # Переменные окружения
├── .gitignore
├── alembic.ini              # Настройки миграций Alembic
├── README.md
└── requirements.txt

</pre>


⸻

🛠 Установка и запуск (локально)
	1.	Клонируем репозиторий:

git clone https://github.com/AzatSE/NotesAI.git
cd NotesAI

	2.	Создаём виртуальное окружение:

python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

	3.	Устанавливаем зависимости:

pip install -r requirements.txt

	4.	Настраиваем переменные окружения для БД и JWT.
	5.	Запускаем сервер:

fastapi dev

	6.	Переходим в браузере на:

http://127.0.0.1:8000/docs


⸻