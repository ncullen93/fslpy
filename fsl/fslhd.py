


import os
import shlex
import subprocess
from tempfile import mktemp

from . import config


def get_fsloutput():
    """
    #' @name get.fsloutput
    #' @title Determine FSL output type
    #' @description Finds the FSLOUTPUTTYPE from system environment or 
    #' \code{getOption("fsl.outputtype")} for output type (nii.gz, nii, ANALYZE,etc) 
    #' @return FSLOUTPUTTYPE, such as NIFTI_GZ.  If none found, uses NIFTI_GZ as default
    #' 
    #' @export
    get.fsloutput = function(){
      fslout = Sys.getenv("FSLOUTPUTTYPE")
      if (fslout == "") {
        fslout = getOption("fsl.outputtype")
      } 
      if (is.null(fslout)) {
        warning("Can't find FSLOUTPUTTYPE, setting to NIFTI_GZ")
        fslout = "NIFTI_GZ"
        options(fsl.outputtype = "NIFTI_GZ")
      }
      if (fslout == "") {
        warning("Can't find FSLOUTPUTTYPE, setting to NIFTI_GZ")
        fslout = "NIFTI_GZ"
        options(fsl.outputtype = "NIFTI_GZ")
      } 
      return(fslout)
    }
    """
    fslout = os.getenv('FSLOUTPUTTYPE')
    if fslout == None:
        fslout = config.FSL_OUTPUTTYPE
    if fslout == None:
        fslout = 'NIFTI_GZ'
        config.set_fsloutput(fslout)
    return fslout


def get_fsldir():
    fsldir = os.getenv('FSLDIR')
    if fsldir is None:
        #x = get_fsl()
        fsldir = config.FSL_PATH
    return fsldir


def get_fsl(add_bin=True):
    """
    #' @name get.fsl
    #' @title Create command declaring FSLDIR
    #' @description Finds the FSLDIR from system environment or \code{getOption("fsl.path")}
    #' for location of FSL functions
    #' @param add_bin Should \code{bin} be added to the fsl path? 
    #' All executables are assumed to be in \code{FSLDIR/bin/}.  If not, and 
    #' \code{add_bin = FALSE}, they will be assumed to be in \code{FSLDIR/}.
    #' @note This will use \code{Sys.getenv("FSLDIR")} before \code{getOption("fsl.path")}.
    #' If the directory is not found for FSL in \code{Sys.getenv("FSLDIR")} and 
    #' \code{getOption("fsl.path")}, it will try the default directory \code{/usr/local/fsl}.
    #' @return NULL if FSL in path, or bash code for setting up FSL DIR
    #' @export
    #' @import neurobase
    """
    cmd = None
    # check for environment variable
    fsldir = os.getenv('FSLDIR')
    if fsldir is None:
        fsldir = config.FSL_PATH
        # try default directories if FSLPATH isnt set either
        if fsldir is None:
            default_paths = ('/usr/local/fsl', '/usr/share/fsl/5.0', '/usr/share/fsl/5.1')
            for default_path in default_paths:
                if os.path.exists(default_path):
                    config.set_fslpath(default_path)
                    fsldir = default_path
                    break
        else:
            if not os.path.exists(fsldir):
                raise ValueError('fslpath is set but folder doesnt exist!')

        bin_ = 'bin'
        bin_app = '%s/' % bin_
        if not add_bin:
            bin_app = bin_ = ''

        fslout = get_fsloutput()
        shfile = os.path.join(fsldir, 'etc/fslconf/fsl.sh')
        cmd = 'FSLDIR=' + shlex.quote(fsldir) + '; ' + \
              'PATH=${FSLDIR}/' + bin_ + ':${PATH};' + \
              'export PATH FSLDIR; ' + '%s ' % ('sh "${FSLDIR}/etc/fslconf/fsl.sh";' if os.path.exists(shfile) else '') + \
              'FSLOUTPUTTYPE=' + fslout + '; export FSLOUTPUTTYPE; ' + \
              '%s%s' % ('${FSLDIR}/', bin_app)

        fsl_pre = config.FSL_PRE
        if fsl_pre is None:
            fsl_pre = ''
        else:
            fsl_pre = str(fsl_pre)

        cmd = cmd + fsl_pre

    if fsldir is None:
        raise ValueError('Cant find FSL')
    if fsldir == '':
        raise ValueError('Cant find FSL')

    if cmd is None:
        cmd = ''
    return cmd


