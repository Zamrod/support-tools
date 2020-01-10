from xml.etree import ElementTree


class Item:
    def __init__(self):
        self.name = None
        self.slug = None
        self.type = None
        self.weight = None
        self.heading = None
        self.attunement = None
        self.rarity = "Common"
        self.value = None
        self.property = None
        self.dmg1 = None
        self.dmg2 = None
        self.dmgType = None
        self.range = None
        self.ac = None
        self.source = None
        self.text = None

    def export_xml(self, compendium):
        el = ElementTree.SubElement(compendium, "item")
        ElementTree.SubElement(el, "name").text = self.name
        ElementTree.SubElement(el, "slug").text = self.slug
        ElementTree.SubElement(el, "type").text = self.type
        ElementTree.SubElement(el, "weight").text = self.weight
        ElementTree.SubElement(el, "heading").text = self.heading
        ElementTree.SubElement(el, "attunement").text = self.attunement
        ElementTree.SubElement(el, "rarity").text = self.rarity
        ElementTree.SubElement(el, "value").text = self.value
        ElementTree.SubElement(el, "property").text = self.property
        ElementTree.SubElement(el, "dmg1").text = self.dmg1
        ElementTree.SubElement(el, "dmg2").text = self.dmg2
        ElementTree.SubElement(el, "dmgType").text = self.dmgType
        ElementTree.SubElement(el, "range").text = self.range
        ElementTree.SubElement(el, "ac").text = self.ac
        ElementTree.SubElement(el, "source").text = self.source
        ElementTree.SubElement(el, "text").text = self.text
