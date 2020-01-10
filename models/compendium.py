import logging
import os
import shutil
import uuid
import vkbeautify as vkb
from xml.etree import ElementTree

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Compendium:

    def __init__(self):
        self.id = str(uuid.uuid4())
        self.name = "Unknown compendium"
        self.slug = "unknown-compendium"
        self.description = None
        self.author = None
        self.monsters = []
        self.spells = []
        self.items = []
        self.images = []

    def export_xml(self, path):

        # create compendium
        compendium_node = ElementTree.Element("compendium")

        ElementTree.SubElement(compendium_node, "name").text = self.name
        ElementTree.SubElement(compendium_node, "slug").text = self.slug

        if self.description:
            ElementTree.SubElement(compendium_node, "description").text = self.description

        if self.author:
            ElementTree.SubElement(compendium_node, "author").text = self.author

        # spells
        for spell in self.spells:
            spell.export_xml(compendium_node)

        # items
        for item in self.items:
            item.export_xml(compendium_node)

        # monster
        for monster in self.monsters:
            monster.export_xml(compendium_node)

        tree = ElementTree.ElementTree(compendium_node)
        tree.write(path, encoding="utf-8", xml_declaration=True)

        working_dir = os.path.dirname(path)
        pretty_output = os.path.join(working_dir, "compendium_pretty.xml")
        ugly_text = ElementTree.tostring(tree.getroot(), encoding='utf-8', method='xml').decode('utf-8')
        pretty_text = vkb.xml(ugly_text)  # return String
        vkb.xml(pretty_text, pretty_output)  # save in file


    def create_archive(src, name):
        # copy assets
        logger.debug("copying assets")
        current_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
        assets_src = os.path.join(current_dir, "assets")
        assets_dst = os.path.join(src, "assets")

        # remove exising assets dir
        if os.path.exists(assets_dst):
            shutil.rmtree(assets_dst)

        # copy assets
        shutil.copytree(assets_src, assets_dst)

        # create archive
        logger.info("creating archive")
        parent_dir = os.path.dirname(src)
        archive_file = os.path.join(parent_dir, name)

        shutil.make_archive(archive_file, 'zip', src)

        # rename
        os.rename(archive_file + ".zip", archive_file + ".compendium")
