from Elisio import settings

def set_django():
    """ in order to get to the database, we must use Django """
    import os
    module = 'DJANGO_SETTINGS_MODULE'
    if (not module in os.environ or
            os.environ[module] != settings.__name__):
        os.environ[module] = settings.__name__
    import django
    if django.VERSION[:2] >= (1, 7):
        django.setup()