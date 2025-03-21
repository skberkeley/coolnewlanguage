import jinja2
import pandas as pd
from aiohttp import web

from coolNewLanguage.src import consts
from coolNewLanguage.src.approvals.approve_result import ApproveResult
from coolNewLanguage.src.approvals.approve_result_type import ApproveResultType
from coolNewLanguage.src.approvals.approve_state import ApproveState
from coolNewLanguage.src.approvals.table_approve_result import TableApproveResult
from coolNewLanguage.src.approvals.table_deletion_approve_result import TableDeletionApproveResult
from coolNewLanguage.src.approvals.table_row_addition_approve_result import TableRowAdditionApproveResult
from coolNewLanguage.src.approvals.table_schema_change_approve_result import TableSchemaChangeApproveResult
from coolNewLanguage.src.exceptions.CNLError import CNLError
from coolNewLanguage.src.stage import config, process, results
from coolNewLanguage.src.stage.stage import Stage
from coolNewLanguage.src.tool import Tool
from coolNewLanguage.src.util.sql_alch_csv_utils import DB_INTERNAL_COLUMN_ID_NAME


"""
A list of ApproveResults to be inspected by the user
This list is constructed by get_user_approvals when the approval page is being built, and then consumed by the approval
handler when the user's approvals are being processed. It allows the two functions to communicate the list of results 
that the user is being asked to approve.
"""
approve_results: list[ApproveResult] = []


def get_user_approvals():
    """
    Get user approvals for changes to the underlying db
    If building_template, this function sets the get_user_approvals flag to True, so that we know to cache changes to
    the db when handling post
    If handling post, takes the cached changes to the db, and constructs the HTML page for approvals, setting it on Stage
    :return:
    """
    if config.building_template:
        raise CNLError(
            "get_user_approvals was called in an unexpected place. Did you forget to check if user input was received?")

    if process.handling_post:
        template: jinja2.Template = process.running_tool.jinja_environment.get_template(
            name=consts.APPROVAL_PAGE_TEMPLATE_FILENAME
        )

        approve_handler_url = f'/{process.curr_stage_url}/approve'
        template.globals['ApproveResultType'] = ApproveResultType
        form_method = 'post'
        form_enctype = 'multipart/form-data'

        tool = process.running_tool

        # Construct approve_results from tool.tables
        approve_results.clear()
        # Create deletion results
        for table in tool.tables._tables_to_delete:
            approve_results.append(TableDeletionApproveResult(
                table, tool._get_table_dataframe(table)))
        # Create table approve results
        for table, df in tool.tables._tables_to_save.items():
            approve_results.append(get_table_approve_object(table, df))

        Stage.approvals_template = template.render(
            approve_results=approve_results,
            form_action=approve_handler_url,
            form_method=form_method,
            form_enctype=form_enctype,
            stage_name=process.stage_name
        )


def get_table_approve_object(table_name: str, df: pd.DataFrame) -> ApproveResult:
    """
    Depending on the difference between the passed df, and the associated prior version in the db, return the
    appropriate type of ApproveResult. Used during approval page construction for tables cached to be stored in the db.
    :param table_name: The name of the table being overwritten
    :param df: The new dataframe to be stored in the db
    :return: An instance of the appropriate subclass of ApproveResult
    """
    tool: Tool = process.running_tool
    original_df = tool._get_table_dataframe(table_name)

    if original_df is None:
        # If the table is new, return a TableApproveResult
        return TableApproveResult(table_name, df)

    # Check if columns were added
    were_columns_added = len(original_df.columns) < len(df.columns)

    # Check if rows were added
    were_rows_added = df.shape[0] != original_df.shape[0]

    if were_columns_added and not were_rows_added:
        # Return a TableSchemaChangeApproveResult
        cols_added = list(
            filter(lambda col: col not in original_df.columns, df.columns))
        return TableSchemaChangeApproveResult(table_name, cols_added, df)

    if not were_columns_added and were_rows_added:
        # We currently only support row additions
        # Return a TableRowAdditionApproveResult
        # Compute the indices of the rows that were added
        added_rows = list(range(original_df.shape[0], df.shape[0]))
        print(added_rows)
        return TableRowAdditionApproveResult(table_name, added_rows, df)

    # Return default TableApproveResult
    return TableApproveResult(table_name, df)


