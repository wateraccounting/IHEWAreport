# -*- coding: utf-8 -*-
import pytest

import inspect
import os

import IHEWAreport


__author__ = "Quan Pan"
__copyright__ = "Quan Pan"
__license__ = "apache"


def test_report():
    print('\nReport\n=====')
    path = os.path.join(
        os.getcwd(),
        os.path.dirname(
            inspect.getfile(
                inspect.currentframe()))
    )
    # os.chdir(path)

    report = IHEWAreport.Report(path, 'ex_DataAnalysis_DiffPctOverPcp.yml')

    # report.get_config()
    # print(report._Report__conf['path'], '\n',
    #       report._Report__conf['name'], '\n',
    #       report._Report__conf['time'], '\n',
    #       report._Report__conf['data'])


if __name__ == "__main__":
    test_report()
