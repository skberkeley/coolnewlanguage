from pathlib import Path

import jinja2

JINJA_ENV = jinja2.Environment(loader=jinja2.BaseLoader())

AIOHTTP_HTML = 'text/html'

DATA_DIR = Path('.').joinpath('data')

FILES_DIR = DATA_DIR.joinpath('uploaded_files')
