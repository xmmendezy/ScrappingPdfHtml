#!/usr/bin/env python3

import os
import sys
import re
from io import StringIO, TextIOWrapper
from typing import BinaryIO, List, Dict, Set
from pathlib import Path
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import HTMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from bs4 import BeautifulSoup

HOME = str(Path.home())
ASSETS = './assets'
FILE: TextIOWrapper
TAGS = ["p", "h1", "h2", "h3", "h4", "h5", "h6"]
RE_SIMPLE = re.compile('^SEÑOR[A]? [a-zA-Z\u00C0-\u017F\s()]+.-')

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
    if not os.path.exists(ASSETS):
        os.makedirs(ASSETS)
    paths_html, paths_pdf = search_files(args['path'])
    if len(paths_html) + len(paths_pdf):
        output_file = f'{args["search"]}.txt'
        FILE = open(os.path.join(HOME, output_file), 'w+')
        FILE.truncate(0)
        FILE.write(f'******** {args["search"]} ************\n\n')
        FILE.write(f'******** HTML ************\n\n')
        search_in_html(paths_html, args['search'])
        FILE.write(f'******** PDF ************\n\n')
        search_in_pdf(paths_pdf, args['search'])
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
    return text


def plain_text(text: str) -> str:
    return text.replace(
        ' ', '').replace(
        '\n', '').replace(
        '\t', '')


def search_in_html(files: List[str], search: str):
    search = prepare_text(search.replace('(', '\(').replace(')', '\)'))
    re_search = re.compile(f'^SEÑOR[A]? {search}.-')
    print('Procesando archivos html........', end="\r")
    for file in files:
        with open(file, 'rb') as fp:
            soup = BeautifulSoup(fp, 'html.parser')
            parts = soup.find_all(lambda tag: tag.name in TAGS and re_search.match(prepare_text(tag.text)))
            for p in parts:
                p_i = p
                is_next = True
                while is_next:
                    write_file(p_i.text + '\n')
                    p_i = p_i.findNext(TAGS)
                    if p_i:
                        if RE_SIMPLE.match(p_i.text):
                            is_next = False
                    else:
                        is_next = False
                write_file('\n\n')


def search_in_pdf(files: List[str], search: str):
    search = prepare_text(search.replace('(', '\(').replace(')', '\)'))
    re_search = re.compile(f'^SEÑOR[A]? {search}.-')
    print('Procesando archivos pdf........', end="\r")
    for file in files:
        with open(file, 'rb') as fp:
            html = pdftohtml(fp)
            soup = BeautifulSoup(html, 'html.parser')
            parts = soup.find_all(lambda tag: tag.name in TAGS and re_search.match(prepare_text(tag.text)))
            for p in parts:
                p_i = p
                is_next = True
                while is_next:
                    write_file(p_i.text + '\n')
                    p_i = p_i.findNext(TAGS)
                    if p_i:
                        if RE_SIMPLE.match(p_i.text):
                            is_next = False
                    else:
                        is_next = False
                write_file('\n\n')


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
