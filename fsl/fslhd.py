
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


def remove_tempfile(file):
    os.remove(file)


def system_cmd(cmd):
    """
    Runs a bash system command and gives back return code and std out
    """
    retval = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
    return retval.returncode, retval.stdout


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

    retval, statsval = system_cmd(cmd)

    if needs_removing:
        remove_tempfile(file)

    return float(statsval)

