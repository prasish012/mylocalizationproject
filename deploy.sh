#!/bin/bash
PROJECT_DIR="/root/mylocalizationproject"
VENV_PATH="$PROJECT_DIR/venv/bin/activate"

cd $PROJECT_DIR
source $VENV_PATH

# 1. Ensure absolute imports work
export PYTHONPATH=$PROJECT_DIR

# 2. Kill and restart Gunicorn
pkill -f gunicorn
gunicorn --bind 127.0.0.1:8001 \
  --chdir $PROJECT_DIR \
  --env PYTHONPATH=$PROJECT_DIR \
  --env DJANGO_SETTINGS_MODULE=mylocalizationproject.settings \
  mylocalizationproject.wsgi:application --daemon --timeout 3600

# 3. Restart Nginx
systemctl restart clp-nginx

echo "Engine Restarted! Check wptranslate.org now."
