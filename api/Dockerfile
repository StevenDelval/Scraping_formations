FROM python:3.12-slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install -r requirements.txt

COPY . /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]



# docker build -t myimage .
# docker run --rm --env-file .env  -p 8000:8000 -v $(pwd):/app myimage

# -v pour ne pas re build l'image si on fait une modif sur le main.py