# Reproduce the targeted corrections

Use source revision `4c6a6c9795d41b3835fe85a53ed9bafe11d6ad22` from the repository root.

```bash
python -m unittest discover -s tests -v
python -m compileall -q internship
printf 'tasks\nsomething\nstill something\ntask 3\nreset\nexit\n' | python -m internship.task4
printf 'task 4\nwhat is the weather\nstill weather\ntell me more\nexit\n' | python -m internship.task4
```

The `CORRECTION_LAST_INTENT_TRANSCRIPT.txt` conversation was run through the real `handle_turn` state machine and prints the mutable session fields after each displayed turn so `last_intent` is observable. The normal terminal CLI deliberately displays only user-facing replies.
