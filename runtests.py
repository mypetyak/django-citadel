#!/usr/bin/env python
import sys
# from os.path import dirname, abspath
# # from optparse import OptionParser
#
# parent = dirname(abspath(__file__))
# sys.path.insert(0, parent)

from django.conf import settings


def main():
    # Dynamically configure the Django settings with the minimum necessary to
    # get Django running tests.
    KEY_LOCS = {}
    settings.configure(
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.admin',
            'django.contrib.sessions',
        ],
        # Django replaces this, but it still wants it. *shrugs*
        # DATABASE_ENGINE='django.db.backends.sqlite3',
        # DATABASES={
        #     'default': {
        #         'ENGINE': 'django.db.backends.sqlite3',
        #         'NAME': ':memory:',
        #     }
        # },
        DATABASES = {
            'default': {
                'ENGINE':   'django.db.backends.postgresql_psycopg2',
                'NAME':     'belgrade',
                'USER':     'belgrade',
                'PASSWORD': '#4Ug4646EGh1YxG$%ppc',
                'HOST':     'localhost',
                'PORT':     '',
            }
        },
        MEDIA_ROOT='/tmp/django_extensions_test_media/',
        MEDIA_PATH='/media/',
        ROOT_URLCONF='',
        DEBUG=True,
        TEMPLATE_DEBUG=True,
    )

    apps = []
    from django.core.management import call_command
    from django.test.utils import get_runner

    DjangoTestRunner = get_runner(settings)

    class TestRunner(DjangoTestRunner):
        def setup_databases(self, *args, **kwargs):
            result = super(TestRunner, self).setup_databases(*args, **kwargs)
            kwargs = {
                "interactive": False,
                "email": "admin@doesnotexit.com",
                "username": "admin",
            }
            call_command("createsuperuser", **kwargs)
            return result

    failures = TestRunner(verbosity=2, interactive=True).run_tests(apps)
    sys.exit(failures)

if __name__ == '__main__':
    main()