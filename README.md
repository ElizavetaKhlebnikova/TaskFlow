# TaskFlow

TaskFlow — REST API для командной работы над проектами. В нём можно добавлять участников, назначать задачи, отслеживать их статус и обсуждать работу в комментариях.

- Проекты с ролями `manager` и `member`. Создатель проекта автоматически становится его владельцем и менеджером.
- Задачи с исполнителем, приоритетом и сроком. Исполнителя можно выбрать из участников проекта.
- Комментарии к задачам и история изменений задач.
- Поиск проектов по названию и фильтрация задач по статусу, приоритету и исполнителю.
- Аутентификация по JWT и управление пользователями через Django Admin.

Стек — Python 3.12+, Django 6.1, Django REST Framework, PostgreSQL, Simple JWT и django-reversion. Тесты используют pytest и pytest-django.

## Локальный запуск

Понадобятся Python 3.12 или новее и запущенный PostgreSQL. Выполняйте команды из корня проекта, где лежит `requirements.txt`.

### 1. Установите зависимости

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

В Windows PowerShell для активации окружения используйте `.\.venv\Scripts\Activate.ps1`.

### 2. Настройте базу данных

Создайте базу PostgreSQL и роль с правами владельца этой базы. Например, выполните от имени администратора PostgreSQL:

```sql
CREATE ROLE taskflow LOGIN PASSWORD 'replace-with-local-password';
CREATE DATABASE taskflow OWNER taskflow;
```

Сгенерируйте секретный ключ Django:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Создайте файл `taskflow/.env` рядом с `manage.py` и подставьте свой ключ и параметры подключения.

```dotenv
SECRET_KEY='вставьте-сгенерированный-ключ'
DEBUG=True
DB_NAME=taskflow
DB_USER=taskflow
DB_PASSWORD=replace-with-local-password
DB_HOST=127.0.0.1
DB_PORT=5432
```

`DEBUG=True` включает режим локальной разработки.

### 3. Запустите приложение

```bash
cd taskflow
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

API доступен по адресу `http://127.0.0.1:8000/api/`, админка — по адресу `http://127.0.0.1:8000/admin/`. Через админку можно создать дополнительные учётные записи и затем добавить их в проект через API.

## Работа с API

### Получение токена

Передайте имя пользователя и пароль, заданные при создании учётной записи.

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H 'Content-Type: application/json' \
  -d '{"username":"YOUR_USERNAME","password":"YOUR_PASSWORD"}'
```

Ответ содержит `access` и `refresh`. Токен `access` действует 60 минут. Чтобы получить новый `access`, отправьте `POST /api/refresh_token/` с JSON-телом `{"refresh":"YOUR_REFRESH_TOKEN"}`. Токен `refresh` действует два дня.

### Создание проекта и задачи

Подставьте значение `access` в переменную `ACCESS_TOKEN`.

```bash
ACCESS_TOKEN='YOUR_ACCESS_TOKEN'

curl -X POST http://127.0.0.1:8000/api/projects/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"name":"Подготовка релиза"}'
```

Возьмите `id` проекта из ответа и подставьте его вместо `1` в поле `project`.

```bash
curl -X POST http://127.0.0.1:8000/api/task/ \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{"project":1,"name":"Проверить миграции","status":"todo","priority":"high"}'
```

Для списка задач этого проекта отправьте `GET /api/task/?project=1` с тем же заголовком авторизации.

### Маршруты

| Ресурс | Метод и путь | Назначение |
| --- | --- | --- |
| Проекты | `GET`, `POST` `/api/projects/` | Список своих проектов и создание проекта |
| Проект | `GET`, `PUT`, `PATCH`, `DELETE` `/api/projects/{id}/` | Просмотр, изменение и удаление проекта |
| Участники | `GET /api/project-members/?project={id}` | Список участников проекта |
| Участники | `POST /api/project-members/` | Добавление пользователя в проект |
| Участник | `PATCH`, `DELETE` `/api/project-members/{id}/` | Изменение роли и удаление участника |
| Задачи | `GET /api/task/?project={id}` | Список задач проекта |
| Задачи | `POST /api/task/` | Создание задачи |
| Задача | `PATCH`, `DELETE` `/api/task/{id}/` | Изменение и удаление задачи |
| История задачи | `GET /api/task/{id}/history/` | Сохранённые версии задачи |
| Комментарии | `GET /api/comments/?task={id}` | Список комментариев к задаче |
| Комментарии | `POST /api/comments/` | Добавление комментария |
| Комментарий | `PATCH`, `DELETE` `/api/comments/{id}/` | Изменение и удаление комментария |

В маршрутах `/api/project-members/{id}/` и `/api/comments/{id}/` указывайте ID записи об участии и ID комментария соответственно.

При запросе списка проектов доступны `search` для поиска по названию, `role` для фильтрации по своей роли и `ordering` для сортировки по `name` или `updated_at`. Например, `GET /api/projects/?role=manager&ordering=-updated_at`.

В списке задач параметр `project` обязателен. Дополнительно можно передать `status`, `priority` и `assignee` (ID пользователя).

- Статусы задач — `planned`, `todo`, `in_progress`, `done`.
- Приоритеты — `low`, `medium`, `high`.

## Тесты

Запускайте тесты из каталога `taskflow/`, где находятся `manage.py` и `pytest.ini`.

```bash
python -m pytest
```

Pytest использует настройки проекта и создаёт отдельную тестовую базу PostgreSQL. Роли из `DB_USER` нужны права на создание базы данных для тестов (`CREATEDB`).

## Структура проекта

```text
TaskFlow/
├── requirements.txt
└── taskflow/
    ├── manage.py
    ├── pytest.ini
    ├── api/        # Маршруты REST API
    ├── project/    # Проекты и права доступа к ним
    ├── task/       # Задачи, комментарии и история изменений
    ├── user/       # Участники проектов и их роли
    └── taskflow/   # Настройки Django и корневые маршруты
```