def get_imgext():
    """
    #' @title Determine extension of image based on FSLOUTPUTTYPE
    #' @description Runs \code{get.fsloutput()} to extract FSLOUTPUTTYPE and then 
    #' gets corresponding extension (such as .nii.gz)
    #' @return Extension for output type
    """
    fslout = get_fsloutput()
    ext_dict = {'NIFTI_PAIR'    : '.hdr', 
                'NIFTI_GZ'      : '.nii.gz', 
                'ANALYZE'       : '.hdr', 
                'ANALYZE_GZ'    : '.hdr.gz',
                'NIFTI'         : '.nii',
                'NIFTI_PAIR_GZ' :  '.hdr.gz'}
    return ext_dict[fslout]


def checkimg(img, **kwargs):
    if ('nibabel' in str(type(img))) or ('Nifti1' in str(type(img))) or ('Nifti2' in str(type(img))):
        tmpfile = mktemp(suffix='.nii.gz')
        img.to_filename(tmpfile)
        return tmpfile, True

    elif ('ants' in str(type(img))) or ('ANTs' in str(type(img))):
        tmpfile = mktemp(suffix='.nii.gz')
        img.to_file(tmpfile)
        return tmpfile, True
    
    elif isinstance(img, str):
        img = os.path.expanduser(img)
        return img, False


def check_outfile(outfile, retimg, fileext='.nii.gz'):
    """
    This function checks if an output filename is not None in conjunction 
    whether the user would like to return an image

    Arguments
    ---------
    outfile : string
        output filename or None
    retimg : boolean
        Should an image be returned
    fileext : string
        the file extension
    """
    if retimg:
        if outfile is None:
            outfile = mktemp(suffix=fileext)
    else:
        if outfile is None:
            raise ValueError('Outfile is None, and retimg=False, one of these must be changed')

    return os.path.expanduser(outfile)


def readimg(filename, **kwargs):
    pypack = config.get_pypackage()
    if pypack == 'ants':
        import ants
        img = ants.image_read(filename, **kwargs)
    elif pypack == 'nibabel':
        import nibabel
        img = nibabel.load(filename, **kwargs)
    else:
        config.set_pypackage('nibabel')
        import nibabel
        img = nibabel.load(filename, **kwargs)
    return img


def remove_tempfile(file):
    os.remove(file)


def system_cmd(cmd):
    """
    Runs a bash system command and gives back return code and std out
    """
    retval = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
    stdout = retval.stdout.decode('unicode_escape')
    return retval.returncode, stdout


def have_fsl():
    """
    #' @title Logical check if FSL is accessible
    #' @description Uses \code{get.fsl} to check if FSLDIR is accessible or the option
    #' \code{fsl.path} is set and returns logical
    #' @param ... options to pass to \code{\link{get.fsl}}
    #' @return Logical TRUE is FSL is accessible, FALSE if not
    #' @export
    #' @examples
    #' have.fsl()
    have.fsl = function(...){
      x = suppressWarnings(try(get.fsl(...), silent = TRUE))
      return(!inherits(x, "try-error"))
    }
    """
    try:
        get_fsl()
        return True
    except:
        return False


