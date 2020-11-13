FROM python:3.8

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

COPY requirments.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirments.txt

COPY . .

#RUN python manage.py makemigrations --no-input --settings digital_reputation.settings.dev
#RUN python manage.py migrate --no-input
#CMD ["uwsgi", "--ini", "uwsgi.ini"]
#CMD ["python", "manage.py", "runserver", "--settings", "digital_reputation.settings.dev"]