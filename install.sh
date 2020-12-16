#!/bin/bash
git pull
sudo apt-get update
sudo apt-get -y install python3 python3-pip nginx libpq-dev
pip3 install virtualenv
export PATH="$HOME/.local/bin:$PATH"
virtualenv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py collectstatic --noinput
sudo cp server_config/gunicorn/gunicorn.config /etc/systemd/system/gunicorn.service
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl restart gunicorn
sudo cp server_config/nginx/sites-available/hipo-exercise /etc/nginx/sites-available/hipo-exercise
sudo ln -s /etc/nginx/sites-available/hipo-exercise /etc/nginx/sites-enabled
sudo cp server_config/nginx/nginx.conf /etc/nginx/nginx.conf
sudo systemctl enable nginx
sudo systemctl restart nginx
