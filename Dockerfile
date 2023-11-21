FROM python:3.9-alpine
WORKDIR /app
COPY requirements.txt ./
RUN pip3 install -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 7777/tcp
CMD ["python3","server.py"]