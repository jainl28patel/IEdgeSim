FROM python:3.7.3-alpine3.9

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./coap_server.py", "&&", "python", "./coap_client.py" ]