FROM python:3.10-slim

WORKDIR /backend

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN chown -R www-data:www-data /tmp && chown -R www-data:www-data /var/log

COPY ./requirements.txt ./requirements.txt

#  Удалена установка rsyslog, потому что он пакет python:3.10
#  использует Debian 12, в котором система логирования заменена
#  на sysmtemd-journald

RUN apt-get update \
    && apt-get install -y vim build-essential cron \
    && pip install -r /backend/requirements.txt \
    && rm -rf /var/lib/apt/lists/*

COPY . .

#  Копируем cron файл в /etc/cron.d/
#  Данный скрипт копирует переменные окружения в файл
#  /etc/security/pam_env.conf чтобы CRON мог иметь
#  такие же переменные окружения
#  Делаем скрипт исполняемым
RUN cp /backend/cron/backend_cron_tasks /etc/cron.d/backend_cron_tasks \
    && chmod +x /backend/cron/docker-entrypoint.sh