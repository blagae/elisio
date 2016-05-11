# copy this file to Elisio/local.py
# and change database settings at will
DATABASE_SETTINGS = {
    'default' : {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'mydb.db'
        }
    }
ADMIN_LIST = {}
DEBUG_SETTING = True

# replace this with a longer key
# suggestion: http://www.miniwebtool.com/django-secret-key-generator/
KEY = 'abc'