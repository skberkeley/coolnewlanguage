from typing import Optional


class Link:
    __slots__ = ('link_meta_id', 'link_id', 'src_table_name', 'src_row_id', 'dst_table_name', 'dst_row_id')

    def __init__(self, link_meta_id: int, link_id: Optional[int], src_table_name: str, src_row_id: int, dst_table_name: str, dst_row_id: int):
        if not isinstance(link_meta_id, int):
            raise TypeError("Expected link_meta_id to be an int")
        if link_id is not None and not isinstance(link_id, int):
            raise TypeError("Expected link_id to be an int")
        if not isinstance(src_table_name, str):
            raise TypeError("Expected src_table_name to be a string")
        if not isinstance(src_row_id, int):
            raise TypeError("Expected src_row_id to be an int")
        if not isinstance(dst_table_name, str):
            raise TypeError("Expected dst_table_name to be a string")
        if not isinstance(dst_row_id, int):
            raise TypeError("Expected dst_row_id to be an int")

        self.link_meta_id = link_meta_id
        self.link_id = link_id
        self.src_table_name = src_table_name
        self.src_row_id = src_row_id
        self.dst_table_name = dst_table_name
        self.dst_row_id = dst_row_id
