# gunicorn_run.py

import os
import sys
from gunicorn.app.wsgiapp import run

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'marketmate.settings')
    gunicorn_args = [
        'gunicorn',
        '--bind', '0.0.0.0:3000', 
        'marketmate.wsgi:application', 
    ]

    sys.argv = gunicorn_args
    sys.exit(run())

if __name__ == '__main__':
    main()
