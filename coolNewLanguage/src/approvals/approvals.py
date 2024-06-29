import jinja2
import sqlalchemy
from aiohttp import web

from coolNewLanguage.src import consts
from coolNewLanguage.src.approvals.approve_result import ApproveResult
from coolNewLanguage.src.approvals.approve_result_type import ApproveResultType
from coolNewLanguage.src.approvals.approve_state import ApproveState
from coolNewLanguage.src.approvals.link_approve_result import LinkApproveResult
from coolNewLanguage.src.approvals.row_approve_result import RowApproveResult
from coolNewLanguage.src.approvals.table_approve_result import TableApproveResult
from coolNewLanguage.src.stage import config, process, results
from coolNewLanguage.src.stage.stage import Stage
from coolNewLanguage.src.tool import Tool
from coolNewLanguage.src.util import db_utils, link_utils
from coolNewLanguage.src.util.sql_alch_csv_utils import DB_INTERNAL_COLUMN_ID_NAME


def get_user_approvals():
    """
    Get user approvals for changes to the underlying db
    If building_template, this function sets the get_user_approvals flag to True, so that we know to cache changes to
    the db when handling post
    If handling post, takes the cached changes to the db, and constructs the HTML page for approvals, setting it on Stage
    :return:
    """
    if config.building_template:
        process.get_user_approvals = True
        return

    if process.handling_post:
        template: jinja2.Template = process.running_tool.jinja_environment.get_template(
            name=consts.APPROVAL_PAGE_TEMPLATE_FILENAME
        )

        approve_handler_url = f'/{process.curr_stage_url}/approve'
        template.globals['ApproveResultType'] = ApproveResultType
        form_method = 'post'
        form_enctype = 'multipart/form-data'

        Stage.approvals_template = template.render(
            approve_results=process.approve_results,
            form_action=approve_handler_url,
            form_method=form_method,
            form_enctype=form_enctype
        )


async def approval_handler(request: web.Request) -> web.Response:
    """
    The handler for user approvals
    Uses the post body to determine which ApproveResults were approved, and which were rejected, and commits those that
    were approved to the database. Then, redirects back to the Tool landing page
    :param request:
    :return:
    """
    process.get_user_approvals = False
    process.handling_user_approvals = True

    # Set the post results of the user's approvals on process
    process.approval_post_body = await request.post()

    # Iterate through the cached ApproveResults, processing each one as appropriate
    approve_result: ApproveResult
    for approve_result in process.approve_results:
        if approve_result.approve_result_type == ApproveResultType.TABLE:
            approve_result: TableApproveResult
            handle_table_approve_result(approve_result)
        elif approve_result.approve_result_type == ApproveResultType.ROW:
            approve_result: RowApproveResult
            handle_row_approve_result(approve_result)
        elif approve_result.approve_result_type == ApproveResultType.LINK:
            approve_result: LinkApproveResult
            handle_link_approve_result(approve_result)

    # If there are results to show, call show_results on them to construct the results template
    results_template: str = ""
    if process.cached_show_results:
        results.show_results(results=process.cached_show_results, results_title=process.cached_show_results_title)
        results_template = Stage.results_template
        Stage.results_template = None

    # Reset the relevant values in process
    process.handling_user_approvals = False
    process.approve_results = []
    process.curr_stage_url = ""
    process.approval_post_body = None
    process.cached_show_results = []
    process.cached_show_results_title = ""
    ApproveResult.num_approve_results = 0

    # Show the cached results or return to landing page
    if results_template:
        return web.Response(body=results_template, content_type=consts.AIOHTTP_HTML)
    raise web.HTTPFound(location='/')


def handle_table_approve_result(table_approve_result: TableApproveResult):
    """
    Handles a user-processed TableApproveResult
    Checks to see which rows were approved by the user, and commits exactly the rows which they approved.
    :param table_approve_result:
    :return:
    """
    # Filter the rows that were approved
    approved_rows = []
    for i, row in enumerate(table_approve_result.rows):
        approve_result_name = f'approve_{table_approve_result.id}_{i + 1}'
        raw_approval_state = process.approval_post_body[approve_result_name]
        approval_state = ApproveState.of_string(raw_approval_state)
        if approval_state == ApproveState.APPROVED:
            approved_rows.append(row)

    # If there were no approved rows, then return early
    if len(approved_rows) == 0:
        return

    # Create the associated table in the db
    tool: Tool = process.running_tool
    tool.db_metadata_obj.create_all(tool.db_engine, [table_approve_result.sqlalchemy_table])

    # Construct an insert statement for the approved rows
    records = [{col_name: row[i] for i, col_name in enumerate(table_approve_result.column_names)} for row in approved_rows]
    insert_stmt = sqlalchemy.insert(table_approve_result.sqlalchemy_table).values(records)

    # Execute the constructed insert statement
    with tool.db_engine.connect() as conn:
        conn.execute(insert_stmt)
        conn.commit()


def handle_row_approve_result(row_approve_result: RowApproveResult):
    """
    Handles a user-processed RowApproveResult
    Checks to see if the row was approved by the user, and commits it if so.
    :param row_approve_result:
    :return:
    """
    approve_result_name = f'approve_{row_approve_result.id}'
    raw_approval_state = process.approval_post_body[approve_result_name]
    approval_state = ApproveState.of_string(raw_approval_state)

    if approval_state != ApproveState.APPROVED:
        return

    # Get the table associated with this row
    tool: Tool = process.running_tool
    table: sqlalchemy.Table = tool.get_table_from_table_name(row_approve_result.table_name)

    # If the approved row is a new one, create an insert statement
    if row_approve_result.is_new_row:
        stmt = sqlalchemy.insert(table).values(row_approve_result.row)
    # Else, construct an update statement
    else:
        id_column = table.c[DB_INTERNAL_COLUMN_ID_NAME]
        row_id = row_approve_result.row[DB_INTERNAL_COLUMN_ID_NAME]
        stmt = sqlalchemy.update(table).where(id_column == row_id).values(row_approve_result.row)

    # Execute the constructed statement
    with tool.db_engine.connect() as conn:
        conn.execute(stmt)
        conn.commit()


def handle_link_approve_result(link_approve_result: LinkApproveResult):
    """
    Handles a user-processed LinkApproveResult
    Checks to see if the link was approved by the user, and commits it if so.
    :param link_approve_result:
    :return:
    """
    approve_result_name = f'approve_{link_approve_result.id}'
    raw_approval_state = process.approval_post_body[approve_result_name]
    approval_state = ApproveState.of_string(raw_approval_state)

    if approval_state != ApproveState.APPROVED:
        return

    # Register the new link
    tool: Tool = process.running_tool
    link = link_approve_result.link
    link_utils.register_new_link(
        tool,
        link.link_meta_id,
        link.src_table_name,
        link.src_row_id,
        link.dst_table_name,
        link.dst_row_id
    )