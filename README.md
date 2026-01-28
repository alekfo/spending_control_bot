# Название проекта
Чат-бот "Отдел логистики VooMoo "
🤖 Telegram-bot: @voomoo_spending_control_bot

 [Свяжитесь с нашим ботом:](https://t.me/voomoo_spending_control_bot)

 Ссылка на репозиторий: https://github.com/alekfo/spending_control_bot/tree/origin

# Описание прокта
Данный чат-бот дает возможность контроля расходов сотрудников отдела логистики

# Возможности

-  👤Регистрация пользователей
-  🔄2 режима работы бота:
  - режим "Для администратора"
  - режим "Для сотрудника"
- 👨‍👩‍👧в режиме "Для сотрудника":
  - просмотр своих расходов за выбранный месяц
  - добавление расхода
- 👑в режиме "Для администратора":
  - просмотр всех зарегистрированных сотрудников
  - просмотр рассходов выбранного сотрудника за выбранный месяц
  - синхронизизация данных из базы с Google-таблицей
  - переход на Google-таблицу по ссылке
- 💾хранение данных в базе

# Основные технологии
## Python (aiogram)
```
Использумые библиотеки в файле requirements.txt
База данных: SQLite (sqlalchemy)
```

## Docker
Сборка образа и запуск контейнера описаны ниже

# Установка и запуск

### Клонирование репозитория
```markdown
bash
git clone https://github.com/alekfo/spending_control_bot.git
cd spending_control_bot
```

### Установка зависимостей
```markdown
bash
pip install -r requirements.txt
```

### Настройка переменных окружения
Создайте файл .env по существующему шаблону .env.template и добавьте:

```
BOT_TOKEN=YOUR_BOT_TOKEN
ADMIN_ID=YOUR_ADMIN_ID
# 1. Укажите путь к вашему credentials.json (получите на сайте https://console.cloud.google.com/) для работы google_sheets
SERVICE_ACCOUNT_FILE=YOURSERVICE_ACCOUNT_FILE
# 2. Укажите ID вашей таблицы (из URL таблицы)
SPREADSHEET_ID=your_SPREADSHEET_ID
```

### Запуск проекта через консоль
```markdown
bash
cd ourlogopedbot
python main.py
```

### Сборка контейнера Docker
В проекте уже собраны Dockerfile и docker-compose.yml. Для сборки образа docker и запуска контейнера необходимо указать путь до файла с базой данных
на вашем локальном устройстве заменив строку '- "/home/vboxuser/PycharmProjects/spending_control_bot/data:/app/data"' на ваш путь.
Для сборки образа и запуска контейнера:
```
bash
cd spending_control_bot
docker compose up -d
```

# Использование

### Основные команды
Для запуска диалога с ботом достаточно отправить любое сообщение и следовать инструкциям от бота или отправить команду /start

### Пример использования:
1. [Приветствие нового сотрудника](screenshots\greeting.png)
2. [Регистрация сотрудника](screenshots\registration.png)
3. [Уведомление админа о новом сотруднике с кнопками подтверждения/отказа](screenshots\new_employee_alarm.png)
4. [Подтверждение регистрации у сотрудника](screenshots\confirmed.png)
5. [Главное меню сотрудника](screenshots\employees_main_menu.png)
6. [Просмотр своих расходов сотрудника за выбранный месяц](screenshots\show_spending.png)
7. [Добавление расхода](screenshots\adding_spending.png) 
8. [Главное меню админа](screenshots\admins_main_menu.png)
9. [Просмотр всех зарегистрированных сотрудников](screenshots\employees_list.png)
10. [Просмотр расхода сотрудника за выбранный месяц](screenshots\get_employees_spendings.png)
11. [Синхронизация Google-таблицы](screenshots\sync.png)
12. [Ссылка на гугл таблицу Google-таблицы](screenshots\link.png)

# Автор
Шленсков Алексей



