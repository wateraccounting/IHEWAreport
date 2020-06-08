# -*- coding: utf-8 -*-
"""
`Document structure <https://en.wikibooks.org/wiki/LaTeX/Document_Structure>`_

"""
import inspect
import os
from datetime import datetime, date
import yaml

import matplotlib
# Not to use X server. For TravisCI.
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import numpy as np
import pandas as pd
import quantities as pq

from pylatex import \
    Package, Document, Command, NoEscape, \
    PageStyle, Head, Foot, \
    Section, Subsection, Subsubsection, NewPage, NewLine, LineBreak, \
    Itemize, \
    Label, Ref, \
    LongTabu, LongTable, MultiColumn, MultiRow, Table, Tabular, \
    TikZ, Axis, Plot, Figure, SubFigure, Alignat, \
    Math, Matrix, VectorName, Quantity

from pylatex.utils import italic, bold, make_temp_dir, rm_temp_dir

try:
    # IHEClassInitError, IHEStringError, IHETypeError, IHEKeyError, IHEFileError
    from ...exception import IHEClassInitError
except ImportError:
    from IHEWAreport.exception import IHEClassInitError


class Template(object):
    """This Base class

    Load base.yml file.

    Args:
        conf (dict): User defined configuration data from yaml file.
    """
    def __init__(self, conf):
        """Class instantiation
        """
        template = 'DataAnalysis.yml'
        path = os.path.join(
            os.getcwd(),
            os.path.dirname(
                inspect.getfile(
                    inspect.currentframe()))
        )
        self.path = ''
        self.path_temp = ''
        self.data = {}
        self.doc = None
        self.__conf = conf

        data = self._conf(path, template)
        if len(data.keys()) > 0:
            self.path = path
            self.data = data
            self.workspace = self.__conf['workspace']  # tests
            # self.path = self.__conf['path']  # tests/output
        else:
            raise IHEClassInitError(template) from None

        doc = self.create()
        if doc is not None:
            print('\nLaTex Start')
            self.path_temp = make_temp_dir()
            print('Created temp dir:', self.path_temp)

            print('>>>>>')
            # ################### #
            # Start class article #
            # ################### #
            self.doc = doc

            # Set global style
            self.doc.preamble.append(NoEscape(r'\cftsetindents{section}{0em}{3em}'))
            self.doc.preamble.append(NoEscape(r'\cftsetindents{subsection}{0em}{5em}'))
            self.doc.preamble.append(NoEscape(r'\cftsetindents{subsubsection}{0em}{7em}'))

            # ##### #
            # Cover #
            # ##### #
            # self.write_cover_page('CoverPage')
            self.write_title_page('FirstPage')

            # ######## #
            # Preamble #
            # ######## #
            # TOC
            # Opt1: no page number
            # self.write_page_toc_no_pagenumber('TOCPage')
            # self.set_page('PreambleHeader', 'roman')

            # Opt2: with Roman page number
            self.set_page('PreambleHeader', 'roman')
            self.write_page_toc('TOCPage')

            # LOT
            self.write_page_lof('LOFPage')

            # LOT
            self.write_page_lot('LOTPage')

            # self.write_page_acknowledgment('AcknowledgementPage')
            # self.write_page_abbreviation('AbbreviationPage')
            # self.write_page_summary('SummaryPage')

            # ######## #
            # Contents #
            # ######## #
            # Set Contents style
            self.set_page('SectionHeader', 'arabic')
            # doc Contents
            self.write_page_section('SectionPage')

            # ##### #
            # Tests #
            # ##### #
            # TODO, Test
            # self.write_test('TestPage')

            # ######## #
            # Appendix #
            # ######## #
            # Reference
            # self.set_page('ReferenceHeader', 'roman')
            self.write_page_reference('ReferencePage')

            # Annex
            # self.set_page('AppendixHeader', 'roman')
            self.write_page_annex('AnnexPage')
            print('<<<<<\n')

            # doc Appendix
            self.saveas()
            self.close()
            print('\nLaTex End')

            rm_temp_dir()
            print('Removed temp dir:', self.path_temp)
        else:
            raise IHEClassInitError(template) from None

    def _conf(self, path, template) -> dict:
        data = {}

        file_conf = os.path.join(path, template)
        with open(file_conf) as fp:
            data = yaml.load(fp, Loader=yaml.FullLoader)

        return data

    def create(self) -> object:
        opt_document = self.data['layout']['document']
        opt_geometry = self.data['layout']['geometry']

        doc = Document(documentclass=opt_document['class'],
                       document_options=opt_document['options'],
                       # document_options=['twoside', 'openany'],
                       geometry_options=opt_geometry)
        # Header and footer
        doc.packages.append(Package('fancyhdr'))
        # Text align
        doc.packages.append(Package('ragged2e'))

        # Toc, LoFig, LoTab
        # Error: Hyperref points Toc \contentsname to Doc-Start
        # If commit tocloft package, Hpyerref ok.
        doc.packages.append(Package('tocloft'))
        # Solution add pkg: tocbibind
        doc.packages.append(Package('tocbibind',
                                    options=[
                                        'notbib']))

        # Hyper link
        doc.packages.append(Package('hyperref',
                                    options=[
                                        'linktocpage',
                                        # 'hidelinks',
                                        'colorlinks=true',
                                        'pdfpagemode=UseOutlines',
                                        'bookmarksopen=true'
                                    ]))
        # doc.packages.append(Package('hyperref',
        #                             options=[
        #                                 'pdfencoding=auto',
        #                                 'psdextra'
        #                             ]))

        # Reference
        # sorting=ynt
        #   nty—sorts entries by name, title, year;
        #   nyt—sorts entries by name, year, title;
        #   nyvt—sorts entries by name, year, volume, title;
        #   anyt—sorts entries by alphabetic label, name, year, title;
        #   anyvt—sorts entries by alphabetic label, name, year, volume, title;
        #   ynt—sorts entries by year, name, title;
        #   ydnt—sorts entries by year (descending order), name, title;
        #   none—no sorting. Entries appear in the order they appear in the text.
        doc.packages.append(Package('biblatex',
                                    options=[
                                        'style=authoryear',
                                        'sorting=ynt'
                                    ]))
        #                                 'backend=bibtex',
        # doc.packages.append(Package('natbib'))

        # Figure position
        doc.packages.append(Package('float'))

        # Math
        # doc.packages.append(Package('alphabeta'))

        # Caption
        doc.packages.append(Package('caption',
                                    options=[
                                        'format=plain',
                                        NoEscape(r'labelfont={bf,it}'),
                                        'textfont=it'
                                    ]))

        return doc

    def set_page(self, sname, ntype):
        """Set page style, re-count number.

        - Re-count page number: 1.
        - Re-count section number: 0.
        - Re-count figure number: 0.
        - Re-count table number: 0.

        Args:
            sname (str): Style name, etc, SectionHeader.
            ntype (str): Numbering style, etc Roman.
        """
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

        self.doc.append(Command('pagenumbering', ntype))
        # self.doc.append(NoEscape(r'\setcounter{page}{1}'))
        self.doc.append(Command('setcounter', ['page', '1']))

        self.doc.append(Command('setcounter', ['section', '0']))
        self.doc.append(Command('setcounter', ['figure', '0']))
        self.doc.append(Command('setcounter', ['table', '0']))

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

    def insert_plot(self, obj_sec, name, caption, width, *args, **kwargs):
        # with obj_sec.create(Figure(position='htbp!')) as plot:
        with obj_sec.create(Figure(position='H')) as plot:
            plot.add_plot(width=NoEscape(width), *args, **kwargs)
            if isinstance(caption, str):
                if len(caption) > 0:
                    plot.add_caption('{}'.format(caption))
            plot.append(Label('figure:{}'.format(name)))
            # obj_sec.append(plot)

    def insert_image(self, obj_sec, name, caption, width, file):
        with obj_sec.create(Figure(position='H')) as img:
            img.add_image(file,
                          width=NoEscape(width),
                          placement=NoEscape(r'\centering'))
            if isinstance(caption, str):
                if len(caption) > 0:
                    img.add_caption(NoEscape('{}'.format(caption)))
            img.append(Label('figure:{}'.format(name)))

    def insert_images(self, obj_sec, name, caption, width, sub_files, sub_captions):
        with obj_sec.create(Figure(position='H')) as img:
            nfiles = len(sub_files)
            sub_width = float(width) / float(nfiles)

            for i in range(nfiles):
                with obj_sec.create(
                        SubFigure(position='c',
                                  width=NoEscape(
                                      r'{}\textwidth'.format(sub_width)))) as sub_img:
                    sub_img.add_image(sub_files[i],
                                      width=NoEscape(r'\textwidth'))
                    if len(sub_captions) == nfiles:
                        sub_img.add_caption(NoEscape('{}'.format(sub_captions[i])))

            if isinstance(caption, str):
                if len(caption) > 0:
                    img.add_caption(NoEscape('{}'.format(caption)))
                    img.append(Label('figure:{}'.format(name)))

    def insert_abbre(self, obj_sec, width, data):
        # tab_style = '{}'.format(' '.join(['X[l]' for i in range(2)]))
        tab_style = 'X[l]X[l]'
        with obj_sec.create(LongTabu(tab_style)) as table:
            table.end_table_header()
            table.end_table_footer()
            table.end_table_last_footer()

            for key, val in data.items():
                table.add_row([key, val])

    def insert_table_data(self, obj_sec, name, caption, width, header, data):
        tab_style = '|{}|'.format('|'.join(['l' for i in range(data.shape[1])]))
        with obj_sec.create(LongTable(tab_style)) as table:
            # http://texdoc.net/texmf-dist/doc/latex/tools/longtable.pdf
            # Specifies rows to appear at the top the first page
            if isinstance(caption, str):
                if len(caption) > 0:
                    table.append(Command('caption',
                                         options=[],
                                         arguments=[NoEscape('{}'.format(caption))]))
                    table.append(NoEscape(r'\label{%s}\\' % 'table:{}'.format(name)))

            table.add_hline()
            table.add_row([bold(NoEscape(val)) for val in header])
            table.add_hline()
            table.append(Command('endfirsthead'))

            # Specifies rows to appear at the top of every page
            table.add_hline()
            table.add_row([NoEscape(val) for val in header])
            table.add_hline()
            table.end_table_header()

            # Specifies rows to appear at the bottom of every page
            # table.add_hline()
            # table.add_row((MultiColumn(3,
            #                            align='r',
            #                            data='Continued on Next Page'),))
            table.add_hline()
            table.end_table_footer()

            # Specifies rows to appear at the bottom of the last page
            # table.add_hline()
            # table.add_row((MultiColumn(3,
            #                            align='r',
            #                            data='Not Continued on Next Page'),))
            # table.add_hline()
            # table.end_table_last_footer()

            for i in range(data.shape[0]):
                # table.add_row(data[i])

                str_row = []
                for val in data[i]:
                    if isinstance(val, float):
                        str_row.append('{:.0f}'.format(val))
                    else:
                        str_row.append(NoEscape(val))
                table.add_row(str_row)

    def insert_table_csv(self, obj_sec, name, caption, width, file):
        # https://en.wikibooks.org/wiki/LaTeX/Tables
        # header = ['header 1', 'header 2', 'header 3']
        # data = np.array([['1', 2, 3]])

        df = pd.read_csv(file, sep=',')
        header = df.columns
        data = df.to_numpy()

        # tab_style = '|{}|'.format('|'.join(['c' for i in range(data.shape[1])]))
        tab_style = '|{}|'.format('|'.join(['l' for i in range(data.shape[1])]))

        with obj_sec.create(LongTable(tab_style)) as table:
            # http://texdoc.net/texmf-dist/doc/latex/tools/longtable.pdf
            # Specifies rows to appear at the top the first page
            if isinstance(caption, str):
                if len(caption) > 0:
                    table.append(Command('caption',
                                         options=[],
                                         arguments=[NoEscape('{}'.format(caption))]))
                    table.append(NoEscape(r'\label{%s}\\' % 'table:{}'.format(name)))

            table.add_hline()
            table.add_row([bold(NoEscape(val)) for val in header])
            table.add_hline()
            table.append(Command('endfirsthead'))

            # Specifies rows to appear at the top of every page
            table.add_hline()
            table.add_row([NoEscape(val) for val in header])
            table.add_hline()
            table.end_table_header()

            # Specifies rows to appear at the bottom of every page
            # table.add_hline()
            # table.add_row((MultiColumn(3,
            #                            align='r',
            #                            data='Continued on Next Page'),))
            table.add_hline()
            table.end_table_footer()

            # Specifies rows to appear at the bottom of the last page
            # table.add_hline()
            # table.add_row((MultiColumn(3,
            #                            align='r',
            #                            data='Not Continued on Next Page'),))
            # table.add_hline()
            # table.end_table_last_footer()

            for i in range(data.shape[0]):
                # table.add_row(data[i])

                str_row = []
                for val in data[i]:
                    if isinstance(val, float):
                        str_row.append('{:.0f}'.format(val))
                    else:
                        str_row.append(NoEscape(val))
                table.add_row(str_row)

        # with self.doc.create(Table(position="htbp")) as table:
        #     table.append(NoEscape(r'\centering'))
        #
        #     tabular = Tabular(tab_style)
        #     tabular.add_hline()
        #     tabular.add_row(["header 1", "header 2", "header 3"])
        #     tabular.add_hline()
        #
        #     for i in range(150):
        #         tabular.add_row(row)
        #     tabular.add_hline()
        #
        #     table.append(tabular)
        #     table.add_caption('Caption Table {}'.format('Caption'))
        #     table.append(Label('table:{}'.format('tab1')))

    def write_test(self, sname):
        self.doc.append(NewPage())
        with self.doc.create(Section('Test')):
            # Reference
            with self.doc.create(Subsection('Reference')):
                self.doc.append(Command('cite', options=[], arguments='bertram'))
                self.doc.append(LineBreak())
                self.doc.append(Command('cite', options=[], arguments='simon06'))
                self.doc.append(LineBreak())

            # List
            with self.doc.create(Subsection('List')) as obj_sec:
                with self.doc.create(Itemize()) as itemize:
                    itemize.add_item("the first item")
                    itemize.add_item("the second item")
                    itemize.add_item("the third etc")
                    # you can append to existing items
                    itemize.append(Command("ldots"))
                    obj_sec.append(itemize)

            # Figure, matplotlib
            with self.doc.create(Subsection('Figure plot')) as obj_sec:
                name = 'fig9998'
                caption = 'Caption Figure plot'
                self.doc.append(NoEscape('Fig. ' + Ref('figure:{}'.format(name)).dumps_as_content()))

                dpi = 3000

                x = [0, 1, 2, 3, 4, 5, 6]
                y = [15, 2, 7, 1, 5, 6, 9]
                plt.plot(x, y)

                self.insert_plot(obj_sec, name, caption, r'1\textwidth', dpi=dpi)

            # Figure, image
            with self.doc.create(Subsection('Figure image')) as obj_sec:
                name = 'fig9999'
                caption = 'Caption Figure image'
                self.doc.append(NoEscape('Fig. ' + Ref('figure:{}'.format(name)).dumps_as_content()))

                self.insert_image(obj_sec, name, caption, r'1\textwidth',
                                  file='D:/IHEProjects/Public/IHEWAdataanalysis/tests/IHEWAdataanalysis/area1/pdf/fig1a.pdf')

            # Table, multi-page LongTable
            with self.doc.create(Subsection('Talbe')) as obj_sec:
                name = 'tab1'
                caption = 'Caption Table'
                self.doc.append(NoEscape('Tab. ' + Ref('table:{}'.format(name)).dumps_as_content()))

                header = ['header 1', 'header 2', 'header 3']
                # data = np.array([['1', 2, 3]])
                data = np.zeros((50, 3))

                self.insert_table_data(obj_sec, name, caption, r'1\textwidth', header, data)

            # Math, equation, numpy
            with self.doc.create(Subsection('Equation numpy')) as obj_sec:
                name = 'equ1'
                caption = 'Caption Equation 1'
                self.doc.append(NoEscape('Equ. ' + Ref('equation:{}'.format(name)).dumps_as_content()))

                M = np.asmatrix(
                    np.array([
                        [2, 3, 4],
                        [0, 0, 1],
                        [0, 0, 2]
                    ]))
                a = np.asmatrix(
                    np.array(
                        [
                            [100, 10, 20]
                        ]).T)

                with obj_sec.create(Alignat(aligns=2,
                                            numbering=True,
                                            escape=False)) as obj_agn:
                    # vec = Matrix(a)
                    # vec_name = VectorName(name)
                    # math = Math(data=[vec_name, '=', vec])
                    # obj_sec.append(math)
                    obj_agn.append(r'\frac{a}{b} &= 0 \\')
                    obj_agn.extend([Matrix(M), Matrix(a), '&=', Matrix(M * a)])
                    obj_agn.append(Label('equation:{}'.format(name)))
                    # print(obj_agn)

            # Math, equation, quantities
            with self.doc.create(Subsection('Equation quantities')) as obj_sec:
                name = 'equ2'
                self.doc.append(NoEscape('Equ. ' + Ref('equation:{}'.format(name)).dumps_as_content()))

                with obj_sec.create(Alignat(aligns=2,
                                            numbering=True,
                                            escape=False)) as obj_agn:
                    G = pq.constants.Newtonian_constant_of_gravitation
                    moon_earth_distance = 384400 * pq.km
                    moon_mass = 7.34767309e22 * pq.kg
                    earth_mass = 5.972e24 * pq.kg
                    moon_earth_force = G * moon_mass * earth_mass / moon_earth_distance ** 2
                    q1 = Quantity(moon_earth_force.rescale(pq.newton),
                                  options={
                                      'round-precision': 4,
                                      'round-mode': 'figures'})
                    # math = Math(data=['F=', q1])
                    # obj_sec.append(math)

                    obj_agn.extend(['F', '&=', q1])
                    obj_agn.append(Label('equation:{}'.format(name)))
                    # print(obj_agn)

        # self.doc.append(NewPage())
        self.doc.append(Command('clearpage'))
        # self.doc.append(Command('cleardoublepage'))

    def write_cover_page(self, sname):
        # fmt_date = "%d %b %Y"

        key = 'cover'
        print('{}'.format(key))

        opt = self.data['content'][key]
        if key in self.__conf['data']['content'].keys():
            if self.__conf['data']['content'][key] is not None:
                opt = self.__conf['data']['content'][key]

        doc_page = PageStyle(sname)

        doc_page.append(opt['title'])

        doc_page.append(Command('thispagestyle', 'empty'))
        self.doc.preamble.append(doc_page)
        self.doc.change_document_style(sname)
        # self.doc.append(NewPage())
        self.doc.append(Command('clearpage'))
        self.doc.append(Command('cleardoublepage'))

    def write_title_page(self, sname):
        fmt_date = "%d %b %Y"
        self.doc.append(NewPage())

        key = 'title'
        print('{}'.format(key))

        opt = self.data['content'][key]
        if key in self.__conf['data']['content'].keys():
            if self.__conf['data']['content'][key] is not None:
                opt = self.__conf['data']['content'][key]

        doc_page = PageStyle(sname)

        doc_page.append(Command('title', NoEscape(opt['title'])))
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
        # self.doc.append(NewPage())
        self.doc.append(Command('clearpage'))
        self.doc.append(Command('cleardoublepage'))

    def write_page_toc_no_pagenumber(self, sname):
        self.doc.append(NewPage())

        key = 'toc'
        print('{}'.format(key))

        doc_page = PageStyle(sname)
        doc_page.append(Command('tableofcontents'))
        doc_page.append(Command('thispagestyle', 'empty'))

        self.doc.preamble.append(doc_page)
        self.doc.change_document_style(sname)
        # self.doc.append(NewPage())
        self.doc.append(Command('clearpage'))
        self.doc.append(Command('cleardoublepage'))

    def write_page_toc(self, sname):
        self.doc.append(NewPage())

        key = 'toc'
        print('{}'.format(key))

        # # self.doc.append(NoEscape(r'\pdfbookmark[0]{\contentsname}{toc}'))  # Chapter
        # self.doc.append(NoEscape(r'\pdfbookmark[1]{\contentsname}{toc}'))  # Section
        # self.doc.append(Command('tableofcontents'))

        self.doc.append(Command('tableofcontents'))
        # pkg: tocbibind
        # self.doc.append(Command('addcontentsline',
        #                         ['toc', 'section', NoEscape(r'\contentsname')]))

        # self.doc.append(NewPage())
        self.doc.append(Command('clearpage'))
        self.doc.append(Command('cleardoublepage'))

    def write_page_lof(self, sname):
        self.doc.append(NewPage())

        key = 'lof'
        print('{}'.format(key))

        # self.doc.append(NoEscape(r'\pdfbookmark[1]{Figures}{lof}'))  # Section
        # self.doc.append(Command('listoffigures'))

        self.doc.append(Command('listoffigures'))
        # pkg: tocbibind
        # self.doc.append(Command('addcontentsline',
        #                         ['toc', 'section', NoEscape(r'\listfigurename')]))

        # self.doc.append(NewPage())
        self.doc.append(Command('clearpage'))
        self.doc.append(Command('cleardoublepage'))

    def write_page_lot(self, sname):
        self.doc.append(NewPage())

        key = 'lot'
        print('{}'.format(key))

        # self.doc.append(NoEscape(r'\pdfbookmark[1]{Tables}{lot}'))  # Section
        # self.doc.append(Command('listoftables'))

        self.doc.append(Command('listoftables'))
        # pkg: tocbibind
        # self.doc.append(Command('addcontentsline',
        #                         ['toc', 'section', NoEscape(r'\listtablename')]))

        # self.doc.append(NewPage())
        self.doc.append(Command('clearpage'))
        self.doc.append(Command('cleardoublepage'))

    def write_page_acknowledgment(self, sname):
        self.doc.append(NewPage())
        self.doc.append(Command('RaggedRight'))

        key = 'acknowledgement'
        print('{}'.format(key))

        opt = self.data['content'][key]
        with self.doc.create(Section(NoEscape(opt['title']), numbering=False)):
            for i in opt['paragraph'].keys():
                self.doc.append(opt['paragraph'][i])
                self.doc.append(LineBreak())

        self.doc.append(Command('addcontentsline',
                                ['toc', 'section', opt['title']]))

        # self.doc.append(NewPage())
        self.doc.append(Command('clearpage'))
        # self.doc.append(Command('cleardoublepage'))

    def write_page_abbreviation(self, sname):
        self.doc.append(NewPage())
        self.doc.append(Command('RaggedRight'))

        key = 'abbreviation'
        print('{}'.format(key))

        opt = self.data['content'][key]
        with self.doc.create(Section(NoEscape(opt['title']), numbering=False)) as obj_sec:
            self.insert_abbre(obj_sec, r'1\textwidth', opt['paragraph'])

        self.doc.append(Command('addcontentsline',
                                ['toc', 'section', opt['title']]))

        # self.doc.append(NewPage())
        self.doc.append(Command('clearpage'))
        self.doc.append(Command('cleardoublepage'))

    def write_page_summary(self, sname):
        self.doc.append(NewPage())
        self.doc.append(Command('RaggedRight'))

        key = 'summary'
        print('{}'.format(key))

        opt = self.data['content'][key]
        with self.doc.create(Section(NoEscape(opt['title']), numbering=False)):
            for i in opt['paragraph'].keys():
                self.doc.append(opt['paragraph'][i])
                self.doc.append(LineBreak())

        self.doc.append(Command('addcontentsline',
                                ['toc', 'section', opt['title']]))

        # self.doc.append(NewPage())
        self.doc.append(Command('clearpage'))
        self.doc.append(Command('cleardoublepage'))

    def write_page_section(self, sname):
        self.doc.append(NewPage())
        self.doc.append(Command('RaggedRight'))

        key = 'section'
        print('{}'.format(key))

        opt = self.data['content'][key]
        try:
            opt_sect = self.__conf['data']['content'][key]
            opt_data = self.__conf['data']['content']['data']
        except KeyError:
            raise KeyError

        # print(opt_content)
        for key_l1 in opt.keys():
            val_l1 = opt[key_l1]
            # val_l1_keys = val_l1.keys()
            val_l1_t = val_l1['title']
            val_l1_p = val_l1['paragraph']
            print(' {} {}'.format(key_l1, val_l1_t))

            with self.doc.create(Section(NoEscape(val_l1_t))) as obj_sec_l1:
                for tmp_key_l1, tmp_val_l1 in val_l1_p.items():
                    # print('  {}'.format(tmp_key_l1))

                    # self.doc.append(val.format_map(opt_data))
                    if isinstance(tmp_val_l1, dict):
                        type_l1 = tmp_val_l1['type']

                        if type_l1 == 'list':
                            items = tmp_val_l1['item']

                            with obj_sec_l1.create(Itemize()) as itemize:
                                for iitem, item in items.items():
                                    try:
                                        tmp_str_para = item.format(data=opt_data)
                                    except KeyError:
                                        tmp_str_para = item
                                    itemize.add_item(tmp_str_para)
                                    itemize.append(Command("ldots"))
                                # obj_sec_l1.append(itemize)

                        if type_l1 == 'equation':
                            pass

                        if type_l1 == 'figure':
                            name = tmp_val_l1['name']

                            dir = opt_data[type_l1]['dir']

                            if 'main' in opt_data[type_l1][name].keys():
                                caption = opt_data[type_l1][name]['caption'].format(data=opt_data)

                                fname = opt_data[type_l1][name]['main']['fname']
                                width = opt_data[type_l1][name]['main']['width']

                                file = os.path.join(self.workspace, dir, fname)
                                self.insert_image(obj_sec_l1,
                                                  name,
                                                  caption,
                                                  r'{}\textwidth'.format(width),
                                                  file)
                            if 'sub' in opt_data[type_l1][name].keys():
                                caption = opt_data[type_l1][name]['caption'].format(data=opt_data)
                                width = opt_data[type_l1][name]['width']

                                sub_files = []
                                sub_captions = []
                                for key, sub_img in opt_data[type_l1][name]['sub'].items():
                                    sub_files.append(os.path.join(self.workspace, dir, sub_img['fname']))
                                    sub_captions.append(sub_img['caption'])

                                self.insert_images(obj_sec_l1,
                                                   name,
                                                   caption,
                                                   r'{}'.format(width),
                                                   sub_files,
                                                   sub_captions)

                        if type_l1 == 'table':
                            name = tmp_val_l1['name']

                            dir = opt_data[type_l1]['dir']

                            fname = opt_data[type_l1][name]['fname']
                            caption = opt_data[type_l1][name]['caption'].format(data=opt_data)
                            width = opt_data[type_l1][name]['width']

                            file = os.path.join(self.workspace, dir, fname)
                            self.insert_table_csv(obj_sec_l1,
                                                  name,
                                                  caption,
                                                  r'1\textwidth',
                                                  file)

                        if type_l1 == 'reference':
                            pass
                    else:
                        if tmp_val_l1[0] == '{' and tmp_val_l1[-1] == '}':
                            tmp_val_l1 = tmp_val_l1.format(data=opt_data)

                        try:
                            tmp_str_para = tmp_val_l1.format(data=opt_data)
                        except KeyError:
                            tmp_str_para = tmp_val_l1

                        try:
                            self.doc.append(NoEscape(tmp_str_para.format(data=opt_data)))
                        except KeyError:
                            self.doc.append(NoEscape(tmp_str_para))
                        finally:
                            self.doc.append(LineBreak())

                # key_l2 = val_l1.keys()
                # key_l2.remove('title')
                # key_l2.remove('paragraph')
                for key_l2 in val_l1.keys():
                    if key_l2 != 'title' and key_l2 != 'paragraph':

                        val_l2 = val_l1[key_l2]
                        val_l2_t = val_l2['title']
                        val_l2_p = val_l2['paragraph']

                        with self.doc.create(Subsection(NoEscape(val_l2_t))) as obj_sec_l2:
                            for tmp_key_l2, tmp_val_l2 in val_l2_p.items():
                                print('  {}'.format(tmp_key_l2))

                                # self.doc.append(val.format_map(opt_data))
                                if isinstance(tmp_val_l2, dict):
                                    type_l2 = tmp_val_l2['type']

                                    if type_l2 == 'list':
                                        items = tmp_val_l2['item']

                                        with obj_sec_l2.create(Itemize()) as itemize:
                                            for iitem, item in items.items():
                                                try:
                                                    tmp_str_para = item.format(data=opt_data)
                                                except KeyError:
                                                    tmp_str_para = item
                                                itemize.add_item(tmp_str_para)
                                                itemize.append(Command("ldots"))
                                            # obj_sec_l2.append(itemize)

                                    if type_l2 == 'equation':
                                        pass

                                    if type_l2 == 'figure':
                                        name = tmp_val_l2['name']

                                        dir = opt_data[type_l2]['dir']

                                        if 'main' in opt_data[type_l2][name].keys():
                                            caption = opt_data[type_l2][name]['caption'].format(data=opt_data)

                                            fname = opt_data[type_l2][name]['main']['fname']
                                            width = opt_data[type_l2][name]['main']['width']

                                            file = os.path.join(self.workspace, dir, fname)
                                            self.insert_image(obj_sec_l2,
                                                              name,
                                                              caption,
                                                              r'{}\textwidth'.format(width),
                                                              file)
                                        if 'sub' in opt_data[type_l2][name].keys():
                                            caption = opt_data[type_l2][name]['caption'].format(data=opt_data)
                                            width = opt_data[type_l2][name]['width']

                                            sub_files = []
                                            sub_captions = []
                                            for key, sub_img in opt_data[type_l2][name]['sub'].items():
                                                sub_files.append(os.path.join(self.workspace, dir, sub_img['fname']))
                                                sub_captions.append(sub_img['caption'])

                                            self.insert_images(obj_sec_l2,
                                                               name,
                                                               caption,
                                                               r'{}'.format(width),
                                                               sub_files,
                                                               sub_captions)

                                    if type_l2 == 'table':
                                        name = tmp_val_l2['name']

                                        dir = opt_data[type_l2]['dir']

                                        fname = opt_data[type_l2][name]['fname']
                                        caption = opt_data[type_l2][name]['caption'].format(data=opt_data)
                                        width = opt_data[type_l2][name]['width']

                                        file = os.path.join(self.workspace, dir, fname)
                                        self.insert_table_csv(obj_sec_l2,
                                                              name,
                                                              caption,
                                                              r'1\textwidth',
                                                              file)

                                    if type_l2 == 'reference':
                                        pass
                                else:
                                    if tmp_val_l2[0] == '{' and tmp_val_l2[-1] == '}':
                                        tmp_val_l2 = tmp_val_l2.format(data=opt_data)

                                    try:
                                        tmp_str_para = tmp_val_l2.format(data=opt_data)
                                    except KeyError:
                                        tmp_str_para = tmp_val_l2

                                    try:
                                        self.doc.append(NoEscape(tmp_str_para.format(data=opt_data)))
                                    except KeyError:
                                        self.doc.append(NoEscape(tmp_str_para))
                                    finally:
                                        self.doc.append(LineBreak())

                            # key_l3 = val_l2.keys()
                            # key_l3.remove('title')
                            # key_l3.remove('paragraph')
                            for key_l3 in val_l2.keys():
                                if key_l3 != 'title' and key_l3 != 'paragraph':

                                    val_l3 = val_l2[key_l3]
                                    val_l3_t = val_l3['title']
                                    val_l3_p = val_l3['paragraph']

                                    with self.doc.create(Subsubsection(NoEscape(val_l3_t))) as obj_sec_l3:
                                        for tmp_key_l3, tmp_val_l3 in val_l3_p.items():
                                            if isinstance(tmp_val_l3, dict):
                                                type_l3 = tmp_val_l3['type']

                                                if type_l3 == 'list':
                                                    items = tmp_val_l3['item']

                                                    with obj_sec_l3.create(Itemize()) as itemize:
                                                        for iitem, item in items.items():
                                                            try:
                                                                tmp_str_para = item.format(data=opt_data)
                                                            except KeyError:
                                                                tmp_str_para = item
                                                            itemize.add_item(tmp_str_para)
                                                            itemize.append(Command("ldots"))
                                                        # obj_sec_l3.append(itemize)

                                                if type_l3 == 'equation':
                                                    pass

                                                if type_l3 == 'figure':
                                                    name = tmp_val_l3['name']

                                                    dir = opt_data[type_l3]['dir']

                                                    if 'main' in opt_data[type_l3][
                                                        name].keys():
                                                        caption = opt_data[type_l3][name]['caption'].format(data=opt_data)

                                                        fname = opt_data[type_l3][name]['main']['fname']
                                                        width = opt_data[type_l3][name]['main']['width']

                                                        file = os.path.join(self.workspace, dir, fname)
                                                        self.insert_image(obj_sec_l3,
                                                                          name,
                                                                          caption,
                                                                          r'{}\textwidth'.format(
                                                                              width),
                                                                          file)
                                                    if 'sub' in opt_data[type_l3][name].keys():
                                                        caption = opt_data[type_l3][name]['caption'].format(data=opt_data)
                                                        width = opt_data[type_l3][name]['width']

                                                        sub_files = []
                                                        sub_captions = []
                                                        for key, sub_img in opt_data[type_l3][name]['sub'].items():
                                                            sub_files.append(os.path.join(self.workspace, dir, sub_img['fname']))
                                                            sub_captions.append(sub_img['caption'])

                                                        self.insert_images(obj_sec_l3,
                                                                           name,
                                                                           caption,
                                                                           r'{}'.format(width),
                                                                           sub_files,
                                                                           sub_captions)
                                                if type_l3 == 'table':
                                                    name = tmp_val_l3['name']

                                                    dir = opt_data[type_l3]['dir']

                                                    fname = opt_data[type_l3][name]['fname']
                                                    caption = opt_data[type_l3][name]['caption'].format(data=opt_data)
                                                    width = opt_data[type_l3][name]['width']

                                                    file = os.path.join(self.workspace,
                                                                        dir, fname)
                                                    self.insert_table_csv(obj_sec_l3,
                                                                          name,
                                                                          caption,
                                                                          r'1\textwidth',
                                                                          file)

                                                if type_l3 == 'reference':
                                                    pass
                                            else:
                                                if tmp_val_l3[0] == '{' and tmp_val_l3[-1] == '}':
                                                    tmp_val_l3 = tmp_val_l3.format(data=opt_data)

                                                try:
                                                    tmp_str_para = tmp_val_l3.format(data=opt_data)
                                                except KeyError:
                                                    tmp_str_para = tmp_val_l3

                                                try:
                                                    self.doc.append(NoEscape(tmp_str_para.format(data=opt_data)))
                                                except KeyError:
                                                    self.doc.append(NoEscape(tmp_str_para))
                                                finally:
                                                    self.doc.append(LineBreak())
                # self.doc.append(NewPage())
                # self.doc.append(Command('clearpage'))
                # self.doc.append(Command('cleardoublepage'))

    def write_page_reference(self, sname):
        self.doc.append(NewPage())
        # self.doc.append(Command('RaggedRight'))

        key = 'reference'
        print('{}'.format(key))

        files = []

        opt = self.data['content'][key]
        # file = os.path.join(self.path, opt['file'])
        file = NoEscape(os.path.join(self.path, opt['file']))
        # file = os.path.join(self.path, opt['file']).replace(os.sep, '/')
        # file = NoEscape(os.path.join(self.path, opt['file']).replace(os.sep, '/'))

        # files.append(os.path.splitext(file)[0])
        # files.append(NoEscape(os.path.splitext(file)[0]))
        if key in self.__conf['data']['content'].keys():
            if 'file' in self.__conf['data']['content'][key].keys():
                opt['file'] = self.__conf['data']['content'][key]['file']
                # file = opt['file']
                file = NoEscape(opt['file'])
                # file = './{}'.format(opt['file'])
                # file = NoEscape('./{}'.format(opt['file']))

                # files.append(os.path.splitext(file)[0])
                # files.append(NoEscape(os.path.splitext(file)[0]))
        # print(files)

        self.doc.preamble.append(Command('addbibresource',
                                         options=[],
                                         arguments=[file]))
        # self.doc.preamble.append(Command('bibliography', arguments=files))

        with self.doc.create(Section(NoEscape(opt['title']), numbering=False)):
            self.doc.append(Command('addcontentsline',
                                    ['toc', 'section', opt['title']]))

            self.doc.append(Command('printbibliography',
                                    options=[
                                        'heading=none'],
                                    arguments=[]))

        # self.doc.append(NewPage())
        self.doc.append(Command('clearpage'))
        # self.doc.append(Command('cleardoublepage'))

    def write_page_annex(self, sname):
        self.doc.append(NewPage())

        key = 'annex'
        print('{}'.format(key))

        # self.doc.append(Command('clearpage'))
        # self.doc.append(Command('cleardoublepage'))
        self.doc.append(Command('RaggedRight'))
        self.doc.append(NoEscape(r'\renewcommand{\thesubsection}{Annex \arabic{subsection}}'))

        opt = self.data['content'][key]
        try:
            opt_annx = self.__conf['data']['content'][key]
            opt_data = self.__conf['data']['content']['data'][key]
        except KeyError:
            raise KeyError

        with self.doc.create(Section(NoEscape(opt['title']), numbering=False)) as obj_sec_l0:
            obj_sec_l0.append(Command('addcontentsline',
                                      ['toc', 'section', opt['title']]))

            for key in opt['section'].keys():
                val = opt['section'][key]
                if isinstance(val, dict):
                    type = val['type']

                    if type == 'text':
                        name = val['name']
                        section = opt_data[type][name]['caption'].format(data=opt_data)
                        print('{} {}'.format(key, section))

                        # with self.doc.create(Subsection(NoEscape(section),
                        #                                 numbering=False)) as obj_sec_l1:
                        #     self.doc.append(Command('addcontentsline',
                        #                             ['toc', 'subsection', NoEscape(section)]))
                        with obj_sec_l0.create(Subsection(NoEscape(section))) as obj_sec_l1:
                            for var_name, var_val in opt_data[type][name]['detail'].items():
                                with obj_sec_l1.create(Subsubsection(NoEscape(var_name), numbering=False)) as obj_sec_l2:
                                    if isinstance(var_val, dict):
                                        for prod_name, prod_val in var_val.items():
                                            try:
                                                tmp_str_para = prod_val.format(data=opt_data)
                                            except KeyError:
                                                tmp_str_para = prod_val

                                            try:
                                                obj_sec_l2.append(
                                                    NoEscape(tmp_str_para.format(data=opt_data)))
                                            except KeyError:
                                                obj_sec_l2.append(NoEscape(tmp_str_para))
                                            finally:
                                                obj_sec_l2.append(LineBreak())

                                    else:
                                        pass

                    if type == 'equation':
                        pass

                    if type == 'figure':
                        name = val['name']
                        section = opt_data[type][name]['caption'].format(data=opt_data)
                        print('{} {}'.format(key, section))

                        # with self.doc.create(Subsection(NoEscape(section),
                        #                                 numbering=False)) as obj_sec_l1:
                        #     self.doc.append(Command('addcontentsline',
                        #                             ['toc', 'subsection', NoEscape(section)]))
                        with obj_sec_l0.create(Subsection(NoEscape(section))) as obj_sec_l1:
                            dir = opt_data[type]['dir']

                            caption = ''
                            if 'main' in opt_data[type][name].keys():
                                fname = opt_data[type][name]['main']['fname']
                                width = opt_data[type][name]['main']['width']

                                file = os.path.join(self.workspace, dir, fname)
                                self.insert_image(obj_sec_l1,
                                                  name,
                                                  caption,
                                                  r'{}\textwidth'.format(width),
                                                  file)
                            if 'sub' in opt_data[type][name].keys():
                                width = opt_data[type][name]['width']

                                sub_files = []
                                sub_captions = []
                                for key, sub_img in opt_data[type][name]['sub'].items():
                                    sub_files.append(os.path.join(self.workspace, dir, sub_img['fname']))

                                self.insert_images(obj_sec_l1,
                                                   name,
                                                   caption,
                                                   r'{}'.format(width),
                                                   sub_files,
                                                   sub_captions)

                    if type == 'table':
                        name = val['name']
                        section = opt_data[type][name]['caption'].format(data=opt_data)
                        print('{} {}'.format(key, section))

                        # with self.doc.create(Subsection(NoEscape(section),
                        #                                 numbering=False)) as obj_sec_l1:
                        #     self.doc.append(Command('addcontentsline',
                        #                             ['toc', 'subsection', NoEscape(section)]))
                        with obj_sec_l0.create(Subsection(NoEscape(section))) as obj_sec_l1:
                            dir = opt_data[type]['dir']

                            caption = ''
                            fname = opt_data[type][name]['fname']
                            width = opt_data[type][name]['width']

                            file = os.path.join(self.workspace, dir, fname)
                            self.insert_table_csv(obj_sec_l1,
                                                  name,
                                                  caption,
                                                  r'1\textwidth',
                                                  file)
                else:
                    if val[0] == '{' and val[-1] == '}':
                        val = val.format(data=opt_data)

                    try:
                        tmp_str_para = val.format(data=opt_data)
                    except KeyError:
                        tmp_str_para = val

                    try:
                        obj_sec_l0.append(
                            NoEscape(tmp_str_para.format(data=opt_data)))
                    except KeyError:
                        obj_sec_l0.append(NoEscape(tmp_str_para))
                    finally:
                        obj_sec_l0.append(LineBreak())

                # obj_sec_l0.append(NewPage())
                obj_sec_l0.append(Command('clearpage'))
                obj_sec_l0.append(Command('cleardoublepage'))

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
                print('Could not delete "{}"'.format(file_with_ext))
                os._exit(1)
        self.doc.generate_tex(file)

        # if file != '.bib' os.path.splitext(file)[0]

        for ftype in ftypes:
            file_with_ext = '{}.{}'.format(file, str(ftype).lower())
            print('Saving: "{}"'.format(file_with_ext))
            if str(ftype).upper() == 'PDF':
                if os.path.isfile(file_with_ext):
                    try:
                        os.remove(file_with_ext)
                    except PermissionError as err:
                        print('Could not delete "{}"'.format(file_with_ext))
                        os._exit(1)
                # pkg natbib will cause latex style error!
                # Opt 1
                if self.__conf['isclean']:
                    self.doc.generate_pdf(file, clean=True, clean_tex=False)
                else:
                    self.doc.generate_pdf(file, clean=False, clean_tex=False)

                # Opt 2
                # .py  -> latexmk  -> .tex & .run.xml
                # .tex -> pdflatex -> .bcf
                # .bcf -> biber    -> .bbl
                # .bbl -> pdflatex -> .pdf 1st time
                # .bbl -> pdflatex -> .pdf 2ed time, make sure
                #
                # import subprocess
                # commands = [
                #     ['pdflatex', file + '.tex'],
                #     ['biber', file],
                #     # ['bibtex', file + '.aux'],
                #     ['pdflatex', file + '.tex'],
                #     ['pdflatex', file + '.tex']
                # ]
                # for c in commands:
                #     subprocess.call(c)

    def close(self):
        # if self.doc is not None:
        #     self.doc = None
        pass
