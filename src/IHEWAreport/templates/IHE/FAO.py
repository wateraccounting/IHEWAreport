# -*- coding: utf-8 -*-
class Template(object):
    """This Base class

    Load base.yml file.

    Args:
        product (str): Product name of data products.
        is_print (bool): Is to print status message.
    """
    def __init__(self):
        """Class instantiation
        """
        print('FAO')

    def create(self):
        print('Template.create()')
