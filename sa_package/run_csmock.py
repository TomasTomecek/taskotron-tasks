from libtaskotron import check

def run_mytask(workdir, koji_build):
    print "Running mytask on %s" % koji_build

    details = []
    result = 'PASSED'
    summary = 'mycheck %s for %s' % (result, koji_build)
    report_type = check.ReportType.KOJI_BUILD
    detail = check.CheckDetail(koji_build, report_type,
                               result, summary)
    #for rpmfile in rpmfiles:
    #    detail.store(rpmfile, False)

    #return check.export_TAP(detail)
