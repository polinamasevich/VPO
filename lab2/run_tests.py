"""Запуск из любой папки: python lab2/run_tests.py. Отчёты остаются в lab2/reports."""
from pathlib import Path
import os
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
REPORTS = ROOT / 'lab2' / 'reports'
REPORTS.mkdir(exist_ok=True)
env = os.environ.copy()
env.setdefault('MPLCONFIGDIR', str(Path(tempfile.gettempdir()) / 'pizzatime-mpl'))
env.setdefault('PYTHONPYCACHEPREFIX', str(Path(tempfile.gettempdir()) / 'pizzatime-pycache'))
config = '--rcfile=lab2/.coveragerc'


def execute(args, output):
    result = subprocess.run([sys.executable, '-m', 'coverage', *args], cwd=ROOT,
                            env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    (REPORTS / output).write_text(result.stdout, encoding='utf-8')
    print(result.stdout)
    return result.returncode


if __name__ == '__main__':
    test_status = execute(['run', config, 'manage.py', 'test', 'lab2.tests',
                           '--settings=lab2.settings', '-v', '2'], 'test-output.txt')
    report_status = execute(['report', config], 'coverage.txt')
    html_status = execute(['html', config], 'html-output.txt')
    json_status = execute(['json', config], 'json-output.txt')
    sys.exit(test_status or report_status or html_status or json_status)
