#!/usr/bin/env python
import os
import sys

from django.conf import settings

#if __name__ == '__main__':
def run_all():
    # Dynamically configure the Django settings with the minimum necessary to
    # get Django running tests.
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    KEY_LOCS = {}
    settings.configure(
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.admin',
            'django.contrib.sessions',
            'citadel',
            'myapp',
        ],
        DATABASES = {
            'default': {
                'ENGINE':   'django.db.backends.postgresql_psycopg2',
                'NAME':     'citadel_test',
                'USER':     'citadel_test',
                'PASSWORD': 'abcdefghijklmnop',
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

    if os.getenv('BUILD_ON_TRAVIS', None):
        settings.DATABASES['default']['USER'] = 'postgres'
        settings.DATABASES['default']['PASSWORD'] = ''

    apps = ['citadel', 'myapp']
    from django.core.management import call_command
    from django.test.utils import get_runner
    from django import VERSION

    if VERSION[1] >=7:
        from django import setup
        setup()

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
