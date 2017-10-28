"""
Configuration file for FSL
"""

FSL_PATH = None
FSL_OUTPUTTYPE = None
FSL_PRE = None


def set_fslpath(path):
    global FSL_PATH 
    FSL_PATH = path

def set_fsloutput(output):
    global FSL_OUTPUTTYPE
    FSL_OUTPUTTYPE = output

def set_fslpre(pre):
    global FSL_PRE
    FSL_PRE = pre
