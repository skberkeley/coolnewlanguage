from typing import Optional

import sqlalchemy

from coolNewLanguage.src import consts
from coolNewLanguage.src.tool import Tool
from coolNewLanguage.src.util.db_utils import get_table_from_table_name


def get_link_metatype_id_from_metaname(tool: Tool, link_meta_name: str) -> Optional[int]:
    """
    Gets the link metatype id associated with the passed link metaname. If no link metatype with the passed metaname
    exists, returns None
    :param tool: The Tool whose link metatypes are to be searched
    :param link_meta_name: The meta_name to be matched
    :return:
    """
    if not isinstance(tool, Tool):
        raise TypeError("Expected tool to be a Tool")
    if not isinstance(link_meta_name, str):
        raise TypeError("Expected link_meta_name to be a string")

    links_meta = get_table_from_table_name(tool, consts.LINKS_METATYPES_TABLE_NAME)

    stmt = sqlalchemy.select(links_meta.c[consts.LINKS_METATYPES_LINK_META_ID])\
        .where(links_meta.c[consts.LINKS_METATYPES_LINK_META_NAME] == link_meta_name)

    with tool.db_engine.connect() as conn:
        result = conn.execute(stmt).first()

    if result is None:
        return None

    return result[consts.LINKS_METATYPES_LINK_META_ID]


def register_link_metatype_on_tool(tool: Tool, link_meta_name: str) -> Optional[int]:
    """
    Registers a link metatype, by first checking to see if it exists in the metatype table before inserting a new row
    into it. Returns the resulting meta id for the registered link metatype.
    :param tool: The Tool for which to register the link metatype
    :param link_meta_name: The meta name for the metatype to be registered
    :return:
    """
    if not isinstance(tool, Tool):
        raise TypeError("Expected tool to be a Tool")
    if not isinstance(link_meta_name, str):
        raise TypeError("Expected link_meta_name to be a string")

    meta_id = get_link_metatype_id_from_metaname(tool, link_meta_name)
    if meta_id is not None:
        return meta_id

    table = get_table_from_table_name(tool, consts.LINKS_METATYPES_TABLE_NAME)
    insert_stmt = sqlalchemy.insert(table).values({consts.LINKS_METATYPES_LINK_META_NAME: link_meta_name})
    with tool.db_engine.connect() as conn:
        result = conn.execute(insert_stmt)
        conn.commit()

    return result.inserted_primary_key[consts.LINKS_METATYPES_LINK_META_ID]


def get_link_id(
        tool: Tool,
        link_meta_id: int,
        src_table_name: str,
        src_row_id: int,
        dst_table_name: str,
        dst_row_id: int
) -> Optional[int]:
    """
    Gets the link id identified by the passed parameters, returning None if such a link has not yet been registered.
    :param tool:
    :param link_meta_id:
    :param src_table_name:
    :param src_row_id:
    :param dst_table_name:
    :param dst_row_id:
    :return:
    """
    if not isinstance(tool, Tool):
        raise TypeError("Expected tool to be a Tool")
    if not isinstance(link_meta_id, int):
        raise TypeError("Expected link_meta_id to be an int")
    if not isinstance(src_table_name, str):
        raise TypeError("Expected src_table_name to be a string")
    if not isinstance(src_row_id, int):
        raise TypeError("Expected src_row_id to be an int")
    if not isinstance(dst_table_name, str):
        raise TypeError("Expected dst_table_name to be a string")
    if not isinstance(dst_row_id, int):
        raise TypeError("Expected dst_row_id to be an int")

    links_registry = get_table_from_table_name(tool, consts.LINKS_REGISTRY_TABLE_NAME)

    stmt = sqlalchemy.select(links_registry.c[consts.LINKS_REGISTRY_LINK_ID])\
        .where(links_registry.c[consts.LINKS_REGISTRY_LINK_META_ID] == link_meta_id)\
        .where(links_registry.c[consts.LINKS_REGISTRY_SRC_TABLE_NAME] == src_table_name)\
        .where(links_registry.c[consts.LINKS_REGISTRY_SRC_ROW_ID] == src_row_id)\
        .where(links_registry.c[consts.LINKS_REGISTRY_DST_TABLE_NAME] == dst_table_name)\
        .where(links_registry.c[consts.LINKS_REGISTRY_DST_ROW_ID] == dst_row_id)

    with tool.db_engine.connect() as conn:
        result = conn.execute(stmt).first()

    if result is None:
        return None

    return result[consts.LINKS_REGISTRY_LINK_ID]


def register_new_link(
        tool: Tool,
        link_meta_id: int,
        src_table_name: str,
        src_row_id: int,
        dst_table_name: str,
        dst_row_id: int
) -> int:
    """
    Registers a new link, which is uniquely identified by its metatype, source table and row id, and destination table
    and row id. Checks to see that the link doesn't already exist before issuing an insert statement. Returns the id of
    the registered link.
    :param tool:
    :param link_meta_id:
    :param src_table_name:
    :param src_row_id:
    :param dst_table_name:
    :param dst_row_id:
    :return:
    """
    if not isinstance(tool, Tool):
        raise TypeError("Expected tool to be a Tool")
    if not isinstance(link_meta_id, int):
        raise TypeError("Expected link_meta_id to be an int")
    if not isinstance(src_table_name, str):
        raise TypeError("Expected src_table_name to be a string")
    if not isinstance(src_row_id, int):
        raise TypeError("Expected src_row_id to be an int")
    if not isinstance(dst_table_name, str):
        raise TypeError("Expected dst_table_name to be a string")
    if not isinstance(dst_row_id, int):
        raise TypeError("Expected dst_row_id to be an int")

    link_id = get_link_id(tool, link_meta_id, src_table_name, src_row_id, dst_table_name, dst_row_id)
    if link_id is not None:
        return link_id

    table = get_table_from_table_name(tool, consts.LINKS_REGISTRY_TABLE_NAME)
    insert_stmt = sqlalchemy.insert(table)\
        .values(
        {
            consts.LINKS_REGISTRY_LINK_META_ID: link_meta_id,
            consts.LINKS_REGISTRY_SRC_TABLE_NAME: src_table_name,
            consts.LINKS_REGISTRY_SRC_ROW_ID: src_row_id,
            consts.LINKS_REGISTRY_DST_TABLE_NAME: dst_table_name,
            consts.LINKS_REGISTRY_DST_ROW_ID: dst_row_id,
        }
    )

    with tool.db_engine.connect() as conn:
        result = conn.execute(insert_stmt)
        conn.commit()

    return result.inserted_primary_key[consts.LINKS_REGISTRY_TABLE_NAME]
