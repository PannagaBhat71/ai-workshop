#!/usr/bin/env bash
# Exit on error
set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Seed base question sets & demo users
python manage.py load_aptitude_resource || true
python manage.py seed_demo_data || true

