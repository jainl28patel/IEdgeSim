FROM python:3.7.3-alpine3.9

WORKDIR /usr/src/app

COPY . .

ENTRYPOINT  [ "./run.sh" ] 


# ENTRYPOINT ["run.sh"]
# ENTRYPOINT [ "./run.sh" ]
# CMD [ "python", "./broker.py", "&", "python", "./client.py", "&", "python", "./server.py" ]