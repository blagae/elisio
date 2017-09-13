from Elisio import local, settings


def set_django():
    """ in order to get to the database, we must use Django """
    import pymysql
    pymysql.install_as_MySQLdb()
    import os
    module = 'DJANGO_SETTINGS_MODULE'
    if module not in os.environ or os.environ[module] != settings.__name__:
        os.environ[module] = settings.__name__
    import django
    if django.VERSION[:2] >= (1, 7):
        django.setup()


def recreate_db():
    if "psycopg2" in local.DATABASE_SETTINGS['default']['ENGINE']:
        import psycopg2
        # http://stackoverflow.com/q/22357856
        with psycopg2.connect(database="postgres", user="postgres", password=local.DB_SUPERUSER_PASSWORD) as conn:
            with conn.cursor() as cur:
                # Explains why we do this - we cannot drop or create from within a DB transaction.
                # http://initd.org/psycopg/docs/connection.html#connection.autocommit
                conn.autocommit = True
                try:
                    cur.execute("DROP DATABASE " + local.DATABASE_SETTINGS['default']['NAME'])
                except psycopg2.ProgrammingError:
                    pass
                cur.execute("CREATE DATABASE " + local.DATABASE_SETTINGS['default']['NAME'] + " WITH OWNER " +
                            local.DATABASE_SETTINGS['default']['USER'])
    set_django()
    from django.core.management import call_command
    call_command('migrate')


def get_commit():
    import subprocess
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD'], shell=True)[:39]
    except subprocess.CalledProcessError:
        return "could not find git commit"
