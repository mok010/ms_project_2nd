FROM mcr.microsoft.com/azure-functions/python:4-python3.11

# 필수 패키지만 설치 (500MB 절약)
RUN apt-get update && apt-get install -y \
    unixodbc-dev \
    curl \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Microsoft ODBC Driver (간소화된 방법)
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    echo "deb [arch=amd64] https://packages.microsoft.com/debian/12/prod bookworm main" > /etc/apt/sources.list.d/mssql-release.list && \
    apt-get update && \
    ACCEPT_EULA=Y apt-get install -y msodbcsql18 --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Python 패키지 (pre-compiled wheel 사용)
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir --only-binary=all -r /tmp/requirements.txt

# 앱 복사
COPY . /home/site/wwwroot
WORKDIR /home/site/wwwroot

ENV AzureWebJobsScriptRoot=/home/site/wwwroot