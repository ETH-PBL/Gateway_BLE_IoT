"""
file name:			run.py
author:				Jackie Lim
created:			30. March 2021

brief:				This file contains custom exceptions for the framework.
"""

class CustomException(Exception):
    pass

class InvalidStateException(CustomException):
    pass

class InputException(CustomException):
    pass

class UserException(CustomException):
    pass
