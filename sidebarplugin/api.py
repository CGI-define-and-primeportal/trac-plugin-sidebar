from trac.core import Interface

class ISidebarBoxProvider(Interface):
    """Extention point interface for components providing sidebar boxes."""

    def get_box(req):
        """Returns a Genshi tag to go into the sidebar. Can return None to decline to provide anything"""
        
