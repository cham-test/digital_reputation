Для запуска проекта в докере: <br>
  docker-compose -f docker-compose.dev.yml up --build [--detach]  # в скобках опциональный флаг <br>
Для запуска проекта без докер: <br>
  python3 -m venv venv <br>
  source venv/bin/activate <br>
  python manage.py makemigrations --settings=digital_reputation.settings.dev <br>
  python manage.py migrate --settings=digital_reputation.settings.dev <br>
  python manage.py runserver --settings=digital_reputation.settings.dev <br>
