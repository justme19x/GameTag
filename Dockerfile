
FROM python:3.10


WORKDIR /GAMETAGYT


ENV PYTHONPATH="${PYTHONPATH}:/GAMETAGYT:/GAMETAGYT/backend"


COPY requirements.txt .


RUN pip install -r requirements.txt


COPY . .


EXPOSE 5000


CMD ["gunicorn", "--bind", "0.0.0.0:5000", "backend.app:app"]
