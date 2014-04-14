import os
import traceback
import sys


SRC_PATH = os.path.dirname(__file__)
LOCAL_PATH = os.path.join(os.path.dirname(SRC_PATH), 'local')


def override_with_local(file_path):
    if SRC_PATH not in file_path:
        return 
    local_mirror = os.path.join(LOCAL_PATH,
                                file_path.replace(SRC_PATH, '',  1)[1:])
    if not os.path.exists(local_mirror):
        return
    try:
        execfile(local_mirror)
    except Exception as exception:
        print >> sys.stderr, traceback.format_exception_only(
            type(exception), exception)
        raise Exception('Make sure to use this functionality strictly inside '
                        'a mirror module')
