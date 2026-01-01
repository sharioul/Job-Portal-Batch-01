import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myProject.settings')
django.setup()

from myApp.models import MessageModel

print("Checking MessageModel objects...")
messages = MessageModel.objects.all()
print(f"Total messages: {messages.count()}")

for msg in messages:
    print(f"ID: {msg.id}, Sender: {msg.sender}, Timestamp: {msg.timestamp}, Type: {type(msg.timestamp)}")
