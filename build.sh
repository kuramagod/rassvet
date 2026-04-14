set -o errexit
pip install -r requirements.txt

python manage.py migrate

python manage.py loaddata categories.json || true
python manage.py loaddata products.json || true
python manage.py loaddata characteristics.json || true
python manage.py loaddata news.json || true

python manage.py collectstatic --noinput