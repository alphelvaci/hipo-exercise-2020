#!/bin/bash
while :;do echo -e '.\c';sleep 1;done &
trap "kill $!" EXIT
echo -e 'Installing\c'
git pull > /dev/null 2>&1
sudo apt-get update > /dev/null 2>&1
sudo apt-get -y install python3 python3-pip nginx libpq-dev > /dev/null 2>&1
pip3 install virtualenv > /dev/null 2>&1
export PATH="$HOME/.local/bin:$PATH" > /dev/null 2>&1
virtualenv .venv > /dev/null 2>&1
source .venv/bin/activate > /dev/null 2>&1
pip3 install -r requirements.txt > /dev/null 2>&1
python3 manage.py makemigrations > /dev/null 2>&1
python3 manage.py migrate > /dev/null 2>&1
python3 manage.py collectstatic --noinput > /dev/null 2>&1
sudo cp server_config/gunicorn/gunicorn.config /etc/systemd/system/gunicorn.service > /dev/null 2>&1
sudo systemctl daemon-reload > /dev/null 2>&1
sudo systemctl enable gunicorn > /dev/null 2>&1
sudo systemctl restart gunicorn > /dev/null 2>&1
sudo cp server_config/nginx/sites-available/hipo-exercise /etc/nginx/sites-available/hipo-exercise > /dev/null 2>&1
sudo ln -s /etc/nginx/sites-available/hipo-exercise /etc/nginx/sites-enabled > /dev/null 2>&1
sudo cp server_config/nginx/nginx.conf /etc/nginx/nginx.conf > /dev/null 2>&1
sudo systemctl enable nginx > /dev/null 2>&1
sudo systemctl restart nginx > /dev/null 2>&1;
echo 'Done'
kill $! && trap " " EXIT