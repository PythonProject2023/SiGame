DOIT_CONFIG = {'default_tasks': ['test', 'docs', 'locale', 'dist']}

def task_test():
    return {
        'actions': ['python -m unittest test.py'],
        'file_dep': ['test.py'],
        'verbosity': 2,
    }

def task_docs():
    return {
        'actions': ['cd docs && make html'],
        'file_dep': ['docs/source/server_documentation.rst',
                     'docs/source/parser_documentation.rst',
                     'docs/source/index.rst',
                     'docs/source/app_documentation.rst'],
        'targets': ['docs/_build/html/index.html'],
        'verbosity': 2,
    }

def task_dist():
    return {
        'actions': ['python -m build -n -w'],
        'file_dep': ['pyproject.toml', 'Pipfile', 'Pipfile.lock', 'README.md', './sigame/server.py', 
                     './sigame/parser.py', './sigame/__init__.py', './sigame/app.py', 
                     './sigame/utils/generate_translation.py', './sigame/__main__.py'],
        'targets': ['dist/*.whl'],
        'verbosity': 2,
    }


def task_locale():
    return {
        'actions': ['cd sigame && python utils/generate_translation.py', 'cd ..', 'pybabel compile -d sigame/locale -D myapp'],
        'file_dep': ['./sigame/locale/en/LC_MESSAGES/myapp.po', './sigame/locale/ru/LC_MESSAGES/myapp.po'],
        'targets': ['./sigame/locale/en/LC_MESSAGES/myapp.mo', './sigame/locale/ru/LC_MESSAGES/myapp.mo'],
        'verbosity': 2,
    }


# def task_style():
#     return {
#         'actions': ['pycodestyle .', 'flake8 .'],
#         'file_dep': ['pyproject.toml', 'Pipfile', 'Pipfile.lock', 'README.md', './sigame/server.py', 
#                      './sigame/parser.py', './sigame/__init__.py', './sigame/app.py', 
#                      './sigame/utils/generate_translation.py', './sigame/__main__.py'],
#         'verbosity': 2,
#     }
