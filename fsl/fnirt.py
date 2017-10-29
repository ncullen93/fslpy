

__all__ = ['fnirt', 'fnirt_help',
           'fnirt_with_affine']

import os
from tempfile import mktemp

from .fslhd import (checkimg, check_outfile, get_fsl, 
                    get_imgext, readnii, remove_tempfile, 
                    system_cmd, fslhelp, flirt)


def fnirt(infile, reffile, outfile=None, retimg=True,
          reorient=False, opts='', verbose=True, **kwargs):
    """
    Register using FNIRT
    
    This function calls \code{fnirt} to register infile to reffile
    and either saves the image or returns an object of class nifti
    
    Arguments
    ---------
    infile : string
        input filename
    
    reffile : string
        reference image to be registered to
    
    outfile : string
        output filename
    
    retimg : boolean
        return image of class nifti
    
    reorient : boolean
        If retimg, should file be reoriented when read in?
    
    intern : boolean
        pass to \code{\link{system}}
    
    opts : string
        additional options to FLIRT
    
    verbose : boolean
        print out command before running
    
    kwargs : keyword args
        additional arguments passed to \code{\link{readnii}}.

    Returns
    -------
    exit code | ants image | nibabel image
    """
    cmd = get_fsl()

    outfile = check_outfile(outfile=outfile, retimg=retimg, fileext='')
    infile, inremove = checkimg(infile, **kwargs)
    reffile, refremove = checkimg(reffile, **kwargs)
    outfile, outremove = checkimg(outfile, **kwargs)
    outfile = outfile.split('.')[0]

    cmd = '%sfnirt --in="%s" --ref="%s" --iout="%s" %s' % \
          (cmd, infile, reffile, outfile, opts)

    if verbose:
        print(cmd, '\n')

    retval, stdout = system_cmd(cmd)
    ext = get_imgext()
    outfile = '%s%s' % (outfile, ext)

    if retimg:
        img = readnii(outfile, reorient=reorient, **kwargs)
        if inremove: remove_tempfile(infile)
        if refremove: remove_tempfile(reffile)
        if outremove: remove_tempfile(outremove)
        return img
    else:
        return retval        


def fnirt_help():
    return fslhelp('fnirt')


def fnirt_with_affine(infile, reffile, flirt_omat=None, flirt_outfile=None,
                      outfile=None, retimg=True, reorient=False,
                      flirt_opts='', opts='', verbose=True, **kwargs):
    """
    Register using FNIRT, but doing Affine Registration as well

    This function calls \code{fnirt} to register infile to reffile
    and either saves the image or returns an object of class nifti, but does
    the affine registration first

    Arguments
    ---------
    infile : string 
        input filename

    reffile : string 
        reference image to be registered to

    flirt_omat : string 
        Filename of output affine matrix

    flirt_outfile : string 
        Filename of output affine-registered image

    outfile : string 
        output filename

    retimg : boolean 
        return image of class nifti

    reorient : boolean 
        If retimg, should file be reoriented when read in?

    intern : boolean 
        pass to \code{\link{system}}

    flirt_opts : string 
        additional options to FLIRT

    opts : string 
        additional options to FNIRT

    verbose : boolean 
        print out command before running

    kwargs : keywords args
        additional arguments passed to \code{\link{readnii}}.
    
    Returns
    -------
    exit code | ants image | nibabel image
    """
    cmd = get_fsl()
    outfile = check_outfile(outfile=outfile, retimg=retimg, fileext='')

    ##################################
    # FLIRT output matrix
    ##################################  
    if flirt_omat is None:
        flirt_omat = mktemp()
    flirt_omat = os.path.expanduser(flirt_omat)

    ##################################
    # FLIRT output file
    ##################################
    if flirt_outfile is None:
        flirt_outfile = mktemp()
    flirt_outfile = os.path.expanduser(flirt_outfile)

    flirt_outfile, flirtoutremove = checkimg(flirt_outfile, **kwargs)
    flirt_outfile = flirt_outfile.split('.')[0]

    infile, inremove = checkimg(infile, **kwargs)
    reffile, refremove = checkimg(reffile, **kwargs)
    outfile, outremove = checkimg(outfile, **kwargs)
    outfile = outfile.split('.')[0]

    #affine_file = mktemp()
    
    # run FLIRT
    res_flirt = flirt(infile=infile, 
                      reffile=reffile, 
                      omat=flirt_omat, 
                      dof=12,
                      outfile=flirt_outfile,                  
                      ### keep retimg = False
                      retimg=False,
                      opts=flirt_opts, 
                      verbose = verbose)
    
    # run FNIRT
    res_fnirt = fnirt(infile=flirt_outfile, 
                      reffile=reffile, 
                      outfile=outfile,                  
                      retimg=retimg,
                      reorient=reorient,                 
                      opts=opts, verbose=verbose, **kwargs)
    return res_fnirt



