"""Implements the function providing names for the output files.

:author: Michel Bierlaire

:date: Tue Mar 26 16:48:40 2019
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def get_new_file_name(name: str, ext: str) -> str:
    """
      Generate a file name that does not exist.

    :param name: name of the file.

    :param ext: file extension.

    :return: name.ext if the file does not exists.  If it does, returns
       name~xx.ext, where xx is the smallest integer such that the
       corresponding file does not exist. It is designed to avoid erasing
       output files inadvertently.

    """
    file_name = name + '.' + ext
    the_file = Path(file_name)
    number = int(0)
    while the_file.is_file():
        file_name = f'{name}~{number:02d}.{ext}'
        the_file = Path(file_name)
        number += 1
    return file_name


def getNewFileName(name: str, ext: str) -> str:
    """
      Old version.

    :param name: name of the file.

    :param ext: file extension.

    :return: name.ext if the file does not exists.  If it does, returns
       name~xx.ext, where xx is the smallest integer such that the
       corresponding file does not exist. It is designed to avoid erasing
       output files inadvertently.

    """
    raise NotImplementedError
    logger.warning(
        'The syntax "getNewFileName" is deprecated and is replaced by '
        'the syntax "get_new_file_name".'
    )
    return get_new_file_name()
