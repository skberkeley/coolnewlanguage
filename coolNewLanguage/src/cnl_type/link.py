from typing import Optional

from coolNewLanguage.src.stage import process
from coolNewLanguage.src.util.link_utils import get_link_metatype_id_from_metaname, register_link_metatype


class Link:
    """
    Represents a Link metatype, rather than a single mapping between a pair of rows
    Each category of link is uniquely identified by its meta_name, or alternatively, by its id in the LINKS_META table

    Attributes:
        _hls_internal_link_meta_id: Optional[int]: The ID of this Link metatype in the LINKS_META table. Could be None,
            in the case that a Link is instantiated while a processor isn't being run, say during a CNLType subclass
            definition
        meta_name: str: The metaname of this link metatype
    """
    __slots__ = ('_hls_internal_link_meta_id', 'meta_name')

    def __init__(self, name: str):
        """
        Initializes a new Link metatype instance. If handling post, checks to see if this metatype exists already,
        registering it if it doesn't; then sets _hls_internal_link_meta_id to be the associated id.
        :param name: The metaname of this Link metatype
        """
        if not isinstance(name, str):
            raise TypeError("Expected name to be a string")

        self.meta_name = name

        if process.handling_post:
            tool = process.running_tool

            meta_id = get_link_metatype_id_from_metaname(tool=tool, link_meta_name=name)

            if meta_id is None:
                meta_id = register_link_metatype(tool=tool, link_meta_name=name)

            self._hls_internal_link_meta_id = meta_id
        else:
            self._hls_internal_link_meta_id = None

    def get_link_meta_id(self) -> Optional[int]:
        """
        Returns this Link metatype's meta id. If it is None, tries to obtain one using the running Tool. Returns None if
        the id is None and no Tool is currently executing a Processor.
        :return:
        """
        if self._hls_internal_link_meta_id is not None:
            return self._hls_internal_link_meta_id

        if not process.handling_post:
            return None

        tool = process.running_tool

        self._hls_internal_link_meta_id = get_link_metatype_id_from_metaname(tool=tool, link_meta_name=self.meta_name)

        if self._hls_internal_link_meta_id is None:
            self._hls_internal_link_meta_id = register_link_metatype(tool=tool, link_meta_name=self.meta_name)

        return self._hls_internal_link_meta_id
