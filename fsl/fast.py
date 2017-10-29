

__all__ = ['fsl_biascorrect']

import os

from .fslhd import (checkimg, check_outfile, 
                    get_fsl, get_imgext, readnii, 
                    remove_tempfile, system_cmd)


def fsl_biascorrect(file, outfile=None, retimg=True, reorient=False, 
                    opts='', verbose=True, remove_seg=True, **kwargs):
    """
    FSL Bias Correct
    
    This function wraps a call to \code{fast} that performs bias corretion.

    Arguments
    ---------
    file : string 
        image to be manipulated
    
    outfile : string 
        resultant image name (optional)
    
    retimg : boolean 
        return image of class nifti
    
    reorient : boolean 
        If retimg, should file be reoriented when read in?
    
    opts : string 
        operations to be passed to \code{fast}
    
    verbose : boolean 
        print out command before running
    
    remove_seg : (logical 
         Should segmentation from FAST be removed? 
    
    kwargs : additional arguments 
        passed to \code{\link{readnii}}. 

    Returns
    -------
    exit code | ants image | nibabel image
    
    Example
    -------
    >>> import fsl
    >>> fsl.fsl_biascorrect(file='~/desktop/img.nii.gz', outfile='~/desktop/img_bc.nii.gz', False)
    """
    cmd = get_fsl()
    file, fileremove = checkimg(file, **kwargs)

    cmd = '%sfast ' % cmd
    #no_outfile = outfile is None
    outfile = check_outfile(outfile=outfile, retimg=retimg, fileext='')
    outfile = outfile.split('.')[0]
    
    cmd = '%s %s -B --nopve --out="%s" "%s";' % (cmd, opts, outfile, file)
    
    if verbose:
        print(cmd, '\n')

    retval, stdout = system_cmd(cmd)

    ext = get_imgext()
    stub = outfile.split('.')[0]
    seg_file = '%s_seg%s' % (stub, ext)
    
    if remove_seg: 
        os.remove(seg_file)

    output = '%s_restore%s' % (stub, ext)
    outfile = '%s%s' % (stub, ext)
    os.rename(output, outfile)

    if retimg:
        img = readnii(outfile, reorient=reorient, **kwargs)
        if fileremove:
            remove_tempfile(file)
        return img
    else:
        return retval


