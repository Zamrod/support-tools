import logging
import os
import re
import shutil
from xml.etree import ElementTree
from slugify import slugify
from models import Monster, Item, Spell, Trait, Action, Image
from parsers.fantasygrounds.cleanup_tools import CleanupTools

logger = logging.getLogger(__name__)


class CompendiumParser:
    def __init__(self):
        # lookup tables
        self.lookup = {
            "monster": {},
            "spell": {},
            "item": {},
            "image_data": {},
            "tokens": {}
        }

    def parse_images(self, reference_node, working_dir):
        images = []
        logger.info("parsing image data")
        for category in reference_node.findall("imagedata/*"):
            logger.debug("Image Category: %s", category.attrib["name"])
            for node in category.findall("*"):
                tag = node.tag
                name = node.find("name").text
                image = Image()
                image.tag = tag
                image.name = name
                image.slug = slugify(name)
                bitmap = node.find("image").find("bitmap").text.replace("\\", "/")
                source = os.path.join(working_dir, bitmap)
                image.source_path = source
                images.append(image)
                self.lookup["image_data"][tag] = image

        logger.info("%s images", len(images))
        return images

    def parse_spells(self, reference_node, source):
        spells = []
        logger.info("parsing spells")
        for node in reference_node.findall("spelldata/*"):
            tag = node.tag
            name = node.find("name").text
            spell = Spell()
            spell.name = name
            spell.slug = slugify(name)
            spell.level = node.find("level").text
            spell.school = node.find("school").text
            spell.classes = node.find("source").text
            spell.time = node.find("castingtime").text
            spell.range = node.find("range").text
            spell.duration = node.find("duration").text
            spell.components = node.find("components").text
            ritual_node = node.find("ritual")
            if ritual_node is not None:
                spell.ritual = "YES"
            spell.text = CleanupTools.cleanup_html(node.findall("description/*"))
            spell.text = str.format("{}\n<i>Source: {}</i>\n", spell.text, source)
            spell.source = source
            self.lookup["spell"][tag] = spell
            spells.append(spell)

        logger.info("%s spells", len(spells))

        return spells

    def parse_items(self, reference_node, source):
        items = []
        logger.info("parsing items")
        for node in reference_node.findall("equipmentdata/*"):
            tag = node.tag
            name = node.find("name").text
            item = Item()
            item.name = name
            item.slug = slugify(name)
            item.type = node.find("subtype").text[0:1].upper()
            item.value = node.find("cost").text
            ac_node = node.find("ac")
            if ac_node is not None:
                item.ac = ac_node.text
            weight_node = node.find("weight")
            if weight_node is not None:
                item.weight = weight_node.text
            item.text = CleanupTools.cleanup_html(node.findall("description/*"))
            properties_node = node.find("properties")
            if properties_node is not None:
                item.property = properties_node.text
            damage_node = node.find("damage")
            if damage_node is not None:
                damage_nodes = damage_node.text.split(" ")
                item.dmg1 = damage_nodes[0]
                if len(damage_nodes) > 1:
                    item.dmgType = damage_nodes[1]

            self.lookup["item"][tag] = item
            items.append(item)
        logger.info("%s items", len(items))
        return items

    def parse_monsters(self, reference_node, source):
        monsters = []
        logger.info("parsing monsters")
        logger.info(reference_node)
        for node in reference_node.findall("category/*"):
            tag = node.tag
            name = node.find("name").text
            logger.info("parsing monster: " + name)

            # if not name.__contains__("Mind Flayer"):
            #     continue

            monster = Monster()
            monster.name = name
            monster.slug = slugify(name)
            monster.type = node.find("type").text
            monster.size = node.find("size").text[:1].upper()
            ac = node.find("ac").text
            ac_text = node.find("actext").text
            monster.ac = ac
            if ac_text is not None:
                monster.ac = "{} {}".format(ac, ac_text)
            hp = node.find("hp").text
            hd = node.find("hd").text
            monster.hp = hp
            if hd is not None:
                monster.hp = "{} {}".format(hp, hd)
            monster.speed = node.find("speed").text
            monster.str = node.find("abilities").find("strength").find("score").text
            monster.dex = node.find("abilities").find("dexterity").find("score").text
            monster.con = node.find("abilities").find("constitution").find("score").text
            monster.int = node.find("abilities").find("intelligence").find("score").text
            monster.wis = node.find("abilities").find("wisdom").find("score").text
            monster.cha = node.find("abilities").find("charisma").find("score").text

            savingthrows = node.find("savingthrows")
            if savingthrows is not None:
                monster.save = savingthrows.text

            skills = node.find("skills")
            if skills is not None:
                monster.skill = skills.text

            senses_text = node.find("senses").text
            monster.senses = senses_text
            if "passive perception" in senses_text.lower():
                index = senses_text.lower().find("passive perception")
                senses = senses_text[0:index]
                passive = senses_text[index + 19:]
                monster.senses = senses
                monster.passive = passive
            monster.alignment = node.find("alignment").text
            monster.languages = node.find("languages").text
            monster.cr = node.find("cr").text

            conditionimmunities_node = node.find("conditionimmunities")
            if conditionimmunities_node is not None:
                monster.conditionImmune = conditionimmunities_node.text

            damageresistances_node = node.find("damageresistances")
            if damageresistances_node is not None:
                monster.resist = damageresistances_node.text

            damageimmunities_node = node.find("damageimmunities")
            if damageimmunities_node is not None:
                monster.immune = damageimmunities_node.text

            damagevulnerabilities_node = node.find("damagevulnerabilities")
            if damagevulnerabilities_node is not None:
                monster.vulnerable = damagevulnerabilities_node.text

            for trait_node in node.findall("traits/*"):
                trait = Trait()
                trait.name = trait_node.find("name").text
                trait.text = trait_node.find("desc").text
                if (trait.text):
                    trait.text = trait.text.replace("\\r", "\n")
                monster.traits.append(trait)

            for action_node in node.findall("actions/*"):
                action = Action()
                action.name = action_node.find("name").text
                action.text = action_node.find("desc").text
                if (action.text):
                    action.text = action.text.replace("\\r", "\n")
                monster.actions.append(action)

            for action_node in node.findall("lairactions/*"):
                action = Action()
                action.name = "{} [Lair Action]".format(action_node.find("name").text)
                action.text = action_node.find("desc").text
                if (action.text):
                    action.text = action.text.replace("\\r", "\n")
                monster.actions.append(action)

            for legendary_action_node in node.findall("legendaryactions/*"):
                action = Action()
                action.name = legendary_action_node.find("name").text
                action.text = legendary_action_node.find("desc").text
                if (action.text):
                    action.text = action.text.replace("\\r", "\n")
                monster.legendaries.append(action)

            for reaction_node in node.findall("reactions/*"):
                action = Action()
                action.name = reaction_node.find("name").text
                action.text = reaction_node.find("desc").text
                if (action.text):
                    action.text = action.text.replace("\\r", "\n")
                monster.reactions.append(action)

            for innatespells_node in node.findall("innatespells/*"):
                monster.spells.append(innatespells_node.find("name").text.split(" (")[0].split(" -")[0].lower())

            for spells_node in node.findall("spells/*"):
                monster.spells.append(spells_node.find("name").text.split(" (")[0].split(" -")[0].lower())

            monster_description = CleanupTools.cleanup_html(node.findall("text/*"))
            monster.description = monster_description
            monster.description = str.format("{}\n<i>Source: {}</i>\n", monster.description, source)

            # parsed the linked image
            for description in node.findall("text/*"):
                if description.tag == 'link':
                    img_ref = description.attrib["recordname"]
                    img_ref = img_ref[20:-2]
                    if self.lookup["image_data"].keys().__contains__(img_ref):
                        monster.image = self.lookup["image_data"][img_ref]
                    break

            monster.source = source
            self.lookup["monster"][tag] = monster
            monsters.append(monster)
        logger.info("%s monsters", len(monsters))
        return monsters

    def fixup_images(self, collection, output_dir):
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        for item in collection:
            if item.image is not None:
                target_file = os.path.join(output_dir, item.image.filename())
                shutil.copy(item.image.source_path, target_file)

    def parse_xml(self, path, compendium_dir, compendium):
        logger.debug("parsing xml: %s", path)

        tree = ElementTree.parse(path)
        working_dir = os.path.dirname(path)
        reference_node = tree.find("./reference")

        # parse images
        compendium.images = self.parse_images(reference_node, working_dir)
    
        # parse spells
        compendium.spells = self.parse_spells(reference_node, compendium.name)

        # parse items
        # compendium.items = self.parse_items(reference_node, compendium.name)

        # parse monsters
        reference_node = tree.find("./npc")
        compendium.monsters = self.parse_monsters(reference_node, compendium.name)

        monster_image_dir = os.path.join(compendium_dir, "monsters")
        self.fixup_images(compendium.monsters, monster_image_dir)

        # load back up list of known spells from 5e
        known_spells = []
        if len(compendium.spells) == 0:
            __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
            known_spells_path = os.path.join(__location__, "known_spells.txt")
            with open(known_spells_path) as f:
                for line in f:
                    known_spells.append(line.rstrip('\n'))

        for monster in compendium.monsters:
            if monster.spells is not None and len(monster.spells) > 0:
                for monster_trait in monster.traits:
                    if monster_trait.name.lower().__contains__("spellcasting"):
                        for monster_spell in monster.spells:
                            regex = str.format("([ .,;:]+)({})([ .,;:\n]+)", monster_spell)
                            monster_trait.text = re.sub(regex, r"\1<spell>\2</spell>\3", monster_trait.text)

        return compendium

    @staticmethod
    def parse_fields(root, node_path, first_level_only):
        tags = {}
        for category in root.findall(node_path):
            if not first_level_only:
                for node in category.findall("*"):
                    for sub_node in node.findall("*"):
                        if tags.__contains__(sub_node.tag):
                            pre_value = tags[sub_node.tag]
                        else:
                            pre_value = 0
                        tags[sub_node.tag] = pre_value + 1
            else:
                if tags.__contains__(category.tag):
                    pre_value = tags[category.tag]
                else:
                    pre_value = 0
                tags[category.tag] = pre_value + 1

        logger.info("::TAGS Dump Start::")
        for tag_key in tags.keys():
            if str.endswith(tag_key, "data"):
                logger.info("%s: %s", tag_key, tags[tag_key])
        logger.info("::TAGS Dump End::\n")

