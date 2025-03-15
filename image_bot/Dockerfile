FROM python:3.11-buster

RUN pip install poetry

COPY . .

RUN poetry install

CMD ["poetry", "run", "python", "image_bot/main.py"]