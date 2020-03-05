# -*- coding: utf-8 -*-
import inspect
import os
from datetime import datetime, date
import yaml
import numpy as np

from pylatex import Package, Document, Command, NewPage, LineBreak, \
    PageStyle, Head, Foot, \
    Section, Subsection, \
    Tabular, Math, TikZ, Axis, Plot, Figure, Matrix, Alignat
from pylatex.utils import italic, NoEscape

try:
    # IHEClassInitError, IHEStringError, IHETypeError, IHEKeyError, IHEFileError
    from .exception import IHEClassInitError
except ImportError:
    from IHEWAreport.exception import IHEClassInitError


class Template(object):
    """This Base class

    Load base.yml file.

    Args:
        product (str): Product name of data products.
        is_print (bool): Is to print status message.
    """
    def __init__(self, conf):
        """Class instantiation
        """
        template = 'FAO.yml'
        path = os.path.join(
            os.getcwd(),
            os.path.dirname(
                inspect.getfile(
                    inspect.currentframe()))
        )
        self.path = ''
        self.data = {}
        self.doc = None
        self.__conf = conf

        data = self._conf(path, template)
        if len(data.keys()) > 0:
            self.path = path
            self.data = data
        else:
            raise IHEClassInitError(template) from None

        doc = self.create()
        if doc is not None:
            self.doc = doc

            self.write_cover_page('CoverPage')
            self.write_title_page('FirstPage')

            self.write_toc_page('TOCPage')

            self.set_page('ContentPage')
            self.write_preamble_page('PreamblePage')
            self.write_section_page('SectionPage')

            self.saveas()
            # self.close()

    def _conf(self, path, template) -> dict:
        data = {}

        file_conf = os.path.join(path, template)
        with open(file_conf) as fp:
            data = yaml.load(fp, Loader=yaml.FullLoader)

        return data

    def create(self) -> object:
        opt_geometry = self.data['layout']
        doc = Document(geometry_options=opt_geometry)
        doc.packages.append(Package('ragged2e'))
        doc.packages.append(Package('hyperref'))

        return doc

    def set_page(self, sname):
        opt_header = self.data['page']['header']
        if 'header' in self.__conf['data']['page'].keys():
            if self.__conf['data']['page']['header'] is not None:
                opt_header = self.__conf['data']['page']['header']

        opt_footer = self.data['page']['footer']
        if 'footer' in self.__conf['data']['page'].keys():
            if self.__conf['data']['page']['footer'] is not None:
                opt_footer = self.__conf['data']['page']['footer']

        doc_header = PageStyle(sname)

        with doc_header.create(Head('L')):
            self.page_header(doc_header, opt_header['left'])
        with doc_header.create(Head('C')):
            self.page_header(doc_header, opt_header['center'])
        with doc_header.create(Head('R')):
            self.page_header(doc_header, opt_header['right'])

        with doc_header.create(Foot('L')):
            self.page_header(doc_header, opt_footer['left'])
        with doc_header.create(Foot('C')):
            self.page_header(doc_header, opt_footer['center'])
        with doc_header.create(Foot('R')):
            self.page_header(doc_header, opt_footer['right'])

        self.doc.append(Command('clearpage'))
        # self.doc.append(NoEscape(r'\setcounter{page}{1}'))
        self.doc.append(Command('setcounter', ['page', '1']))

        self.doc.preamble.append(doc_header)
        self.doc.change_document_style(sname)

    def page_header(self, obj, txt):
        if txt == 'page_number':
            obj.append(Command('thepage'))
        elif txt == 'simple_page_number':
            from pylatex import simple_page_number
            obj.append(simple_page_number())
        else:
            obj.append(txt)

    def write_cover_page(self, sname):
        # fmt_date = "%d %b %Y"

        opt = self.data['content']['cover']
        if 'cover' in self.__conf['data']['content'].keys():
            if self.__conf['data']['content']['cover'] is not None:
                opt = self.__conf['data']['content']['cover']

        doc_page = PageStyle(sname)

        doc_page.append(opt['title'])

        doc_page.append(Command('thispagestyle', 'empty'))
        self.doc.preamble.append(doc_page)
        self.doc.change_document_style(sname)

    def write_title_page(self, sname):
        fmt_date = "%d %b %Y"
        self.doc.append(NewPage())

        opt = self.data['content']['title']
        if 'title' in self.__conf['data']['content'].keys():
            if self.__conf['data']['content']['title'] is not None:
                opt = self.__conf['data']['content']['title']

        doc_page = PageStyle(sname)

        doc_page.append(Command('title', opt['title']))
        doc_page.append(Command('author', opt['author']))
        if isinstance(opt['date'], str):
            doc_page.append(
                Command('date',
                        datetime.strptime(opt['date'],
                                          '%Y-%m-%d').strftime(fmt_date)))
        elif isinstance(opt['date'], date):
            doc_page.append(
                Command('date',
                        opt['date'].strftime(fmt_date)))
        elif isinstance(opt['date'], datetime):
            doc_page.append(
                Command('date',
                        opt['date'].strftime(fmt_date)))
        else:
            doc_page.append(
                Command('date',
                        NoEscape(r'\today')))
        doc_page.append(Command('maketitle'))

        doc_page.append(Command('thispagestyle', 'empty'))
        self.doc.preamble.append(doc_page)
        self.doc.change_document_style(sname)

    def write_toc_page(self, sname):
        self.doc.append(NewPage())

        doc_page = PageStyle(sname)

        doc_page.append(Command('tableofcontents'))

        doc_page.append(Command('thispagestyle', 'empty'))
        self.doc.preamble.append(doc_page)
        self.doc.change_document_style(sname)

    def write_preamble_page(self, sname):
        page_keys = ['acknowledgement', 'abbreviation', 'summary']

        for key in page_keys:
            self.doc.append(NewPage())
            self.doc.append(Command('RaggedRight'))
            print('Writing {}'.format(key))

            opt = self.data['content'][key]
            with self.doc.create(Section(opt['title'], numbering=False)):
                for i in opt['paragraph'].keys():
                    self.doc.append(opt['paragraph'][i])
                    self.doc.append(LineBreak())

    def write_section_page(self, sname):
        opt = self.data['content']['section']
        try:
            opt_txt = self.__conf['data']['content']['section']['text']
            opt_val = self.__conf['data']['content']['section']['value']
            opt_equ = self.__conf['data']['content']['section']['equation']
            opt_fig = self.__conf['data']['content']['section']['figure']
            opt_tab = self.__conf['data']['content']['section']['table']
            opt_ref = self.__conf['data']['content']['section']['reference']
        except KeyError:
            raise KeyError

        # print(opt_content)
        for key, val in opt.items():
            self.doc.append(NewPage())
            self.doc.append(Command('RaggedRight'))
            print('Writing {}'.format(key))

            subkey = list(val.keys())
            # print(type(subkey), subkey)
            sec_t = val['title']
            sec_p = val['paragraph']
            subkey.remove('title')
            subkey.remove('paragraph')

            with self.doc.create(Section(sec_t)):
                for key_p, val_p in sec_p.items():
                    self.doc.append(val_p.format_map(opt_val))
                    self.doc.append(LineBreak())

                subval = val[subkey[0]]

                subsubkey = list(subval.keys())
                # print(type(subsubkey), subsubkey)
                subsec_t = subval['title']
                subsec_p = subval['paragraph']
                subsubkey.remove('title')
                subsubkey.remove('paragraph')

                print('  Writing {}'.format(subkey[0]))
                with self.doc.create(Subsection(subsec_t)):
                    for subkey_p, subval_p in subsec_p.items():
                        self.doc.append(subval_p.format_map(opt_val))
                        self.doc.append(LineBreak())

    def saveas(self):
        fname = self.__conf['data']['doc']['name']
        ftypes = self.__conf['data']['doc']['saveas']

        file = os.path.join(self.__conf['path'], '{n}'.format(n=fname))
        file_with_ext = '{}.{}'.format(file, 'tex'.lower())
        print('Saving: "{}"'.format(file_with_ext))
        if os.path.isfile(file_with_ext):
            try:
                os.remove(file_with_ext)
            except PermissionError as err:
                print('Could not delete file.')
                os._exit(1)
        self.doc.generate_tex(file)

        for ftype in ftypes:
            file_with_ext = '{}.{}'.format(file, str(ftype).lower())
            print('Saving: "{}"'.format(file_with_ext))
            if str(ftype).upper() == 'PDF':
                if os.path.isfile(file_with_ext):
                    try:
                        os.remove(file_with_ext)
                    except PermissionError as err:
                        print('Could not delete file.')
                        os._exit(1)
                self.doc.generate_pdf(file, clean_tex=False)

    def close(self):
        if self.doc is not None:
            self.doc = None
