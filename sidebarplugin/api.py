from trac.core import Interface

class ISidebarBoxProvider(Interface):
    """Extention point interface for components providing sidebar boxes."""

    def get_box():
        """Return an iterable which provides dictionaries like:
        {'url': '/ajax/usersearch/area',
         'name': 'Search Domain',
         'permission': 'SEARCH_AREA'}

         permission can be None. The url will be adjusted to be
         correct for this Trac instance.
         """