def fslstats(file, opts=None, verbose=False, ts=False, **kwargs):
    """
    #' @title FSL Stats 
    #' @description This function calls \code{fslstats}
    Arguments
    ---------
    file : string
        filename of image to be checked
    opts : string
        operation passed to `fslstats`
    verbose : boolean
        print out command before running
    ts : boolean
        true if img is a timeseries (4D), invoking `-t`
    
    Returns
    -------
    scalar

    Example
    -------
    >>> import fsl
    >>> # pass in filename
    >>> val1 = fsl.fslstats('~/desktop/img.nii.gz', opts='-m', verbose=True)
    >>> # pass in nibabel image
    >>> import nibabel as nib
    >>> img = nib.load('/users/ncullen/desktop/img.nii.gz')
    >>> val2 = fsl.fslstats(img, opts='-m')
    >>> # pass in ants image
    >>> import ants
    >>> img = ants.image_read('~/desktop/img.nii.gz')
    >>> val3 = fsl.fslstats(img, opts='-m')
    """
    cmd = get_fsl()
    file, needs_removing = checkimg(file, **kwargs)

    # build cmd
    cmd = '%sfslstats %s "%s" %s' % \
          (cmd, '-t' if ts else '', file, opts)

    if verbose:
        print(cmd)

    retval, stdout = system_cmd(cmd)

    stdout = stdout.replace('\n',' ').strip(' ')

    if needs_removing:
        remove_tempfile(file)

    try:
        stdout = float(stdout)
    except:
        pass

    return stdout


def fslstats_help():
    """
    #' @title FSL Stats Help
    #' @description This function calls \code{fslstats}'s help
    #' @return Prints help output and returns output as character vector
    #' @aliases fslrange.help fslmean.help fslentropy.help fslsd.help
    #' @export
    #' @examples
    #' if (have.fsl()){
    #'  fslstats.help() 
    #' }
    fslstats.help = function(){
      return(fslhelp("fslstats"))
    }

    Example
    -------
    >>> import fsl
    >>> fsl.fslstats_help()
    """
    return fslhelp('fslstats')


def fslhelp(func_name, help_arg='--help', extra_args='', return_string=False):
    """
    #' @title Wrapper for getting fsl help
    #' @description This function takes in the function and returns the
    #' help from FSL for that function
    #' @param func_name FSL function name
    #' @param help.arg Argument to print help, usually "--help" 
    #' @param extra.args Extra arguments to be passed other than 
    #' \code{--help}
    #' @return Prints help output and returns output as character vector
    #' @export
    fslhelp = function(func_name, help.arg = "--help", extra.args = ""){
      cmd = get.fsl()
      cmd <- paste0(cmd, sprintf('%s %s %s', func_name, 
                                 help.arg, extra.args))
      #     args = paste(help.arg, extra.args, sep=" ", collapse = " ")
      suppressWarnings({res = system(cmd, intern = TRUE)})
      #     res = system2(func_name, args = args, stdout=TRUE, stderr=TRUE)
      message(res, sep = "\n")
      return(invisible(res))
    }
    """
    cmd = get_fsl()
    cmd = '%s%s %s %s' % \
          (cmd, func_name, help_arg, extra_args)
    retval, stdout = system_cmd(cmd)

    helpstring = stdout.decode('unicode_escape') 
    if return_string:
        return helpstring
    else:
        print(helpstring)


def fslbet(infile, outfile=None, retimg=True, reorient=False, opts='', betcmd=('bet2', 'bet'), verbose=False, **kwargs):
    """
    Use FSL's Brain Extraction Tool (BET)
    
    This function calls \code{bet} to extract a brain from an image, 
    usually for skull stripping.

    Arguments
    ---------
    infile : string
        input filename
    
    outfile : string
        output filename
    
    retimg : boolean
        return a loaded image object 
        (either from ants or nibabel, depending on config settings)
    
    reorient : boolean
        If retimg, should file be reoriented when read in
    
    opts : string
        additional options to \code{bet}
    
    betcmd : string
        Use \code{bet} or \code{bet2} function
    
    verbose : boolean
        print out command before running 
    
    kwargs : additional arguments passed to \code{\link{readimg}}.
    
    Returns
    -------
    string or image object

    Example
    -------
    >>> import fsl
    >>> infile = '/users/ncullen/desktop/img.nii.gz'
    >>> outfile = '/users/ncullen/desktop/img_bet.nii.gz'
    >>> fsl.fslbet(infile, outfile, retimg=False)
    """
    if isinstance(betcmd, tuple):
        betcmd = betcmd[0]

    cmd = get_fsl()
    outfile = check_outfile(outfile=outfile, retimg=retimg, fileext='')
    infile, inremove = checkimg(infile, **kwargs)
    outfile, outremove = checkimg(outfile, **kwargs)

    cmd = '%s%s "%s" "%s" %s' % (cmd, betcmd, infile, outfile, opts)

    if verbose:
        print(cmd, '\n')

    retval, stdout = system_cmd(cmd)
    ext = get_imgext()
    outfile = '%s%s' % (outfile, ext)
    
    if retimg:
        img = readimg(outfile, reorient=reorient, **kwargs)
        if inremove: remove_tempfile(infile)
        if outremove: remove_tempfile(outfile)
        return img
    else:
        if inremove: remove_tempfile(infile)
        return retval


