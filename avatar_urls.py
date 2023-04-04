import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
from django.core.files.base import ContentFile

error_count = 0
for obj in User.objects.all():
  try:
    with open(obj.avatar.path, 'rb') as f:
      data = f.read()
      if obj.avatar is not None:
        obj.avatar.save(os.path.basename(obj.avatar.name), ContentFile(data))
        obj.save()
  except Exception as e:
    error_count += 1
    print(e, obj.id)
