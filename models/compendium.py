import logging
import os
import shutil
import uuid
from xml.etree import ElementTree

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Compendium:

    def __init__(self):

        self.id = str(uuid.uuid4())
        self.name = "Unknown compendium"
        self.slug = "unknown-compendium"

        self.monsters = []
        self.spells = []
        self.items = []

    def export_xml(self, path):

        # create compendium
        compendium = ElementTree.Element("compendium")

        # monster
        for monster in self.monsters:
            monster.export_xml(compendium)

        # spells
        for spell in self.spells:
            spell.export_xml(compendium)

        # items
        for item in self.items:
            item.export_xml(compendium)

        tree = ElementTree.ElementTree(compendium)
        tree.write(path, encoding="utf-8", xml_declaration=True)

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
