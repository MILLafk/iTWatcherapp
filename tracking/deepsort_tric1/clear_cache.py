import os
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_name.settings')
settings.configure()

# Now you can use Django modules, including cache-related code
from django.core.cache import cache

# Clear all cache entries
cache.clear()
