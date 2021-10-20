import os
import re
from typing import Union
from werkzeug.datastructures import FileStorage

from flask_uploads import UploadSet, IMAGES


IMAGE_SET = UploadSet('images', IMAGES)  # set name and allowed extensions


def save_image(image: FileStorage, folder: str = None, name: str = None
               ) -> str:
    """
    Takes FileStorage and saves it to a folder.
    :return:
    """
    return IMAGE_SET.save(image, folder, name)


def get_path(filename: str = None, folder: str = None) -> str:
    """
    Take image name and folder and return full path.
    :return:
    """
    return IMAGE_SET.path(filename, folder)


def find_image_any_format():
    """
    Takes a filename and returns an image on any of the accepted formats.
    :return:
    """
    pass


def _retrieve_filename():
    """
    Take FileStorage and return the file name.
    :return:
    """
    pass


def is_filename_safe():
    """
    Check our regex and return whether the string matches or not.
    :return:
    """
    pass


def get_basename():
    """
    Return full name of image in the path
    get_basename('some/folder/image.jpg') returns 'image.jpg'
    :return:
    """
    pass


def get_extension():
    """
    Return file extension
    get_basename('image.jpg') returns '.jpg'
    :return:
    """
    pass
