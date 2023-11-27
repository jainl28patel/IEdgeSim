FROM python:3.7.3-alpine3.9

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .


# RUN chmod a+x run.sh 
ENTRYPOINT ["./run.sh"]
# CMD [ "run.sh" ]
# CMD [ "python", "./zigbee_server.py", "&", "python", "./zigbee_client.py" ]