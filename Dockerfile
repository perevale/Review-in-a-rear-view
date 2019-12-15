FROM python:3

ADD app.py /

RUN pip install flask
RUN pip install flask_restplus
RUN pip install IMDbPY
RUN pip install requests

CMD [ "python", "./app.py" ]