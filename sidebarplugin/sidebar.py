from trac.core import Component, implements, TracError
from trac.web.chrome import add_stylesheet, ITemplateProvider
from trac.web.api import ITemplateStreamFilter
from genshi.builder import tag
from genshi.filters.transform import Transformer
from api import ISidebarBoxProvider
from trac.core import ExtensionPoint
from pkg_resources import resource_filename

try:
    from simplifiedpermissionsadminplugin import SimplifiedPermissions
except ImportError, e:
    SimplifiedPermissions = None

class SidebarSystem(Component):
    """The sidebar system will call all ISidebarBoxProvider's get_box() in turn
        and append the result. The resulting tags will be placed in the 
        beginning of the <div id=content> tag of all wiki pages."""
    
    implements(ITemplateStreamFilter, ITemplateProvider)
    sidebar_boxes = ExtensionPoint(ISidebarBoxProvider)
    # ITemplateProvider methods
    def get_htdocs_dirs(self):
        return [('sidebar', resource_filename(__name__, 'htdocs'))]

    def get_templates_dirs(self):
        return [resource_filename('sidebarplugin', 'templates')]

    # ITemplateStreamFilter
    def filter_stream(self, req, method, filename, stream, data):
        if not filename == "wiki_view.html":
            return stream
        if not data['page'].name == "WikiStart":
            return stream
        add_stylesheet(req, "sidebar/css/sidebar.css")
        transformers = []
        stream = stream | Transformer("//div[@id='wikipage']").prepend(tag.div(class_="sidebar"))
        for box in self.sidebar_boxes:
            box_detail = box.get_box(req)
            if box_detail:
                transformers.append(Transformer("//div[@class='sidebar']").prepend(box_detail))
        return stream.filter(*transformers)
