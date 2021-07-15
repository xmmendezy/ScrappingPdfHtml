#!/usr/bin/env python3

import os
import sys
import re
from io import StringIO, TextIOWrapper
from typing import BinaryIO, List, Dict, Pattern, Set, Any
from pathlib import Path
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import HTMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from bs4 import BeautifulSoup

HOME = str(Path.home())
ASSETS = './assets'
FILE: TextIOWrapper
RE_SIMPLE = re.compile('SEÑOR[A]? [a-zA-Z\u00C0-\u017F\s()]+.-')

REPLACEMENTS = (
    ("á", "a"),
    ("é", "e"),
    ("í", "i"),
    ("ó", "o"),
    ("ú", "u"),
)


def main():
    global FILE
    args = parse_args()
    if not args.get('search', None):
        print('Sin busqueda establecida')
        return
    print('Buscando archivos...', end="\r")
    search = prepare_text(args['search'].replace('(', '\(').replace(')', '\)'))
    re_search = re.compile(f'SEÑOR[A]? {search}.-')
    if not os.path.exists(ASSETS):
        os.makedirs(ASSETS)
    paths_html, paths_pdf = search_files(args['path'])
    if len(paths_html) + len(paths_pdf):
        output_file = f'{args["search"]}.txt'
        FILE = open(os.path.join(HOME, output_file), 'w+')
        FILE.truncate(0)
        FILE.write(f'******** {args["search"]} ************\n\n')
        FILE.write(f'******** HTML ************\n\n')
        search_in_html(paths_html,re_search )
        FILE.write(f'******** PDF ************\n\n')
        search_in_pdf(paths_pdf, re_search)
        FILE.close()
        print(f'Archivo de respuesta en {os.path.join(HOME,output_file)}')
    else:
        print('Sin archivos')
        return


def requirements():
    os.system('poetry export -f requirements.txt > requirements.txt')


def parse_args() -> Dict[str, str]:
    args: Dict[str, str] = {
        'search': '',
        'path': ASSETS
    }
    args_base: Dict[str, str] = {
        's': 'search',
        'search': 'search',
        'p': 'path',
        'path': 'path'
    }
    args_list: List[str] = sys.argv[1:]
    i: int = 0
    while i < len(args_list):
        arg = args_list[i]
        if arg.startswith('-'):
            if arg.startswith('--'):
                key = arg[2:]
            else:
                key = arg[1:]
            if i + 1 < len(args_list):
                if args_list[i+1].startswith('-'):
                    i += 1
                else:
                    key = args_base.get(key, '')
                    if key:
                        args[key] = args_list[i+1]
                    i += 2
            else:
                i += 1
    return args


def search_files(path: str) -> List[List[str]]:
    paths_html: List[str] = []
    paths_pdf: List[str] = []
    for (dirpath, _, filenames) in os.walk(path):
        for filename in filenames:
            if os.path.splitext(filename)[-1].lower() == '.html':
                paths_html.append(os.path.join(dirpath, filename))
            if os.path.splitext(filename)[-1].lower() == '.pdf':
                paths_pdf.append(os.path.join(dirpath, filename))
    return [paths_html, paths_pdf]


def prepare_text(text: str) -> str:
    for a, b in REPLACEMENTS:
        text = text.replace(a, b).replace(a.upper(), b.upper())
    text = text.replace('  ', ' ').replace('  ', ' ')
    return text


def search_in_html(files: List[str], re_search: Pattern[str]):
    print('Procesando archivos html........', end="\r")
    for file in files:
        with open(file, 'rb') as fp:
            search_text(fp, re_search)


def search_in_pdf(files: List[str], re_search: Pattern[str]):
    print('Procesando archivos pdf........', end="\r")
    for file in files:
        with open(file, 'rb') as fp:
            html = pdftohtml(fp)
            search_text(html, re_search)


def search_text(html: Any, re_search: Pattern[str]):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text().replace('  ', ' ').replace('  ', ' ')
    for i, j in [(m.start(0), m.end(0)) for m in re_search.finditer(prepare_text(text))]:
        end = RE_SIMPLE.search(prepare_text(text[j:]))
        if end:
            j = j + end.start(0)
        write_file(text[i:j] + '\n')

def pdftohtml(pdf: BinaryIO):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    laparams = LAParams()
    device = HTMLConverter(rsrcmgr, retstr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    maxpages = 0
    caching = True
    pagenos: Set = set([])
    for page in PDFPage.get_pages(pdf, pagenos, maxpages=maxpages, caching=caching, check_extractable=True):
        interpreter.process_page(page)
    xml = retstr.getvalue()
    device.close()
    retstr.close()
    return xml


def write_file(text: str):
    if FILE:
        FILE.write(text)


if __name__ == '__main__':
    main()
