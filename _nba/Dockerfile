FROM ubuntu:xenial

RUN apt-get update && \
    apt-get install -y software-properties-common build-essential python3-pip  nano

ADD freetds.conf /etc/freetds/freetds.conf
ADD odbcinst.ini /etc/odbcinst.ini
ADD odbc.ini /home/odbc.ini

RUN apt-get update
RUN apt-get install -y tdsodbc unixodbc-dev
RUN apt install unixodbc-bin -y
RUN apt-get clean

COPY ["requirements.txt", "app.py", "teams.py", "court.py", "app_styles.py", "sql_queries.py", "shared_config.py", "shared_modules.py", "assets", "./"]

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

EXPOSE 8050

CMD ["python3", "app.py"]
