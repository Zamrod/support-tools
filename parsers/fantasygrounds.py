import logging
import os
import re
import shutil
from bs4 import BeautifulSoup
from xml.etree import ElementTree

from natsort import humansorted
from slugify import slugify

from models import Group, Page, Map, Marker, Encounter, Combatant, Module, Monster, Item, Spell, Trait, Action


logger = logging.getLogger(__name__)


# class helpers
class Image:
    tag = None
    name = None
    bitmap = None


class NPC:
    tag = None
    name = None


class FantasyGrounds:

    def cleanup_html(self, nodes):
        text = ""
        for node in nodes:
            html = ElementTree.tostring(node, encoding='utf-8', method='xml').decode('utf-8').replace("\\r", "\n")
            soup = BeautifulSoup(html, 'html.parser')
            for h in soup.findAll('h'):
                new_tag = soup.new_tag("b")
                new_tag.string = str.format("{}\n", h.string)
                h.replaceWith(new_tag)
            for p in soup.findAll('p'):
                p.replaceWith(str.format("{}\n", p.text))
            for td in soup.findAll('td'):
                td.replaceWith(str.format("{}\t\t\t", td.text))
            for tr in soup.findAll('tr'):
                tr.replaceWith(str.format("{}\n", tr.text))
            for table in soup.findAll('table'):
                table.replaceWith(str.format("{}\n", table.text))
            for li in soup.findAll('li'):
                li.replaceWith(str.format("-\t{}\n", li.text))
            for list_node in soup.findAll('list'):
                list_node.replaceWith(str.format("{}\n", list_node.text))
            text = str.format("{}{}", text, soup.prettify())
        return text

    def parse_xml(self, path, module, compendium):
        logger.debug("parsing xml: %s", path)

        # lookup tables
        lookup = {}
        lookup["encounter"] = {}
        lookup["page"] = {}
        lookup["map"] = {}
        lookup["image"] = {}
        lookup["npc"] = {}
        lookup["quest"] = {}
        lookup["monster"] = {}
        lookup["spell"] = {}
        lookup["item"] = {}
        lookup["imagedata"] = {}
        lookup["tokens"] = {}

        # arrays
        pages = []
        maps = []
        groups = []
        encounters = []
        monsters = []
        items = []
        spells = []

        # xml tree
        tree = ElementTree.parse(path)
        root = tree.getroot()
        working_dir = os.path.dirname(path)

        monsters_dir = os.path.join(working_dir, "monsters")
        if os.path.exists(monsters_dir):
            shutil.rmtree(monsters_dir)

        # # tokens
        # tokens_dir = os.path.join(working_dir, "tokens")
        # if os.path.exists(tokens_dir):
        #     shutil.copytree(tokens_dir, monsters_dir)

        # image data
        for category in root.findall("./reference/imagedata/category"):
            for node in category.findall("*"):
                tag = node.tag
                name = node.find("name").text
                slug = slugify(name)
                bitmap = node.find("image").find("bitmap").text.replace("\\", "/")

                source = os.path.join(working_dir, bitmap)
                target_filename = os.path.basename(source)
                target_dir = os.path.join(working_dir, "monsters")
                if not os.path.exists(target_dir):
                    os.mkdir(target_dir)
                target = os.path.join(target_dir, target_filename)
                shutil.copyfile(source, target)
                lookup["imagedata"][tag] = target_filename

        logger.info("%s images", len(lookup["imagedata"]))

        # tags = {}
        # for category in root.findall("./reference/spelldata"):
        #     for node in category.findall("*"):
        #         for subnode in node.findall("*"):
        #             if tags.__contains__(subnode.tag):
        #                 pre_value = tags[subnode.tag]
        #             else:
        #                 pre_value = 0
        #             tags[subnode.tag] = pre_value + 1
        # logger.info("::TAGS Dump Start::")
        # for tag_key in tags.keys():
        #     logger.info("%s: %s", tag_key, tags[tag_key])
        # logger.info("::TAGS Dump End::\n")

        logger.info("parsing spells")
        for category in root.findall("./reference/spelldata"):
            for node in category.findall("*"):
                tag = node.tag
                name = node.find("name").text
                spell = Spell()
                spell.name = name
                spell.slug = slugify(name)
                spell.level = node.find("level").text
                spell.school = node.find("school").text.upper()[0:1]
                spell.classes = node.find("source").text
                spell.time = node.find("castingtime").text
                spell.range = node.find("range").text
                spell.duration = node.find("duration").text
                spell.components = node.find("components").text
                ritual_node = node.find("ritual")
                if ritual_node is not None:
                    spell.ritual = "YES"
                spell.text = self.cleanup_html(node.findall("description/*"))
                spell.source = compendium.slug
                spells.append(spell)
                compendium.spells.append(spell)
                lookup["spell"][tag] = spell

        logger.info("%s spells", len(spells))

        for category in root.findall("./reference/equipmentdata"):
            for node in category.findall("*"):
                tag = node.tag
                name = node.find("name").text

                item = Item()
                item.name = name
                item.slug = slugify(name)
                lookup["item"][tag] = item
                items.append(item)
                compendium.items.append(item)

        logger.info("%s items", len(items))


        # monsters
        logger.info("parsing monsters")
        for category in root.findall("./reference/npcdata"):
            for node in category.findall("*"):
                tag = node.tag
                name = node.find("name").text

                monster = Monster()
                monster.name = name
                monster.slug = slugify(name)
                # monster.image = node.find("token").text.split("\\")[1].split("@")[0]
                monster.type = node.find("type").text
                monster.size = node.find("size").text[:1].upper()
                ac = node.find("ac").text
                actext = node.find("actext").text
                monster.ac = ac
                if actext is not None:
                    monster.ac = "{} {}".format(ac, actext)
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

                sensestext = node.find("senses").text
                monster.senses = sensestext
                if "passive perception" in sensestext.lower():
                    index = sensestext.lower().find("passive perception")
                    senses = sensestext[0:index]
                    passive = sensestext[index + 19:]
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
                    trait.text = trait_node.find("desc").text.replace("\\r", "\n")
                    monster.traits.append(trait)

                for action_node in node.findall("actions/*"):
                    action = Action()
                    action.name = action_node.find("name").text
                    action.text = action_node.find("desc").text.replace("\\r", "\n")
                    monster.actions.append(action)

                for action_node in node.findall("lairactions/*"):
                    action = Action()
                    action.name = "{} [Lair Action]".format(action_node.find("name").text)
                    action.text = action_node.find("desc").text.replace("\\r", "\n")
                    monster.actions.append(action)

                for legendary_action_node in node.findall("legendaryactions/*"):
                    action = Action()
                    action.name = legendary_action_node.find("name").text
                    action.text = legendary_action_node.find("desc").text.replace("\\r", "\n")
                    monster.legendaries.append(action)

                for reaction_node in node.findall("reactions/*"):
                    action = Action()
                    action.name = reaction_node.find("name").text
                    action.text = reaction_node.find("desc").text.replace("\\r", "\n")
                    monster.reactions.append(action)

                for innatespells_node in node.findall("innatespells/*"):
                    monster.spells.append(innatespells_node.find("name").text.split(" (")[0].split(" -")[0].lower())

                for spells_node in node.findall("spells/*"):
                    monster.spells.append(spells_node.find("name").text.split(" (")[0].split(" -")[0].lower())

                monster.description = self.cleanup_html(node.findall("text/*"))

                # for description in node.findall("text/*"):
                #
                #     if html.startswith('<link class="imagewindow"'):
                #         img_ref = description.attrib["recordname"]
                #         img_ref = img_ref[20:-2]
                #         monster.image = lookup["imagedata"][img_ref]
                #         continue
                #     if html.startswith('<list>'):
                #         html = html.replace('<list>', '').replace('</list>', '')
                #         html = html.replace('<li>', '\n-\t').replace('</li>', '')
                #     html = html.replace('<p>', '').replace('</p>', '\n')
                #     html = html.replace('<h>', '<b>').replace('</h>', '</b>\n')
                #     html = html.replace('<b><i>', '<b>').replace('</i></b>', '</b>')
                #
                #     monster.description = '{}{}'.format(monster.description, html)
                #     .replace("\\r", "\n")
                #     # logger.info("%s: %s", description, html)

                lookup["monster"][tag] = monster
                monsters.append(monster)
                compendium.monsters.append(monster)
        logger.info("%s monsters", len(monsters))

        # NPCS
        logger.info("parsing npcs")

        for category in root.findall("./npc/category"):
            for node in category.findall("*"):
                tag = node.tag
                name = node.find("name").text

                npc = NPC()
                npc.name = name
                lookup["npc"][tag] = npc

        # PAGES
        logger.info("parsing pages")

        parent = Group()
        parent.name = "Story"
        parent.slug = slugify(parent.name)
        groups.append(parent)

        for category in root.findall("./encounter/category"):

            group = Group()
            group.name = category.get("name")
            group.slug = slugify(group.name)
            group.parent = parent

            if group.name == None or group.name == "":
                group = parent
            else:
                groups.append(group)

            # get all pages
            for node in category.findall("*"):
                # tag 
                tag = node.tag

                # create page
                page = Page()
                page.meta["tag"] = tag
                page.name = node.find("name").text
                page.slug = slugify(page.name)
                page.content = ElementTree.tostring(node.find("text"), encoding='utf-8', method='xml').decode('utf-8')
                page.parent = group

                pages.append(page)
                lookup["page"][tag] = page

        # QUESTS
        logger.info("parsing quests")

        parent = Group()
        parent.name = "Quests"
        parent.slug = slugify(parent.name)
        groups.append(parent)

        # some modules got, so use this instead
        for node in root.findall("./quest/*/*"):
            # for node in root.findall("./quest/*"):
            # tag 
            tag = node.tag

            # create quest
            page = Page()
            page.meta["tag"] = id
            page.name = node.find("name").text
            page.slug = slugify(page.name)

            page.content = ElementTree.tostring(node.find("description"), encoding='utf-8', method='xml').decode(
                'utf-8')

            cr = node.find("cr").text if node.find("cr") else ""
            xp = node.find("xp").text if node.find("xp") else ""

            page.content += '<p><strong>CR:</strong> ' + cr + ' <strong>XP:</strong> ' + xp + '</p>'
            page.parent = parent

            pages.append(page)
            lookup["quest"][tag] = page

        # sort
        pages_sorted = humansorted(pages, key=lambda x: x.name)

        # MAPS & IMAGES
        logger.info("parsing images and maps")

        parent = Group()
        parent.name = "Maps & Images"
        parent.slug = slugify(parent.name)
        groups.append(parent)

        for category in root.findall("./image/category"):
            group = Group()
            group.name = category.get("name")
            group.slug = slugify(group.name)
            group.parent = parent

            if group.name == None or group.name == "":
                group = parent
            else:
                groups.append(group)

            for node in category.findall("*"):
                # tag 
                tag = node.tag

                # create image
                image = Image()
                image.tag = tag
                image.bitmap = node.find("./image/bitmap").text.replace("\\", "/")
                image.name = node.find("name").text

                lookup["image"][tag] = image

                markers = []

                # get shortcouts (markers)
                for shortcut in node.findall("./image/shortcuts/shortcut"):
                    # create marker
                    marker = Marker()
                    marker.x = shortcut.find("x").text
                    marker.y = shortcut.find("y").text

                    shortcut_ref = shortcut.find("recordname").text.replace("encounter.", "").replace("@*", "")
                    page = None
                    if shortcut_ref in lookup["page"]:
                        page = lookup["page"][shortcut_ref]

                        # remove chapter numbers from page name
                        # maybe use a regex?
                        name = page.name
                        if " " in page.name:
                            first, second = page.name.split(' ', 1)
                            if "." in first:
                                name = second

                        marker.name = name
                        marker.contentRef = "/page/" + page.slug

                    markers.append(marker)

                if markers:
                    # if markers not empty, its a map
                    map = Map()
                    map.parent = group
                    map.meta["tag"] = tag
                    map.name = image.name
                    map.slug = slugify(map.name)
                    map.image = image.bitmap
                    if node.find("./image/gridsize") != None:
                        map.gridSize = node.find("./image/gridsize").text
                    if node.find("./image/gridoffset") != None:
                        gridOffset = node.find("./image/gridoffset").text
                        map.gridOffsetX = gridOffset.split(",")[0]
                        map.gridOffsetY = gridOffset.split(",")[1]
                    map.markers = markers

                    maps.append(map)
                    lookup["map"][tag] = map
                else:
                    # otherwise, its a image
                    page = Page()
                    page.parent = group
                    page.meta["tag"] = tag
                    page.name = image.name
                    page.slug = slugify(page.name)
                    page.content = '<p><img class="size-full" src="' + image.bitmap + '" /></p>'

                    pages_sorted.append(page)
                    # do not add to lookup tables

        # sort
        maps_sorted = humansorted(maps, key=lambda x: x.name)

        # ENCOUNTERS
        logger.info("parsing encounters")

        parent = Group()
        parent.name = "Encounters"
        parent.slug = slugify(parent.name)
        groups.append(parent)

        for category in root.findall("./battle/category"):
            group = Group()
            group.name = category.get("name")
            group.slug = slugify(group.name)
            group.parent = parent

            if group.name == None or group.name == "":
                group = parent
            else:
                groups.append(group)

            for node in category.findall("*"):
                # tag
                tag = node.tag

                # create encounter
                encounter = Encounter()
                encounter.meta["tag"] = tag
                encounter.parent = group

                encounter.name = node.find("name").text
                encounter.slug = slugify(encounter.name)

                encounters.append(encounter)
                lookup["encounter"][tag] = encounter

                # get combatants
                for npcnode in node.find("npclist").findall("*"):

                    # get positions
                    maplinks = npcnode.findall("./maplink/*")

                    # combatants count
                    count = int(npcnode.find("count").text)

                    # iterate
                    for x in range(count):
                        combatant = Combatant()
                        combatant.name = npcnode.find("name").text
                        encounter.combatants.append(combatant)

                        # if position on map
                        if len(maplinks) == count:
                            maplinknode = maplinks[x]

                            if maplinknode.find("./imagex") != None:
                                combatant.x = maplinknode.find("./imagex").text

                            if maplinknode.find("./imagey") != None:
                                combatant.y = maplinknode.find("./imagey").text

        encounters_sorted = humansorted(encounters, key=lambda x: x.name)

        # custom regex for processing links
        def href_replace(match):
            key = str(match.group(2)).split("@")[0]

            type = match.group(1)

            if type == "image" and key in lookup["map"]:
                return 'href="/map/' + lookup["map"][key].slug
            elif type == "image" and key in lookup["image"]:
                return 'href="' + lookup["image"][key].bitmap
            elif type == "encounter" and key in lookup["page"]:
                return 'href="' + lookup["page"][key].slug
            elif type == "battle" and key in lookup["encounter"]:
                return 'href="/encounter/' + lookup["encounter"][key].slug
            elif type == "quest" and key in lookup["quest"]:
                return 'href="' + lookup["quest"][key].slug
            else:
                return key

        # fix content tags in pages
        for page in pages_sorted:
            content = page.content
            # maybe regex 
            content = content.replace('<text type="formattedtext">', '').replace('<text>', '').replace('</text>', '')
            content = content.replace('<description type="formattedtext">', '').replace('<description>', '').replace(
                '</description>', '')
            content = content.replace('<frame>', '<blockquote class="read">').replace('</frame>', '</blockquote>')
            content = content.replace('<frameid>DM</frameid>', '')
            content = content.replace('\r', '<br />')
            content = content.replace('<h>', '<h3>').replace('</h>', '</h3>')
            content = content.replace('<list>', '<ul>').replace('</list>', '</ul>')
            # content = content.replace("<linklist>", "<ul>").replace("</linklist>", "</ul>")
            content = content.replace('<linklist>', '').replace('</linklist>', '')
            content = content.replace('<link', '<p><a').replace('</link>', '</a></p>')
            content = content.replace(' recordname', ' href')
            content = content.strip()

            # fix links
            content = re.sub(r'href=[\'"]?(encounter|battle|image|quest)\.([^\'">]+)', href_replace, content)

            # add title
            if content.startswith('<h3>'):
                page.content = content.replace('<h3>', '<h2>', 1).replace('</h3>', '</h2>', 1)
            else:
                page.content = '<h2>' + page.name + '</h2>' + content

        # assign data to module
        module.groups = groups
        module.pages = pages_sorted
        module.maps = maps_sorted
        module.encounters = encounters_sorted

        return module

    def process_mod(self, path, module, compendium):
        # path info
        basename = os.path.basename(path)
        dirname = os.path.dirname(path)
        unpacked_dir = os.path.join(dirname, module.slug)

        # unpack archive
        logger.info("unpacking archive: %s", basename)
        shutil.unpack_archive(path, unpacked_dir, "zip")

        # convert db.xml to module.xml
        xml_file = os.path.join(unpacked_dir, "db.xml")
        client_xml_file = os.path.join(unpacked_dir, "client.xml")

        if os.path.exists(xml_file):
            # parse data
            self.parse_xml(xml_file, module, compendium)

            # create dst
            moduleDst = os.path.join(unpacked_dir, "module.xml")
            compendiumDst = os.path.join(unpacked_dir, "compendium.xml")

            # export xml
            module.export_xml(moduleDst)
            compendium.export_xml(compendiumDst)

        elif os.path.exists(client_xml_file):
            # parse data
            self.parse_xml(client_xml_file, module, compendium)

            # create dst
            moduleDst = os.path.join(unpacked_dir, "module.xml")
            compendiumDst = os.path.join(unpacked_dir, "compendium.xml")

            # export xml
            module.export_xml(moduleDst)
            compendium.export_xml(compendiumDst)
        else:
            raise ValueError("db.xml not found")

        # create archive
        Module.create_archive(unpacked_dir, module.slug)

        return module

    def process(self, path, module, compendium):
        # path info
        basename = os.path.basename(path)
        ext = os.path.splitext(basename)[1]

        # file check
        if not os.path.isfile(path):
            raise ValueError('Path must be a file')

        # extension check
        if ext == ".mod":
            # .mod file
            self.process_mod(path, module, compendium)
        elif ext == ".xml":
            # .xml file
            self.parse_xml(path, module, compendium)
        else:
            raise ValueError('Invalid path')
