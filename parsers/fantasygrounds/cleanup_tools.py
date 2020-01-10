import logging
from xml.etree import ElementTree
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class CleanupTools:

    @staticmethod
    def cleanup_html(nodes):
        text = ""
        for node in nodes:
            html = ElementTree.tostring(node, encoding='utf-8', method='xml').decode('utf-8').replace("\\r", "\n")
            soup = BeautifulSoup(html, 'html.parser')
            if html.startswith("<link"):
                continue
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
