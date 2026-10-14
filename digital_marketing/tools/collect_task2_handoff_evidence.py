"""Reproduce handoff validation and PDF QA without fetching or altering history."""
import hashlib
import json
import platform
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE = '61e7e068c887800e0e33377d1dc86491f973ab92'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ev = ROOT / 'digital_marketing/evidence/task2/handoff'
    raw = ROOT / 'artifacts/digital_marketing/task2_handoff'
    ev.mkdir(parents=True, exist_ok=True)
    raw.mkdir(parents=True, exist_ok=True)
    protected = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASELINE], cwd=ROOT, text=True).splitlines()
    checked = 0
    for name in protected:
        if name.startswith(('internship/', 'tests/', 'evidence/', 'deliverables/', 'digital_marketing/research/task2/', 'digital_marketing/evidence/task2/', 'digital_marketing/research/task3/', 'digital_marketing/research/task4/', 'digital_marketing/evidence/task3/', 'digital_marketing/evidence/task4/', 'digital_marketing/deliverables/')):
            if (ROOT / name).read_bytes() != subprocess.check_output(['git', 'show', f'{BASELINE}:{name}'], cwd=ROOT):
                raise ValueError('Protected file changed: ' + name)
            checked += 1
    records = []
    commands = [
        ['python', '-m', 'unittest', 'discover', '-s', 'digital_marketing/research/task2/handoff', '-v'],
        ['python', '-m', 'unittest', 'discover', '-s', 'digital_marketing/research/task2/recovery', '-v'],
        ['python', 'digital_marketing/tools/test_task2_recovery_report.py'],
        ['python', '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
        ['python', 'digital_marketing/tools/generate_task2_handoff_report.py']]
    for index, command in enumerate(commands):
        result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        text = result.stdout + result.stderr
        output = ev / f'command-{index}.txt'
        output.write_text(text.replace(str(ROOT), '<repository>'))
        match = re.search(r'Ran (\d+) tests', text)
        records.append({'command': command, 'utc': datetime.now(timezone.utc).isoformat(), 'exit_code': result.returncode, 'tests_run': int(match.group(1)) if match else None, 'output': str(output.relative_to(ROOT))})
        if result.returncode:
            raise RuntimeError(text)
    pdf = ROOT / 'digital_marketing/deliverables/DM_Task2_Competitor_Audit_HANDOFF_DRAFT.pdf'
    for command in [['pdfinfo', str(pdf)], ['pdftotext', str(pdf), str(ev / 'pdf-text.txt')], ['pdftoppm', '-png', '-r', '110', str(pdf), str(raw / 'page')]]:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(result.stderr)
        if command[0] == 'pdfinfo':
            (ev / 'pdfinfo.txt').write_text(result.stdout)
            if not re.search(r'Pages:\s+4\b', result.stdout):
                raise ValueError('Expected four report pages')
        records.append({'command': [item.replace(str(ROOT) + '/', '') for item in command], 'utc': datetime.now(timezone.utc).isoformat(), 'exit_code': result.returncode})
    source = ROOT / 'digital_marketing/research/task2/handoff/PUBLIC_SOURCE_HANDOFF_2026-10-13.md'
    manifest = {'execution_source_revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'generated_utc': datetime.now(timezone.utc).isoformat(), 'python': platform.python_version(), 'platform': platform.platform(), 'commands': records, 'protected_files_checked': checked, 'protected_files_result': 'byte-for-byte unchanged', 'status': 'incomplete measured audit; secondary qualitative update', 'handoff': {'review_date_utc': '2026-10-13', 'provenance': 'independent reviewer supplied by user; not retrieved by Codex', 'path': str(source.relative_to(ROOT)), 'sha256': sha(source)}, 'pdf': {'path': str(pdf.relative_to(ROOT)), 'bytes': pdf.stat().st_size, 'pages': 4, 'sha256': sha(pdf)}, 'visual_qa': 'See QA.md; rendering alone does not establish manual inspection', 'digests': {str(path.relative_to(ROOT)): sha(path) for path in sorted(ev.glob('*')) if path.is_file() and path.name != 'manifest.json'}}
    (ev / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'pdf': manifest['pdf'], 'tests': [row['tests_run'] for row in records if row.get('tests_run')], 'protected': checked}, indent=2))


if __name__ == '__main__':
    main()
