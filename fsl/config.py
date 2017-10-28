"""
Configuration file for FSL
"""
__all__ = ['set_fslpath', 
           'set_fsloutput',
           'set_fslpre',
           'get_fslpre']


FSL_PATH = None
FSL_OUTPUTTYPE = None
FSL_PRE = None
PYPACKAGE = 'nibabel'

def set_fslpath(path):
    global FSL_PATH 
    FSL_PATH = path

def get_fslpath():
    global FSL_PATH 
    return FSL_PATH

def set_fsloutput(output):
    global FSL_OUTPUTTYPE
    FSL_OUTPUTTYPE = output

def set_fslpre(pre):
    global FSL_PRE
    FSL_PRE = pre

def get_fslpre(pre):
    global FSL_PRE
    return FSL_PRE


def set_pypackage(p):
    p = p.lower()
    if p not in {'ants', 'antspy' 'nibabel'}:
        raise ValueError('pypackage must be ants or nibabel')
    if p == 'antspy':
        p = 'ants'
    global PYPACKAGE
    PYPACKAGE = p

def get_pypackage():
    global PYPACKAGE
    return PYPACKAGE