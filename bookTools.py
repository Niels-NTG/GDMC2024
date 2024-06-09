import functools
import json
import re
from datetime import datetime
from glob import glob
from typing import Dict, List

from pylatexenc.latex2text import latex2text

from gdpc.src.gdpc import Block, minecraft_tools


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
    return re.sub(r'^\w\w\w,\s\d+\s\w\w\w\s|\s.+$', '', data['versions'][-1]['created'])


def primaryAuthor(snbt: str) -> str:
    return re.sub(r'^.+?title:\'|(?: et al\.)? \(§7.+', '', snbt)


def truncatedBookTitle(data: Dict) -> str:
    title = data['authors_parsed'][0][0]
    if len(data['authors_parsed']) > 1:
        title += ' et al.'
    if len(title) > 25:
        title = title[:25] + '…'
    title += ' (§7' + lastVersionYear(data) + '§r)'
    return title


def authorsHeader(data: Dict) -> str:
    s = '§8§o'
    for author in data['authors_parsed']:
        s += f'{author[2]} {author[1]} {author[0]}'.strip() + '\n'
    return re.sub(r' {2,}', '', s).strip() + '§r'


def firstPage(data: Dict) -> str:
    s = categoriesHeader(data) + '\n'
    s += '§6§l' + sanitizeForBook(data['title']) + '§r\n\n'
    s += authorsHeader(data) + '\n\n'
    s += '§7' + lastVersionYear(data) + '§r\f'
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


def createBookShelfBlock(facing: str) -> Block:
    return Block(
        id='minecraft:chiseled_bookshelf',
        states={
            'facing': facing,
        },
    )


def fillBookShelf(bookSources: List[str], block: Block) -> Block:
    if len(bookSources) > 6:
        raise Exception('Too many book sources provided at once!')
    shelfSNBT = '{Items: ['
    for bookIndex in range(6):
        shelfSNBT += f'{{Slot: {bookIndex}b, Count: 1b, id: "minecraft:written_book", tag: {bookSources[bookIndex]}}},'
        block.states[f'slot_{bookIndex}_occupied'] = 'true'
    shelfSNBT = shelfSNBT[:-1]
    shelfSNBT += ']}'
    block.data = shelfSNBT
    return block


def writeCategoryFile(line: str, category: str, year: str):
    with open(f'dataset/{category}-{year}.json', 'a') as f:
        f.write(line)
        f.write('\n')


def splitByCategory():
    with open('dataset/arxiv-metadata-oai-snapshot.json') as f:
        for line in f:
            entry = json.loads(line)
            primaryCategory = entry['categories'].split(' ')[0]
            year = lastVersionYear(entry)
            bookData = writeBookData(entry)
            writeCategoryFile(bookData, primaryCategory, year)


def gatherBooksOfCategory(category: str = 'cs.') -> List[str]:
    groupedBooks = []
    startYear = 1980
    endYear = datetime.today().year
    for year in range(startYear, endYear + 1):
        bookGroup: List[str] = []
        inputFiles = glob(f'dataset/{category}*-{year}.json')
        for inputFile in inputFiles:
            with open(inputFile) as f:
                for line in f:
                    # Somewhere in the data is a bomb of 0.2 megabyte (221257 bytes).
                    # To prevent Minecraft chunk size from growing such
                    # that is crashes the game, skip all books that are
                    # over roughly 10k bytes
                    # TODO re-run book parser to trim the abstracts, notes and author lists down
                    if len(line) < 10000:
                        bookGroup.append(line)
        bookGroup.sort(key=lambda x: primaryAuthor(x))
        groupedBooks.extend(bookGroup)
    return groupedBooks
