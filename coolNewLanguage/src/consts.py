from pathlib import Path

import jinja2

JINJA_ENV = jinja2.Environment(loader=jinja2.BaseLoader())

AIOHTTP_HTML = 'text/html'

DATA_DIR = Path('.').joinpath('data')

FILES_DIR = DATA_DIR.joinpath('uploaded_files')

STATIC_ROUTE = '/static'

CNL_DIR = Path('coolNewLanguage')

WEB_DIR = CNL_DIR.joinpath('web')

STATIC_FILE_DIR = WEB_DIR.joinpath('static')

TEMPLATES_DIR = WEB_DIR.joinpath('templates')

LANDING_PAGE_TEMPLATE_FILENAME = 'list_stages_landing_page.html'

LANDING_PAGE_STAGES = 'stages'

STAGE_TEMPLATE_FILENAME = 'stage.html'

STAGE_RESULTS_TEMPLATE_FILENAME = 'stage_results.html'

SELECT_STMT_RESULT_TEMPLATE_FILENAME = 'select_statement_results.html'

CELL_LIST_RESULT_TEMPLATE_FILENAME = 'cell_list_result.html'

FILE_UPLOAD_COMPONENT_TEMPLATE_FILENAME = 'file_upload_component_template.html'

USER_INPUT_COMPONENT_TEMPLATE_FILENAME = 'user_input_component_template.html'

TABLE_SELECTOR_COMPONENT_TEMPLATE_FILENAME = 'table_selector.html'
