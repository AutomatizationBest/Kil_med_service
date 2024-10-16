# FROM python:3.11.9-slim

# RUN apt-get update && apt-get install -y firefox-esr xvfb


# # Копирование и установка Python-зависимостей
# COPY requirements.txt requirements.txt
# RUN pip install -r requirements.txt

# # Копирование остальных файлов
# COPY . .

# # Установка прав для ChromeDriver
# # RUN chmod +x /usr/local/bin/chromedriver

# # Команда для запуска приложения
# CMD ["python", "main.py"]

FROM python:3.11.9-slim

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "main.py" ]