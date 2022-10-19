import os
import shutil

import django
from django.core import management

from coolNewLanguage.src.util import ImportUtils

DJANGO_STARTPROJECT = 'django-admin startproject {}'
DJANGO_SETTINGS_MODULE = 'DJANGO_SETTINGS_MODULE'


class Tool:
    def __init__(self, *modules, **kwargs):
        if 'tool_name' in kwargs:
            self.tool_name = kwargs['tool_name']
        else:
            self.tool_name = 'tool'

        for module in modules:
            module.tool = self
        self.modules = modules

        self.project_started = False
        self.start_project()

    def run(self):
        if not self.project_started:
            self.start_project()

        management.call_command('runserver', 'localhost:8000', '--noreload')

    def render(self):
        # add default method to views
        views_module = ImportUtils.import_django_module(f'{self.tool_name}.views')
        setattr(views_module, 'default_response', "")
        setattr(
            views_module,
            'default',
            lambda request: django.http.HttpResponse(getattr(views_module, 'default_response'))
        )
        # add path to urls
        urls_module = ImportUtils.import_django_module(f'{self.tool_name}.urls', invalidate_caches=False)
        urls_module.urlpatterns.append(django.urls.path('', views_module.default))

        if self.modules == ():
            setattr(views_module, 'default_response', "This is an empty tool.")
            return
        for module in self.modules:
            module.render()

    def start_project(self):
        if self.project_started:
            return

        formatted_startproject = DJANGO_STARTPROJECT.format(self.tool_name)
        os.system(formatted_startproject)

        # move django project files into same level as working directory
        shutil.move(f'./{self.tool_name}/manage.py', './manage.py')
        django_file_root = f'./{self.tool_name}'
        django_project_file_root = os.path.join(django_file_root, self.tool_name)
        for f in os.listdir(os.path.join(django_file_root, self.tool_name)):
            shutil.move(os.path.join(django_project_file_root, f), os.path.join(django_file_root, f))
        os.rmdir(django_project_file_root)

        # set DJANGO_SETTINGS_MODULE in env to use management.call_command
        # path is specific to directory we're running from
        django_settings_val = f'{self.tool_name}.settings'
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', django_settings_val)
        django.setup()

        # apply migrations so django server can be run
        management.call_command('migrate')

        # create views file
        open(os.path.join('.', self.tool_name, 'views.py'), 'x')

        self.project_started = True
