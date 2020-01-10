import logging
import os
import shutil
from xml.etree import ElementTree

from slugify import slugify

from models import Module, Compendium
from .compendium_parser import CompendiumParser
from .module_parser import ModuleParser

logger = logging.getLogger(__name__)


class FantasyGroundsParser:

    def process_mod_file(self, path, compendium, module):
        compendium_parser = CompendiumParser()
        module_parser = ModuleParser()

        # path info
        basename = os.path.basename(path)
        dir_name = os.path.dirname(path)
        unpacked_dir = os.path.join(dir_name, str.format("{}_source", slugify(basename)))
        compendium_dir = os.path.join(dir_name, str.format("{}_compendium", slugify(basename)))
        module_dir = os.path.join(dir_name, str.format("{}_module", slugify(basename)))

        # unpack archive
        logger.info("unpacking archive: %s", basename)
        shutil.unpack_archive(path, unpacked_dir, "zip")

        if os.path.exists(compendium_dir):
            shutil.rmtree(compendium_dir)
        os.mkdir(compendium_dir)

        if os.path.exists(module_dir):
            shutil.rmtree(module_dir)
        os.mkdir(module_dir)

        client_xml_file = os.path.join(unpacked_dir, "client.xml")
        db_xml_file = os.path.join(unpacked_dir, "db.xml")

        definition_xml_file = os.path.join(unpacked_dir, "definition.xml")
        if os.path.exists(definition_xml_file):
            tree = ElementTree.parse(definition_xml_file)
            displayname_node = tree.find("displayname")
            if displayname_node is not None:
                source_name = displayname_node.text
            else:
                source_name = tree.find("name").text
            source_author = tree.find("author").text
            # module base info
            module.name = source_name
            module.slug = slugify(source_name)
            module.author = source_author
            module.image = "front_cover.jpg"
            # compendium base info
            compendium.name = source_name
            compendium.slug = slugify(source_name)
            compendium.author = source_author
            compendium.image = "front_cover.jpg"

        # convert client.xml and db.xml to compendium.xml
        if os.path.exists(client_xml_file):
            # parse data
            compendium_parser.parse_xml(client_xml_file, compendium_dir, compendium)
        if os.path.exists(db_xml_file):
            # parse data
            compendium_parser.parse_xml(db_xml_file, compendium_dir, compendium)

        # create dst
        compendium_dst = os.path.join(compendium_dir, "compendium.xml")

        # export xml
        compendium.export_xml(compendium_dst)

        # convert client.xml and db.xml to module.xml
        if os.path.exists(client_xml_file):
            # parse data
            module_parser.parse_xml(client_xml_file, module)
        if os.path.exists(db_xml_file):
            # parse data
            module_parser.parse_xml(db_xml_file, module)

        # create dst
        module_dst = os.path.join(module_dir, "module.xml")

        # export xml
        module.export_xml(module_dst)

        # create archive
        Compendium.create_archive(compendium_dir, compendium.slug)
        Module.create_archive(module_dir, module.slug)

    def process(self, path, compendium, module):

        # file check
        if not os.path.isfile(path):
            raise ValueError('Path must be a file')

        # path info
        base_dir = os.path.dirname(path)
        basename = os.path.basename(path)
        ext = os.path.splitext(basename)[1]
        working_dir = os.path.dirname(base_dir)
        working_dir = os.path.join(working_dir, "output")

        if os.path.exists(working_dir):
            shutil.rmtree(working_dir)

        # handle zip file from thetrove.net
        if ext == ".zip":
            shutil.unpack_archive(path, working_dir)
            for filename in os.listdir(working_dir):
                if filename.endswith(".mod"):
                    mod_file = os.path.join(working_dir, filename)
                    logger.info("Processing Mod File: %s", mod_file)
                    self.process_mod_file(mod_file, compendium, module)

        elif ext == ".mod":
            # .mod file
            self.process_mod_file(path, compendium, module)
        else:
            raise ValueError('Invalid path')
