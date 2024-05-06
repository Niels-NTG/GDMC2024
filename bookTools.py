import functools
import json
import re
from typing import Dict, List

from glm import ivec3
from pylatexenc.latex2text import latex2text

import globals
from gdpc.src.gdpc import Block, minecraft_tools

if __name__ == '__main__':
    globals.initialize()


@functools.cache
def categoryGroup(category: str) -> str:
    # Computer science
    if category.startswith('cs.'):
        return 'Computer Science'
    # Economics
    if category.startswith('econ'):
        return 'Economics'
    # Electrical Engineering and Systems Science
    if category.startswith('eess'):
        return 'Electrical Engineering and Systems Science'
    # Mathematics
    if category.startswith('math'):
        return 'Mathematics'
    # Physics
    if (
        category.startswith('astro-ph') or
        category.startswith('cond-mat') or
        category.startswith('gr-qc') or
        category.startswith('hep-') or
        category.startswith('nlin') or
        category.startswith('nucl-') or
        category.startswith('physics') or
        category.startswith('quant')
    ):
        return 'Physics'
    # Quantitative Biology
    if category.startswith('q-bio'):
        return 'Quantitative Biology'
    # Quantitative Finance
    if category.startswith('q-fin'):
        return 'Quantitative Finance'
    # Statistics
    if category.startswith('stat'):
        return 'Statistics'


@functools.cache
def categoryColor(category: str) -> str:
    # Computer science -> green
    if category.startswith('cs.'):
        return '§a'
    # economics -> blue
    if category.startswith('econ'):
        return '§9'
    # Electrical Engineering and Systems Science -> yellow
    if category.startswith('eess'):
        return '§e'
    # Math -> dark green
    if category.startswith('math'):
        return '§2'
    # Physics -> dark purple
    if (
        category.startswith('astro-ph') or
        category.startswith('cond-mat') or
        category.startswith('gr-qc') or
        category.startswith('hep-') or
        category.startswith('nlin') or
        category.startswith('nucl-') or
        category.startswith('physics') or
        category.startswith('quant')
    ):
        return '§5'
    # Quantitative Biology -> aqua
    if category.startswith('q-bio'):
        return '§b'
    # Quantitative Finance -> dark blue
    if category.startswith('q-fin'):
        return '§1'
    # Statistics -> red
    if category.startswith('stat'):
        return '§c'
    return '§f'


def categoriesHeader(data: Dict) -> str:
    s = '§n'
    for category in data['categories'].split(' '):
        s += categoryColor(category) + category + '§r, '
    return s[:-2] + '§r'


def lastVersionYear(data: Dict) -> str:
    return '§7' + re.sub(r'^\w\w\w,\s\d+\s\w\w\w\s|\s.+$', '', data['versions'][-1]['created']) + '§r'


def truncatedBookTitle(data: Dict) -> str:
    title = data['authors_parsed'][0][0]
    if len(data['authors_parsed']) > 1:
        title += ' et al.'
    if len(title) > 25:
        title = title[:25] + '…'
    title += ' (' + lastVersionYear(data) + ')'
    return title


def authorsHeader(data: Dict) -> str:
    s = '§8§o'
    for author in data['authors_parsed']:
        s += f'{author[2]} {author[1]} {author[0]}'.strip() + '\n'
    return re.sub(r' {2,}', '', s).strip() + '§r'


def firstPage(data: Dict) -> str:
    s = categoriesHeader(data) + '\n'
    s += '§6§l' + sanitizeForBook(entry['title']) + '§r\n\n'
    s += authorsHeader(data) + '\n\n'
    s += lastVersionYear(data) + '\f'
    return s


def lastPage(data: Dict) -> str:
    s = ''
    if data['id']:
        s += 'arXiv:§c§n' + data['id'] + '§r\n\n'
    if data['doi']:
        s += 'DOI:§6§n' + data['doi'] + '§r\n\n'
    if data['journal-ref']:
        s += 'Journal reference:§1§n' + data['journal-ref'] + '§r\n\n'
    if len(data['versions']):
        s += 'Version:§7' + data['versions'][-1]['version'] + ' (' + data['versions'][-1]['created'] + ')§r\n\n'
    if data['comments']:
        s += '\fComments: §7§o' + sanitizeForBook(data['comments']) + '§r\n\n'
    return s.strip()


def bookAuthors(data: Dict) -> str:
    authors = []
    for author in data['authors_parsed']:
        authors.append(f'{author[2]} {author[1]} {author[0]}'.strip())
    return re.sub(r' {2,}', '', '; '.join(authors)).strip()


def sanitizeForBook(s: str) -> str:
    s = re.sub(r'\s\s', '', re.sub(r'[\n\r]+', ' ', s)).strip()
    try:
        s = latex2text(s)
    except:
        print(f'latex2text: {s}')
    try:
        s = s.encode('raw_unicode_escape').decode('unicode_escape')
    except UnicodeDecodeError:
        print(f'UnicodeDecodeError: {s}')
    return s


def writeBookData(data: Dict) -> str:
    return minecraft_tools.bookData(
        '\\\\s' + firstPage(data) +
        sanitizeForBook(data['abstract']) + '§r\f' +
        '\\\\s' + lastPage(data),
        # NOTE title cam be max 32 charachters
        title=truncatedBookTitle(data),
        author=bookAuthors(data),
        description='arXiv:' + data['id'],
        desccolor='red',
    )


def fillBookShelf(bookSources: List[Dict], block: Block) -> Block:
    if len(bookSources) > 6:
        print('Too many book sources provided at once!')
        return block
    shelfSNBT = '{Items: ['
    for slowIndex in range(6):
        book = writeBookData(bookSources[slowIndex])
        shelfSNBT += f'{{Slot: {slowIndex}b, Count: 1b, id: "minecraft:written_book", tag: {book}}},'
    shelfSNBT = shelfSNBT[:-1]
    shelfSNBT += ']}'
    block.data = shelfSNBT
    return block


# TODO entries in file are sorted by ArXiv ID. Think of a better sorting system.
with open('dataset/arxiv-metadata-oai-snapshot.json') as f:
    bookShelfEntries: List[Dict] = []
    pos = ivec3(globals.buildarea.begin)
    bookCount = 0
    facing = 'north'

    for line in f:
        entry = json.loads(line)
        # print(entry)
        bookShelfEntries.append(entry)
        if len(bookShelfEntries) == 6:
            pos.x = pos.x + 1
            if pos.x > globals.buildarea.end.x:
                pos.y = pos.y + 1
                pos.x = globals.buildarea.begin.x

            bookShelfBlock = Block(
                id='minecraft:chiseled_bookshelf',
                states={
                    'facing': facing,
                    'slot_0_occupied': 'true',
                    'slot_1_occupied': 'true',
                    'slot_2_occupied': 'true',
                    'slot_3_occupied': 'true',
                    'slot_4_occupied': 'true',
                    'slot_5_occupied': 'true',
                }
            )
            bookshelfBlock = fillBookShelf(bookShelfEntries, bookShelfBlock)
            globals.editor.placeBlockGlobal(block=bookshelfBlock, position=pos)
            bookShelfEntries = []
        bookCount += 1
