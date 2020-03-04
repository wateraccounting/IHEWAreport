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
        template = 'ADB.yml'
        path = os.path.join(
            os.getcwd(),
            os.path.dirname(
                inspect.getfile(
                    inspect.currentframe()))
        )
        print('{}\n{}'.format(path, template))

    def _conf(self, path, template):
        pass

    def create(self):
        pass

    def write(self):
        pass

    def saveas(self):
        pass

    def close(self):
        pass