import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myProject.settings')
django.setup()

User = get_user_model()

try:
    if User.objects.filter(username='admin').exists():
        u = User.objects.get(username='admin')
        u.set_password('admin')
        u.save()
        print("Updated admin password to 'admin'")
    else:
        User.objects.create_superuser('admin', 'admin@example.com', 'admin')
        print("Created superuser 'admin' with password 'admin'")
except Exception as e:
    print(f"Error: {e}")
