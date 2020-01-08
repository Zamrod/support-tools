from xml.etree import ElementTree


class Trait:
    def __init__(self):
        self.name = None
        self.text = None


class Action:
    def __init__(self):
        self.name = None
        self.text = None


class Monster:
    def __init__(self):
        self.name = None
        self.slug = None
        self.description = ""
        self.size = None
        self.type = None
        self.alignment = None
        self.ac = None
        self.hp = None
        self.speed = None
        self.str = None
        self.dex = None
        self.con = None
        self.int = None
        self.wis = None
        self.cha = None
        self.role = "enemy"
        self.save = None
        self.skill = None
        self.immune = None
        self.conditionImmune = None
        self.vulnerable = None
        self.resist = None
        self.senses = None
        self.passive = None
        self.languages = None
        self.cr = None
        self.image = None
        self.environment = None
        self.traits = []
        self.actions = []
        self.legendaries = []
        self.reactions = []
        self.spells = []

    def export_xml(self, compendium):
        el = ElementTree.SubElement(compendium, "monster")
        ElementTree.SubElement(el, "name").text = self.name
        ElementTree.SubElement(el, "slug").text = self.slug
        ElementTree.SubElement(el, "size").text = self.size
        ElementTree.SubElement(el, "type").text = self.type
        ElementTree.SubElement(el, "alignment").text = self.alignment
        ElementTree.SubElement(el, "ac").text = self.ac
        ElementTree.SubElement(el, "hp").text = self.hp
        ElementTree.SubElement(el, "speed").text = self.speed
        ElementTree.SubElement(el, "str").text = self.str
        ElementTree.SubElement(el, "dex").text = self.dex
        ElementTree.SubElement(el, "con").text = self.con
        ElementTree.SubElement(el, "int").text = self.int
        ElementTree.SubElement(el, "wis").text = self.wis
        ElementTree.SubElement(el, "cha").text = self.cha
        ElementTree.SubElement(el, "role").text = self.role
        ElementTree.SubElement(el, "save").text = self.save
        ElementTree.SubElement(el, "skill").text = self.skill
        ElementTree.SubElement(el, "immune").text = self.immune
        ElementTree.SubElement(el, "conditionImmune").text = self.conditionImmune
        ElementTree.SubElement(el, "vulnerable").text = self.vulnerable
        ElementTree.SubElement(el, "resist").text = self.resist
        ElementTree.SubElement(el, "senses").text = self.senses
        ElementTree.SubElement(el, "passive").text = self.passive
        ElementTree.SubElement(el, "languages").text = self.languages
        ElementTree.SubElement(el, "cr").text = self.cr
        ElementTree.SubElement(el, "spells").text = str.join(", ", self.spells)
        ElementTree.SubElement(el, "image").text = self.image
        ElementTree.SubElement(el, "description").text = self.description
        #sElementTree.SubElement(el, "environment").text = self.environment

        for trait in self.traits:
            trait_el = ElementTree.SubElement(el, "trait")
            ElementTree.SubElement(trait_el, "name").text = trait.name
            ElementTree.SubElement(trait_el, "text").text = trait.text

        for action in self.actions:
            action_el = ElementTree.SubElement(el, "action")
            ElementTree.SubElement(action_el, "name").text = action.name
            ElementTree.SubElement(action_el, "text").text = action.text

        for legendary in self.legendaries:
            legendary_el = ElementTree.SubElement(el, "legendary")
            ElementTree.SubElement(legendary_el, "name").text = legendary.name
            ElementTree.SubElement(legendary_el, "text").text = legendary.text

        for reaction in self.reactions:
            action_el = ElementTree.SubElement(el, "reaction")
            ElementTree.SubElement(action_el, "name").text = reaction.name
            ElementTree.SubElement(action_el, "text").text = reaction.text