async def approval_handler(request: web.Request) -> web.Response:
    """
    The handler for user approvals
    Uses the post body to determine which ApproveResults were approved, and which were rejected, and commits those that
    were approved to the database. Then, redirects back to the Tool landing page
    :param request:
    :return:
    """
    if not isinstance(request, web.Request):
        raise TypeError("Expected request to be an aiohttp web.Request")

    process.handling_user_approvals = True

    # Set the post results of the user's approvals on process
    process.approval_post_body = await request.post()

    # Iterate through the cached ApproveResults, processing each one as appropriate
    for approve_result in approve_results:
        match approve_result:
            case TableApproveResult():
                handle_table_approve_result(approve_result)
            case TableSchemaChangeApproveResult():
                handle_table_schema_change_approve_result(approve_result)
            case TableDeletionApproveResult():
                handle_table_deletion_approve_result(approve_result)
            case TableRowAdditionApproveResult():
                handle_table_row_addition_approve_result(approve_result)
            case _:
                raise ValueError(f"Unknown ApproveResult type")

    # If there are results to show, call show_results on them to construct the results template
    results_template: str = ""
    if process.cached_show_results:
        results.show_results(*process.cached_show_results,
                             results_title=process.cached_show_results_title)
        # show_results sets the results_template on Stage, so we need to cache it and then reset it
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

    # Remove cached changes from tool.tables
    process.running_tool.tables._tables_to_delete.clear()

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

    for index, _ in table_approve_result.dataframe.iterrows():
        approve_result_name = f'approve_{table_approve_result.id}_{index}'
        raw_approval_state = process.approval_post_body[approve_result_name]
        approval_state = ApproveState.of_string(raw_approval_state)
        if approval_state == ApproveState.APPROVED:
            approved_rows.append(index)

    # If there were no approved rows, then return early
    if len(approved_rows) == 0:
        return

    # Filter the dataframe to only include the approved rows
    df = table_approve_result.dataframe.loc[approved_rows]

    # Save the dataframe using tool.tables
    process.running_tool.tables._save_table(
        table_approve_result.table_name, df)


def handle_table_schema_change_approve_result(table_schema_change_approve_result: TableSchemaChangeApproveResult):
    """
    Handles a user-processed TableSchemaChangeApproveResult
    Filters rows that were approved by the user, and commits the new columns and data to the table if they were
    approved. If no rows were approved, then the new columns are not committed.
    :param table_schema_change_approve_result:
    :return:
    """
    df = table_schema_change_approve_result.dataframe

    # Compute the approved rows
    approve_result_name = f'approve_{table_schema_change_approve_result.id}'

    indices = df.index
    approved_rows = [i for i in indices if ApproveState.of_string(
        process.approval_post_body[f'{approve_result_name}_{i}']) == ApproveState.APPROVED]

    # If no rows were approved, then return early. No changes will be committed
    if len(approved_rows) == 0:
        return

    # Keep values which were approved
    for col in table_schema_change_approve_result.cols_added:
        df[col] = df.apply(
            lambda x: x[col] if x.name in approved_rows else '', axis=1)

    # Commit the final df
    process.running_tool.tables._save_table(
        table_schema_change_approve_result.table_name, df)


def handle_table_row_addition_approve_result(table_row_addition_approve_result: TableRowAdditionApproveResult):
    """
    Handles a user-processed TableRowAdditionApproveResult
    Filters rows that were approved by the user, and commits the new rows to the table if they were approved.
    :param table_row_addition_approve_result:
    :return:
    """
    df = table_row_addition_approve_result.dataframe

    # Compute the approved rows
    approve_result_name = f'approve_{table_row_addition_approve_result.id}'

    indices = table_row_addition_approve_result.rows_added
    approved_rows = [i for i in indices if ApproveState.of_string(
        process.approval_post_body[f'{approve_result_name}_{i}']) == ApproveState.APPROVED]

    # If no rows were approved, then return early. No changes will be committed
    if len(approved_rows) == 0:
        return

    # Filter the dataframe to only include the approved rows
    df = df.loc[approved_rows]

    # Get the existing table
    existing_df = process.running_tool._get_table_dataframe(
        table_row_addition_approve_result.table_name)

    # Concatenate the approved rows to the existing table
    if existing_df is not None:
        df = pd.concat([existing_df, df])

    # Commit the final df
    process.running_tool.tables._save_table(
        table_row_addition_approve_result.table_name, df)


def handle_table_deletion_approve_result(table_deletion_approve_result: TableDeletionApproveResult):
    """
    Handles a user-processed TableDeletionApproveResult
    Checks to see if the table deletion was approved by the user, and commits it if so.
    :param table_deletion_approve_result:
    :return:
    """
    approve_result_name = f'approve_{table_deletion_approve_result.id}'
    raw_approval_state = process.approval_post_body[approve_result_name]
    approval_state = ApproveState.of_string(raw_approval_state)

    if approval_state != ApproveState.APPROVED:
        return

    # Drop the table
    process.running_tool.tables._delete_table(
        table_deletion_approve_result.table_name)
