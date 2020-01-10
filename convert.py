#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse
import logging
import sys
import uuid

from slugify import slugify
from models import Module, Compendium
from parsers.fantasygrounds import FantasyGroundsParser

# parse arguments
parser = argparse.ArgumentParser(description="Convert existing modules to Encounter+ compatible file")
parser.add_argument("path", metavar="PATH", help="a path to .mod, .xml, .db3 file to convert")
parser.add_argument("--parser", default="fg", help="data parser (fg)")
parser.add_argument("--debug", action="store_true", default=False, help="enable debug logs")
parser.add_argument("--name", help="name")
parser.add_argument("--author", help="author")
parser.add_argument("--cover", help="cover image")
parser.add_argument("--code", help="short code")
parser.add_argument("--id", help="id")
args = parser.parse_args()

# setup logging
if args.debug:
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
else:
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    # create module
    module = Module()
    module.id = args.id or str(uuid.uuid4())
    module.name = args.name or "Unknown"
    module.slug = slugify(module.name)
    module.author = args.author or "Unknown"
    module.code = args.code
    module.image = args.cover or "Cover.jpg"

    # create compendium
    compendium = Compendium()
    compendium.id = args.id or str(uuid.uuid4())
    compendium.name = args.name or "Unknown"
    compendium.slug = slugify(compendium.name)
    compendium.author = args.author or "Unknown"
    compendium.code = args.code
    compendium.image = args.cover or "Cover.jpg"

    # create data parser
    dp = None

    if args.parser == "fg":
        # FantasyGrounds
        dp = FantasyGroundsParser()
        module.description = "Converted from FG"
        compendium.description = "Converted from FG"

    # process data in path
    dp.process(args.path, compendium, module)
