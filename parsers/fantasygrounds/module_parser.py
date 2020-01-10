import logging
import os
import re
import shutil
from bs4 import BeautifulSoup
from xml.etree import ElementTree

from natsort import humansorted
from slugify import slugify

from models import Module, Monster, Item, Spell, Trait, Action


logger = logging.getLogger(__name__)


# class helpers


class NPC:
    tag = None
    name = None


class ModuleParser:

    def parse_xml(self, path, module):
        logger.debug("parsing xml: %s", path)

        return module


