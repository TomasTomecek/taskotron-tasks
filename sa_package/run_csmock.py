#!/usr/bin/python
"""
task for taskotron: use csmock to analyze provided koji build

run it as: runtask -d -i <srpm_path> -t koji_build ./task.yml
"""
import os
import subprocess

from libtaskotron import check

ANALYZERS = "cppcheck,gcc,clang"
CSMOCK_COMMAND = ["csmock", "-t", ANALYZERS]


def analyze(srpm, work_dir):
    """ analyze provided srpm """
    cmd = CSMOCK_COMMAND + [srpm]
    pwd = os.environ['PWD']
    os.chdir(work_dir)
    rc = subprocess.call(cmd)
    # TODO: untar results
    os.chdir(pwd)
    return rc


def run(workdir, koji_build, koji_tag=None):
    # TODO: figure out mock profile somehow
    srpm = "None"

    try:
        srpm_path = koji_build['downloaded_rpms'][0]
    except (KeyError, IndexError):
        print 'no downloaded srpms'
        result = 'FAILED'
    else:
        srpm = srpm_path.rsplit('/', 1)[1]
        try:
            rc = analyze(srpm, workdir)
        except Exception as ex:
            print repr(ex)
            result = 'FAILED'
        else:
            if rc == 0:
                result = 'PASSED'
                # TODO: result = not passed if there are some defects
                # TODO: upload results to result DB
            else:
                print 'Return code: %d' % rc
                result = 'FAILED'

    summary = 'csmock %s for %s' % (result, srpm)
    report_type = check.ReportType.KOJI_BUILD
    detail = check.CheckDetail(item=srpm,
                               report_type=report_type)
    detail.outcome = result
    detail.summary = summary
    # TODO: add results into TAP

    return check.export_TAP(detail)
