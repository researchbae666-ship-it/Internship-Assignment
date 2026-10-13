# Actual cloud environment

> **Dual-track setup update — 13 October 2026:** The recorded toolchain remains
> suitable for the existing Python workflow. The active branch is now
> `dual-track/marketing-and-enhancements`; no dependency, service, credential,
> or environment-configuration change is required for the planning-only
> Marketing setup.

Observed 12 October 2026 in `/workspace/Internship-Assignment`.

| Item | Observation |
| --- | --- |
| Python | CPython 3.12.14 |
| OS | Debian GNU/Linux 13 (trixie), VERSION_ID 13, Debian 13.6 |
| Kernel / CPU | Linux 6.18.44 / x86_64 |
| Git | 2.52.0; local branch `work`; remote `main` exists |
| pip | 26.2.1 for Python 3.12 |
| Tests | standard-library unittest available; pytest not installed |
| Reporting | reportlab and pypdf importable; pandoc and xelatex installed |
| PDF tools | pdftotext, pdfinfo and pdftoppm available |
| Other tools | node and npm present; not needed for Python tasks |
| Initial Git state | clean; four original files tracked; baseline 791338e4931f642b144a440f0179b20f827ec12a |

Observed commands: `python --version`, `git --version`, `python -m pip --version`, `uname -sr`, `cat /etc/os-release`, importlib module availability checks, shutil.which tool checks, `git status --short --branch`, `git ls-files`, `pdfinfo` and `pdftotext -layout` on the assignment PDF. PDF has one page, is not encrypted, and text extraction succeeded.

## Execution constraints

Filesystem writes are allowed under /workspace and /tmp; protected credential/config directories remain restricted. Network is enabled with platform-restricted egress policy and package-manager presets; GitHub push was previously verified. Form and LinkedIn access have not been tested. No live services or credentials are needed for planned tasks. Processes are not assumed to survive future cloud tasks. Use existing isolated checkout and temporary synthetic directories; no worktrees.

Programs/test suite are planned around Python standard library; installed ReportLab can generate the report in Phase 3. Installation and runtime dependency verification beyond module presence will occur in the approved phase; presence is not proof report generation works. No setup draft changes or new services are needed for Phase 1. Do not claim fresh-task restoration or publication was verified.
