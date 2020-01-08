from xml.etree import ElementTree


class Spell:
    def __init__(self):
        self.name = None
        self.slug = None
        self.level = 0
        self.school = None
        self.ritual = "NO"
        self.time = None
        self.range = None
        self.duration = None
        self.classes = None
        self.components = None
        self.text = None
        self.source = None
        self.image = None

    def export_xml(self, compendium):
        el = ElementTree.SubElement(compendium, "spell")
        ElementTree.SubElement(el, "name").text = self.name
        ElementTree.SubElement(el, "slug").text = self.slug
        ElementTree.SubElement(el, "level").text = self.level
        ElementTree.SubElement(el, "school").text = self.school
        ElementTree.SubElement(el, "ritual").text = self.ritual
        ElementTree.SubElement(el, "time").text = self.time
        ElementTree.SubElement(el, "range").text = self.range
        ElementTree.SubElement(el, "duration").text = self.duration
        ElementTree.SubElement(el, "classes").text = self.classes
        ElementTree.SubElement(el, "components").text = self.components
        ElementTree.SubElement(el, "text").text = self.text
        ElementTree.SubElement(el, "source").text = self.source
        ElementTree.SubElement(el, "image").text = self.image
