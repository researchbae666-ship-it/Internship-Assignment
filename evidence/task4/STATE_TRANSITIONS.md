# State-transition evidence

Source revision: `7c23159507b94caccebcbffc32eccf0705c22408`

The live `MAIN_TRANSCRIPT.txt` demonstrates this executed sequence:

```text
root -> task_2 -> task_2 follow-up -> python -> python clarification
-> python lists -> submission -> submission deadline -> submission clarification
-> reset -> exit
```

`tests/test_task4.py` additionally executed and asserted:

- a pending root choice resolves to Task 2;
- a pending Python choice resolves to its selected topic;
- an explicit topic change supersedes a pending choice;
- reset clears conversational context;
- independently created `SessionState` values do not share state;
- history retains only the configured 20 newest turns;
- exit ends the session without persistence;
- EOF and KeyboardInterrupt finish with a clean success return from the CLI loop;
- an unexpected internal exception is reported through the CLI with return code 1.

History is process-local only and is never written by the application.
