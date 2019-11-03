FROM python:3.7-slim

# install FreeTDS
RUN apt-get update
RUN apt-get install unixodbc -y
RUN apt-get install unixodbc-dev -y
RUN apt-get install freetds-dev -y
RUN apt-get install freetds-bin -y
RUN apt-get install tdsodbc -y
RUN apt-get install --reinstall build-essential -y

# populate "odbcinst.ini"
RUN echo "[FreeTDS]\n\
Description = FreeTDS unixODBC Driver\n\
Driver = /usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so\n\
Setup = /usr/lib/x86_64-linux-gnu/odbc/libtdsS.so" >> /etc/odbcinst.ini

COPY ["requirements.txt", "app.py", "nba_settings.py", "teams.py", "court.py", "app_styles.py", "sql_queries.py", "shared_config.py", "shared_modules.py", "assets", "./"]

RUN pip install --upgrade pip
RUN pip install pyodbc
RUN pip install -r requirements.txt

EXPOSE 8050

CMD ["python3", "app.py"]
