from pathlib import Path

import jinja2

JINJA_ENV = jinja2.Environment(loader=jinja2.BaseLoader())

AIOHTTP_HTML = 'text/html'

DATA_DIR = Path('.').joinpath('data')

FILES_DIR = DATA_DIR.joinpath('uploaded_files')

STATIC_ROUTE = '/static'

STYLES_ROUTE = '/styles'

GET_TABLE_ROUTE = '/_get_table'

CNL_DIR = Path('coolNewLanguage')

WEB_DIR = CNL_DIR.joinpath('web')

STATIC_FILE_DIR = WEB_DIR.joinpath('static')

TEMPLATES_DIR = WEB_DIR.joinpath('templates')

STYLES_DIR = WEB_DIR.joinpath('styles')

LANDING_PAGE_TEMPLATE_FILENAME = 'list_stages_landing_page.html'

LANDING_PAGE_STAGES = 'stages'

STAGE_TEMPLATE_FILENAME = 'stage.html'

STAGE_RESULTS_TEMPLATE_FILENAME = 'stage_results.html'

TABLE_RESULT_TEMPLATE_FILENAME = 'result_table.html'

CELL_LIST_RESULT_TEMPLATE_FILENAME = 'cell_list_result.html'

LINK_RESULT_TEMPLATE_FILENAME = 'link_result.html'

FILE_UPLOAD_COMPONENT_TEMPLATE_FILENAME = 'file_upload_component_template.html'

USER_INPUT_COMPONENT_TEMPLATE_FILENAME = 'user_input_component_template.html'

SELECTOR_COMPONENT_TEMPLATE_FILENAME = "selector_component_template.html"

TABLE_SELECTOR_COMPONENT_TEMPLATE_FILENAME = 'table_selector.html'

COLUMN_SELECTOR_COMPONENT_TEMPLATE_FILENAME = 'column_selector.html'

APPROVAL_PAGE_TEMPLATE_FILENAME = 'approval_page.html'

LINKS_METATYPES_TABLE_NAME = "__hls_links_metatypes"
LINKS_METATYPES_LINK_META_ID = "link_meta_id"
LINKS_METATYPES_LINK_META_NAME = "meta_name"

LINKS_REGISTRY_TABLE_NAME = "__hls_links"
LINKS_REGISTRY_LINK_ID = "id"
LINKS_REGISTRY_LINK_META_ID = "link_meta_id"
LINKS_REGISTRY_SRC_TABLE_NAME = "src_table_name"
LINKS_REGISTRY_SRC_ROW_ID = "src_row_id"
LINKS_REGISTRY_DST_TABLE_NAME = "dst_table_name"
LINKS_REGISTRY_DST_ROW_ID = "dst_row_id"

GET_TABLE_TABLE_SELECT = "table_select"
GET_TABLE_COLUMN_SELECT = "column_select"

TABLE_SELECTOR_FULL_TABLE_TEMPLATE_FILENAME = "table_selector_full_table.html"
COLUMN_SELECTOR_FULL_TABLE_TEMPLATE_FILENAME = "column_selector_full_table.html"

METADATA_COLUMN_NAMES = set(["__hls_internal_id"])

DATAFRAME_TABLE_TEMPLATE_FILENAME = "dataframe_table.html"
