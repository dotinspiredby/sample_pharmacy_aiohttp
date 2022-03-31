FROM python:3.9

# Просим Python не писать .pyc файлы
ENV PYTHONDONTWRITEBYTECODE 1

# Просим Python не буферизовать stdin/stdout
ENV PYTHONUNBUFFERED 1

WORKDIR /web_app/pharmasys

COPY ./requirements.txt /web_app/pharmasys/requirements.txt

RUN pip install -r /web_app/pharmasys/requirements.txt

COPY . /web_app/pharmasys/

EXPOSE 8080

CMD ["python", "main.py"]