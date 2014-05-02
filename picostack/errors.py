class PicoStackError(Exception):
    '''User-defined base error for all Pico Stack errors.'''


class DataModelError(PicoStackError):
    '''Thrown in case django-side data model logics goes wrong.'''
