# Fix for django-q Compatibility Issue

## Problem
`django-q` 1.3.9 is not compatible with Django 5.x because it tries to import `django.utils.baseconv` which was removed in Django 5.0.

## Solution Options

### Option 1: Use django-q2 (Recommended)
`django-q2` is a maintained fork that supports Django 5.x:

```bash
pip uninstall django-q
pip install django-q2
```

Then update `settings.py` - the configuration remains the same, just change the app name:
```python
INSTALLED_APPS = [
    # ... other apps ...
    'django_q2',  # Changed from 'django_q'
]
```

### Option 2: Downgrade Django (Not Recommended)
If you must use django-q 1.3.9, downgrade Django to 4.2 LTS:

```bash
pip install "Django>=4.2,<5.0"
```

### Option 3: Manual Patch (Temporary Fix)
You can manually patch the django-q source code, but this is not recommended for production:

1. Find the django-q installation location:
```bash
python -c "import django_q; print(django_q.__file__)"
```

2. Edit `django_q/core_signing.py` and replace:
```python
from django.utils import baseconv
```
with:
```python
try:
    from django.utils import baseconv
except ImportError:
    # Django 5.0+ removed baseconv, use base64 instead
    import base64
    import string
    
    class baseconv:
        # Simple base36 implementation
        BASE36_ALPHABET = string.digits + string.ascii_lowercase
        
        @staticmethod
        def base36_to_int(s):
            return int(s, 36)
        
        @staticmethod
        def int_to_base36(i):
            if i < 0:
                raise ValueError("Negative base36 conversion input.")
            if i < 36:
                return baseconv.BASE36_ALPHABET[i]
            s = ''
            while i != 0:
                i, n = divmod(i, 36)
                s = baseconv.BASE36_ALPHABET[n] + s
            return s or '0'
```

**Note:** This is a workaround and may not work for all django-q features.

## Recommended Action
Use **Option 1** (django-q2) as it's the most reliable solution for Django 5.x compatibility.

