import sqlalchemy

from coolNewLanguage.src.row import Row


def verify_row_iterator(row_iterator: Row.RowIterator,
                        table: sqlalchemy.Table,
                        row_mapping: dict,
                        col_names,
                        row_id: int,
                        cell_mapping: dict):
    assert row_iterator.table == table
    assert row_iterator.row_mapping == row_mapping
    assert row_iterator.col_names == col_names
    assert row_iterator.row_id == row_id
    assert row_iterator.cell_mapping == cell_mapping
