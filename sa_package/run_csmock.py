#!/usr/bin/python
"""
task for taskotron: use csmock to analyze provided koji build

run it as: runtask -d -i <srpm_path> -t koji_build ./task.yml
"""
import os
import json
import subprocess

from libtaskotron import check

ANALYZERS = "cppcheck,gcc,clang"
#ANALYZERS = "gcc"
CSMOCK_COMMAND = ["csmock", "-t", ANALYZERS]
INLINE_TEMPLATE_REPORT = "\
%(checker)s %(file_name)s:%(line)s: %(event)s: %(message)s"
TEMPLATE_JSON_RESULTS_SUFFIX = 'scan-results.js'
TEMPLATE_TAR_RESULTS_SUFFIX = '.tar.xz'


def analyze(srpm, work_dir):
    """ analyze provided srpm """
    cmd = CSMOCK_COMMAND + [srpm]
    rc = subprocess.call(cmd)
    return rc


def untar_results(tar_path):
    rc = subprocess.call(["tar", "-xf", tar_path])
    if rc != 0:
        raise RuntimeError("Extraction failed")


def get_defects_list(json_results_path):
    # TODO: catch exceptions in here
    with open(json_results_path, 'r') as f:
        results = []
        js = json.load(f)
        defects = js['defects']
        for defect in defects:
            key_event_idx = defect['key_event_idx']
            events = defect['events']
            key_event = events[key_event_idx]
            dogfood = {}
            dogfood.update(key_event)
            dogfood.update(defect)
            line = INLINE_TEMPLATE_REPORT % dogfood
            results.append(line)
        return results


def run(workdir, koji_build, koji_build_dict, koji_tag=None):
    """
    workdir -- temp directory
    koji_build -- nvr of build
    koji_build_dict -- dict with information about downloaded srpm
    """
    # TODO: figure out mock profile somehow
    srpm = "None"
    results = []
    pwd = os.environ['PWD']
    os.chdir(workdir)

    try:
        srpm_path = koji_build_dict['downloaded_rpms'][0]
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
                untar_results(koji_build + TEMPLATE_TAR_RESULTS_SUFFIX)
                json_results_path = os.path.join(
                    koji_build, TEMPLATE_JSON_RESULTS_SUFFIX)
                results = get_defects_list(json_results_path)
                if len(results) > 0:
                    result = 'NEEDS_INSPECTION'
                else:
                    result = 'PASSED'
                # TODO: upload results to result DB
            else:
                print 'Return code: %d' % rc
                result = 'FAILED'

    summary = 'state = %s, package = %s (%d defect%s)' % (
        result, srpm, len(results), 's' if len(results) > 1 else '')
    report_type = check.ReportType.KOJI_BUILD
    detail = check.CheckDetail(item=srpm,
                               report_type=report_type)
    detail.outcome = result
    detail.summary = summary
    detail.output = results

    os.chdir(pwd)
    return check.export_TAP(detail)
