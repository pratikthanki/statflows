FROM ubuntu:xenial

RUN apt-get update && \
    apt-get install -y software-properties-common build-essential python3-pip  nano \
    curl apt-utils apt-transport-https debconf-utils gcc build-essential g++-5

# apt-get and system utilities
RUN apt-get update && apt-get install -y \
    curl apt-utils apt-transport-https debconf-utils gcc build-essential g++-5 \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y tdsodbc unixodbc-dev \
 && apt install unixodbc-bin -y  \
 && apt-get clean -y

# adding custom MS repository
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/ubuntu/16.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

# install SQL Server drivers
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql unixodbc-dev

# install SQL Server tools
RUN apt-get update && ACCEPT_EULA=Y apt-get install -y mssql-tools
RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
RUN /bin/bash -c "source ~/.bashrc"

# python libraries
RUN apt-get update && apt-get install -y \
    python-pip python-dev python-setuptools \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# install necessary locales
RUN apt-get update && apt-get install -y locales \
    && echo "en_US.UTF-8 UTF-8" > /etc/locale.gen \
    && locale-gen
RUN pip install --upgrade pip

# install additional utilities
RUN apt-get update && apt-get install gettext nano vim -y

ADD freetds.conf /etc/freetds/freetds.conf
ADD odbcinst.ini /etc/odbcinst.ini
ADD odbc.ini /home/odbc.ini

COPY ["requirements.txt", "app.py", "nba_settings.py", "teams.py", "court.py", "app_styles.py", "sql_queries.py", "shared_config.py", "shared_modules.py", "assets", "./"]

RUN pip3 install --upgrade pip

# install SQL Server Python SQL Server connector module - pyodbc
RUN pip3 install pyodbc
RUN pip3 install --trusted-host pypi.python.org -r requirements.txt

EXPOSE 8050

CMD ["python3", "app.py"]
