from django.core.management.base import BaseCommand, CommandError
from django.apps import apps
from django.core.exceptions import ImproperlyConfigured
from citadel.fields import SecretField

class Command(BaseCommand):
    args = '<sub_command>'
    help = 'test'
    requires_system_checks = True
    can_import_settings = True

    def handle(self, *args, **options):
        try:
            sub = args[0]
            app_name = args[1]
        except IndexError:
            raise CommandError('Incorrect subcommand - please see \'citadel_upgrade --help\'')

        if sub == 'work_factor':
            from django.db.models import get_app, get_models
            try:
                app = apps.get_app_config(app_name)
            except ImproperlyConfigured:
               raise CommandError('App %s does not exist!' % app_name) 

            for name, model in app.models.iteritems():
                #@TODO: Django 1.8 supports _meta.get_fields()
                fields = model._meta.fields
                for field in [field for field in fields if type(field) is SecretField]:
                    for instance in model.objects.all():
                        print 'instance: ' + repr(instance)
                        print 'field: ' + repr(field)
                        secret = getattr(instance, field.name)
                        #secret = instance.field
                        print 'workfactor: ' + repr(secret.get_work_factor())

        self.stdout.write('Done')
