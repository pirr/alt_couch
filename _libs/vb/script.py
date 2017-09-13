import alt_path
from alt.dict_ import dict_
import alt.time
import psutil, subprocess, sys, os

def find_by_name(root, script_name):

    view = root.db.view('www-scripts_by_name')
    rows = view[script_name].rows
    if not rows:
        return dict_(error='Скрипт не существует')
    script_doc = root.db[rows[0].id]

    return script_doc

# TODO переписать более акккуратно, возможны коллизии
def run(root, script_name, params=dict_()):

    script_doc = find_by_name(root, script_name)
    script_id = script_doc._id

    run_doc = dict_(type='run', script_id=script_id, params=params, ctime=alt.time.mtime(),
                    status='WAIT')
    run_id = root.heap_db.new_id(run_doc)

    return run_id

def os_pid_running(pid):

    if not psutil.pid_exists(pid):
        return False

    proc = psutil.Process(pid)
    if proc.is_running():
        if proc.status() == psutil.STATUS_ZOMBIE:
            return False

    return proc.is_running()

def report(root, run_id):

    report_id = run_id+'_report'
    if report_id in root.heap_db:
        report_doc = root.heap_db[report_id]
        return report_doc

    run_doc = root.heap_db[run_id]
    if os_pid_running(run_doc.os_pid):
        return dict_(status='RUN')
    else:
        return dict_(status='FATAL')