def fslbet_help(betcmd=('bet2', 'bet')):
    """
    #' @title Help for FSL BET
    #' @description This function calls \code{bet}'s help
    #' @param betcmd string Get help for \code{bet} or \code{bet2} function
    #' @return Prints help output and returns output as character vector
    #' @export
    #' @examples
    #' if (have.fsl()){
    #'  fslbet.help()
    #'  fslbet.help("bet")
    #' }  
    fslbet.help = function(betcmd = c("bet2", "bet")){
      betcmd = match.arg( betcmd )
      return(fslhelp(betcmd, help.arg = "-h"))
    }
    """
    if isinstance(betcmd, tuple):
        betcmd = betcmd[0]

    return fslhelp(betcmd)


def fslcog(img, mm=True, verbose=False, ts=False):
    """
    Image Center of Gravity (FSL)
    
    Find Center of Gravity of Image from FSL
    
    Arguments
    ---------
    img : string | nibabel image | ants image
        image on which CoG will be calculated
    
    mm : boolean
        if the center of gravity (COG) would be in mm (True) or voxels (False)
    
    verbose : boolean
         print out command before running 

    ts : boolean
         is the series a timeseries (4D), invoking \code{-t} 

    Returns
    -------
    list of length 3 unless `ts==True`

    Example
    -------
    >>> import fsl
    >>> cog = fslcog('~/desktop/img.nii.gz')
    """
    opts = '-c' if mm else '-C'
    cog = fslstats(img, opts=opts, verbose=verbose, ts=ts)
    cog = cog.split(' ')

    if len(cog) == 1:
        cog = float(cog[0])
    else:
        cog = [float(c) for c in cog]

    return cog


def fslorient(file, retimg=True, reorient=False, opts='', verbose=False, **kwargs):
    """
    FSL Orient

    Arguments
    ---------
    file : string | ants image | nibabel image
        image to be manipulated
    
    retimg : boolean 
        return image of class nifti
    
    reorient : boolean 
        If \code{retimg}, should file be reoriented when read in?
    
    opts : string 
        operations to be passed to \code{fslorient}
    
    verbose : boolean 
        print out command before running
    
    kwargs : additional arguments 
        passed to \code{\link{readimg}}.
    
    Returns
    -------
    exit code from system call | ants image | nibabel image
    
    Example
    -------
    >>> import fsl
    >>> fsl.fslorient('~/desktop/img.nii.gz', retimg=False)
    """
    if ('-get' in opts) and retimg:
        print('fslorient option was a -get, ',
              'image was not changed - output not returned,',
              ' and retimg set to False')
        retimg = False

    cmd = get_fsl()
    file, fileremove = checkimg(file, **kwargs)
    cmd = '%sfslorient %s "%s"' % (cmd, opts, file)
    outfile = file.split('.')[0]
    ext = get_imgext()
    outfile = '%s%s' % (outfile, ext)

    if verbose:
        print(cmd, '\n')

    retval, stdout = system_cmd(cmd)

    if retimg:
        img = readimg(outfile, **kwargs)
        return img
    else:
        return retval


def fslorient_help():
    return fslhelp('fslorient')


