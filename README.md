Для запуска проекта в докере:
  docker-compose -f docker-compose.dev.yml up --build [--detach]  # в скобках опциональный флаг
Для запуска проекта без докер:
  python3 -m venv venv
  source venv/bin/activate
  python manage.py makemigrations --settings=digital_reputation.settings.dev
  python manage.py migrate --settings=digital_reputation.settings.dev
  python manage.py runserver --settings=digital_reputation.settings.dev
