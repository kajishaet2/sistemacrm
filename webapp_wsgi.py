import os
import sys

path = '/home/your_username/your_project_folder'
sys.path.insert(0, path)
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
