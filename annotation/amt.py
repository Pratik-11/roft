# Generates users with random username/password and exports to CSV

import sys
import os
import uuid
import csv
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE','trick.settings')
django.setup()
from core.models import User

n_users = int(sys.argv[1])
users = set()

with open('users.csv', 'w') as f:
    writer = csv.writer(f, quoting=csv.QUOTE_ALL)
    writer.writerow(['username', 'password'])

    for _ in range(n_users):
        username, password = uuid.uuid4().hex, uuid.uuid4().hex 
        user = User.objects.create_user(username=username, password=password, email=None)
        users.add(user)

        writer.writerow([username, password])