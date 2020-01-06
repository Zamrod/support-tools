from xml.etree import ElementTree


class Item:
    def __init__(self):
        self.parent = None
        self.name = None
        self.slug = None
        self.meta = {}

    def export_xml(self, compendium):
        el = ElementTree.SubElement(compendium, "item")
        if self.parent is not None:
            el.set("parent", self.parent.id)
        ElementTree.SubElement(el, "name").text = self.name
        ElementTree.SubElement(el, "slug").text = self.slug

