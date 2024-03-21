import numpy as np
import pandas as pd
from statistics import mode
from coolNewLanguage.src.component.column_selector_component import ColumnSelectorComponent
from coolNewLanguage.src.component.file_upload_component import FileUploadComponent
from coolNewLanguage.src.component.table_selector_component import TableSelectorComponent
from coolNewLanguage.src.component.text_component import TextComponent
from coolNewLanguage.src.component.user_input_component import UserInputComponent
from coolNewLanguage.src.component.selector_component import SelectorComponent
from coolNewLanguage.src.processor.lamda_processor import LambdaProcessor
from coolNewLanguage.src.stage import results
from coolNewLanguage.src.tool import Tool
from coolNewLanguage.src.util.db_utils import create_table_from_csv, get_column_names_from_table_name, \
    create_table_from_lists


def main():
    tool = Tool('basic_backend')

    def csv_upload_and_name():
        """
        Stage to upload a csv file and give the resulting table a name. To test, upload a csv file, giving it a name,
        and then upload a non-csv file and make sure an error is shown. Finally, upload the original file and test that
        an error is shown regarding uploading a file with the same name.
        :return:
        """
        table_name = UserInputComponent(str, label="Enter table name:")
        csv_file = FileUploadComponent('csv', label="Upload a csv file:")

        def create_table():
            return create_table_from_csv(table_name, csv_file, True, overwrite_existing=True)
        created_table = LambdaProcessor(create_table).result
        results.show_results([results.Result(created_table, "Created table: ")])

    tool.add_stage('csv_upload_and_name', csv_upload_and_name)

    def metrics():
        """
        Stage to get various metrics of a column of data. To test, select a table in the database,
        select the column of interest, and select the metric of interest. If mean, median, or standard
        deviation are selected, the entries of the column must be castable to integers (otherwise the program will error).
        Demonstration on how to utilize Numpy in context of a CNL program.
        """
        table = TableSelectorComponent(label="Select a table")
        col = ColumnSelectorComponent(label="Select the column that you want your metric on")
        metric_selector = SelectorComponent(str, options=["mean", "median", "mode", "standard deviation"], label="Select the metric you want to see! Mean, median, and standard deviation only work for numerial data.")

        def process_metrics():
            desired_metric = metric_selector.value
            column_name = col.emulated_columns[0]
            values = []

            for row in table:
                value = row[column_name].val
                if desired_metric != "mode":
                    try:
                        value = int(value)
                    except:
                        raise Exception("Expected value of column to be a number, since mean, median, or standard deviation was selected.")
                values.append(value)

            if desired_metric == "mean":
                return round(np.mean([value for value in values]), 3)
            elif desired_metric == "median":
                return round(np.median([value for value in values]), 3)
            elif desired_metric == "standard deviation":
                return round(np.std([value for value in values]), 3)
            else:
                return mode(values)

        processor = LambdaProcessor(process_metrics)
        results.show_results([results.Result(processor.result, "Desired metric:")])

    tool.add_stage('metrics', metrics)

    def inner_merge():
        """
        Stage to perform an inner merge with specified tables and columns. This implementation only
        merges on one column of keys for each table. Values of left keys must be unique. Does not utilize any external
        packages.
        """
        left_table = TableSelectorComponent(label="Select the left table for the merge")
        right_table = TableSelectorComponent(label="Select the right table for the merge")
        left_on = ColumnSelectorComponent(label="Select the column for the left table to merge on, expects merge keys to be unique (implementation only merges on one column)")
        right_on = ColumnSelectorComponent(label="Select the column for the right table to merge on (implementation only merges on one column)")
        table_name = UserInputComponent(str, label="Enter table name, entering a name that already exists will REWRITE the original table with newly merged table.")

        def process_inner_merge():
            left_key = left_on.emulated_columns[0]
            right_key = right_on.emulated_columns[0]
            left_cols = []
            right_cols = []
            left_merge_information = {}
            new_rows = []
            for row in left_table:
                if not left_cols:
                    left_cols = list(row.keys())[1:]
                left_merge_information[row[left_key].val] = [row[col].val for col in left_cols]
            for row in right_table:
                if not right_cols:
                    right_cols = list(row.keys())[1:]
                    right_cols.remove(right_key)
                if row[right_key].val in left_merge_information:
                    right_row = [row[col].val for col in right_cols]
                    new_rows.append(left_merge_information[row[right_key].val] + right_row)

            left_cols.extend(right_cols)

            new_table = [left_cols]
            new_table.extend(new_rows)

            return create_table_from_lists(table_name.value, new_table, return_existing_table=False, overwrite_existing_table=True)

        processor = LambdaProcessor(process_inner_merge)
        results.show_results([results.Result(processor.result, "Merged table:")])

    tool.add_stage('inner merge', inner_merge)

    def pandas_merge():
        left_table = TableSelectorComponent(label="Select the left table for the merge")
        right_table = TableSelectorComponent(label="Select the right table for the merge")
        left_on = ColumnSelectorComponent(label="Select the column for the left table to merge on, expects merge keys to be unique (implementation only merges on one column)")
        right_on = ColumnSelectorComponent(label="Select the column for the right table to merge on (implementation only merges on one column)")
        merge_type = SelectorComponent(str, options = ['left', 'right', 'outer', 'inner', 'cross'], label="Select the merge type desired. Missing values will be reported as \"None\" in the merged table.")
        table_name = UserInputComponent(str, label="Enter table name, entering a name that already exists will REWRITE the original table with newly merged table.")

        def process_pandas_merge():
            left_key = left_on.emulated_columns[0]
            right_key = right_on.emulated_columns[0]
            left_table_dict = {}
            right_table_dict = {}
            for row in left_table:
                if not left_table_dict:
                    for col in list(row.keys())[1:]:
                        left_table_dict[col] = []
                for key in left_table_dict:
                    left_table_dict[key].append(row[key].val)
            for row in right_table:
                if not right_table_dict:
                    for col in list(row.keys())[1:]:
                        right_table_dict[col] = []
                for key in right_table_dict:
                    right_table_dict[key].append(row[key].val)

            left_df = pd.DataFrame(left_table_dict)
            right_df = pd.DataFrame(right_table_dict)

            merged_dataframe = left_df.merge(right_df, how=merge_type.value, left_on=left_key, right_on=right_key)

            new_table = [list(merged_dataframe.columns)]
            new_table.extend(merged_dataframe.values.tolist())

            return create_table_from_lists(table_name.value, new_table, return_existing_table=False, overwrite_existing_table=True)

        processor = LambdaProcessor(process_pandas_merge)
        results.show_results([results.Result(processor.result, "Merged table:")])

    tool.add_stage('pandas merge', pandas_merge)

    def numerical_filter():
        table = TableSelectorComponent(label="Select the table you want to filter")
        col = ColumnSelectorComponent(label="Select the numerical column to filter on")
        relationship = SelectorComponent(str, options=["Greater than", "Less than", "Equal to", "Not equal to"], label="Select the relationship you want to filter on")
        boundary = UserInputComponent(int, label="Input the value you want to compare the values of your selected column to")

        def process_numerical_filter():
            var = relationship.value
            if var == "Greater than":
                return [row for row in table if int(row[col.emulated_columns[0]].val) > boundary.value]
            elif var == "Less than":
                return [row for row in table if int(row[col.emulated_columns[0]].val) < boundary.value]
            elif var == "Equal to":
                return [row for row in table if int(row[col.emulated_columns[0]].val) == boundary.value]
            else:
                return [row for row in table if int(row[col.emulated_columns[0]].val) != boundary.value]

        processor = LambdaProcessor(process_numerical_filter)
        results.show_results([results.Result(processor.result, "Filtered results:")])

    tool.add_stage('numerical_filter', numerical_filter)

    def numerical_filter_new_table():
        table = TableSelectorComponent(label="Select the table you want to filter")
        col = ColumnSelectorComponent(label="Select the numerical column to filter on")
        relationship = SelectorComponent(str, options=["Greater than"], label="Select the relationship you want to filter on")
        boundary = UserInputComponent(int, label="Input the value you want to compare the values of your selected column to")
        table_name = UserInputComponent(str, label="Enter table name, entering a name that already exists will REWRITE the original table with newly merged table.")

        def process_numerical_filter_new_table():
            columns = []
            valid_rows = []
            for row in table:
                if not columns:
                    columns = list(row.keys())[1:]
                if int(row[col.emulated_columns[0]].val) > boundary.value:
                    row_values = []
                    for column in columns:
                        row_values.append(row[column].val)
                    valid_rows.append(row_values)

            new_table = [columns]
            new_table.extend(valid_rows)

            return create_table_from_lists(table_name.value, new_table, return_existing_table=False, overwrite_existing_table=True)

        processor = LambdaProcessor(process_numerical_filter_new_table)
        results.show_results([results.Result(processor.result, "Filtered table:")])

    tool.add_stage('process_numerical_filter_new_table', numerical_filter_new_table)

    def drop_column():
        table = TableSelectorComponent(label="Select the table you want to filter")
        col = ColumnSelectorComponent(label="Select column to drop")
        table_name = UserInputComponent(str, label="Enter table name, entering a name that already exists will REWRITE the original table.")


        def process_drop_column():
            columns = []
            new_rows = []
            for row in table:
                if not columns:
                    columns = list(row.keys())[1:]
                    columns.remove(col.emulated_columns[0])
                new_row = [row[column].val for column in columns]
                new_rows.append(new_row)

            new_table = [columns]
            new_table.extend(new_rows)

            return create_table_from_lists(table_name.value, new_table, return_existing_table=False, overwrite_existing_table=True)

        processor = LambdaProcessor(process_drop_column)
        results.show_results([results.Result(processor.result)])

    tool.add_stage('drop_column', drop_column)

    def delete_table():
        table = TableSelectorComponent(label="Select a table that you want to delete from the database.")

        def process_delete_table():
            table.delete()
            return "Sucessfully deleted table"

        processor = LambdaProcessor(process_delete_table)
        results.show_results([results.Result(processor.result)])

    tool.add_stage('delete_table', delete_table)

    tool.run()

if __name__ == '__main__':
    main()
