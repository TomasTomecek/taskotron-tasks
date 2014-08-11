import subprocess

from libtaskotron import check


CSMOCK_COMMAND = """\
csmock -t cppcheck,gcc,clang %(srpm_path)s\
"""


def analyze(srpms):
    for srpm in srpms:
        cmd = CSMOCK_COMMAND % {'srpm_path': srpm}
        rc = subprocess.call(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def run(workdir, koji_build):
    print "Running mytask on %s" % koji_build

    try:
        analyze(koji_build['downloaded_rpms'])
    except Exception:
        result = 'FAILED'
    except KeyError:
        result = 'FAILED'
    else:
        result = 'PASSED'

    details = []
    summary = 'mycheck %s for %s' % (result, koji_build)
    report_type = check.ReportType.KOJI_BUILD
    detail = check.CheckDetail(koji_build, report_type,
                               result, summary)
    #for rpmfile in rpmfiles:
    #    detail.store(rpmfile, False)

    #return check.export_TAP(detail)
