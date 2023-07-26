class Link:
    # TODO: Add docstrings
    __slots__ = [
        "_hls_internal_field",
        "_hls_internal_link_id"
    ]

    def synthesize(field:str, link_id:int):
        # TODO: Make static
        l = Link()
        l._hls_internal_field = field
        l._hls_internal_link_id = link_id
