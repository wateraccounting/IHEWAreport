# -*- coding: utf-8 -*-
import inspect
import os
import yaml
import numpy as np

from pylatex import Document, Section, Subsection, Tabular, Math, TikZ, Axis, \
    Plot, Figure, Matrix, Alignat
from pylatex.utils import italic

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
        print('{}.{}'.format(path, template))

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

            self.write()
            self.saveas()
            # self.close()

    def _conf(self, path, template) -> dict:
        data = {}

        file_conf = os.path.join(path, template)
        with open(file_conf) as fp:
            data = yaml.load(fp, Loader=yaml.FullLoader)

        return data

    def create(self) -> object:
        geometry_options = self.data['layout']

        return Document(geometry_options=geometry_options)

    def write(self):
        with self.doc.create(Section('Section')):
            self.doc.append('Section -> text.')
            with self.doc.create(Subsection('Section -> Subsection')):
                self.doc.append('Section -> Subsection -> text.')

    def saveas(self):
        fname = self.__conf['data']['doc']['name']
        ftypes = self.__conf['data']['doc']['saveas']

        for ftype in ftypes:
            file = os.path.join(self.__conf['path'], '{n}'.format(n=fname))

            print('Save as: "{}.{}"'.format(file, str(ftype).lower()))
            if str(ftype).upper() == 'PDF':
                self.doc.generate_pdf(file, clean_tex=False)

    def close(self):
        if self.doc is not None:
            self.doc = None
