"""Task 4: a local, rule-based terminal assistant for internship guidance.

No network, accounts, persistent storage, or personal data are used. The routing
order is: exit, reset/cancel, global help, explicit tree/topic switch, pending
follow-up, then fallback. A session is in-memory and independent per instance.
"""

from __future__ import annotations

import sys
import unicodedata
from dataclasses import dataclass, field
from typing import Callable


HISTORY_LIMIT = 20


@dataclass
class SessionState:
    current_tree: str | None = None
    pending_choice: str | None = None
    last_intent: str | None = None
    turn_count: int = 0
    history: list[str] = field(default_factory=list)
    fallback_count: int = 0
    clarification_count: int = 0
    active: bool = True


@dataclass(frozen=True)
class TurnResult:
    text: str
    intent: str
    should_exit: bool = False


def normalize(text: str) -> str:
    """Normalize Unicode input with NFKC, casefolding, punctuation and whitespace."""
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    normalized = unicodedata.normalize("NFKC", text).casefold()
    characters = [" " if unicodedata.category(char).startswith("P") else char for char in normalized]
    return " ".join("".join(characters).split())


def _tokens(text: str) -> set[str]:
    return set(text.split())


def _record(session: SessionState, normalized: str) -> None:
    session.turn_count += 1
    session.history.append(normalized)
    del session.history[:-HISTORY_LIMIT]


def _set_context(session: SessionState, tree: str | None, pending: str | None, intent: str) -> None:
    session.current_tree = tree
    session.pending_choice = pending
    session.last_intent = intent
    session.fallback_count = 0
    session.clarification_count = 0


def _clarification(session: SessionState, first_message: str, choices: str) -> TurnResult:
    """Return a contextual clarification that escalates after a repeated miss."""
    session.clarification_count += 1
    if session.clarification_count >= 2:
        return TurnResult(
            f"I still need a clear choice. {choices} Type help for the main menu or reset to clear this context.",
            "ambiguous",
        )
    return TurnResult(first_message, "ambiguous")


def _opening() -> str:
    return (
        "Welcome to the Progree Python assignment helper. Choose: tasks, python, or submission. "
        "Type help at any time; reset/cancel clears context; exit ends this local session."
    )


def _general_help(session: SessionState, _: str) -> TurnResult:
    _set_context(session, None, "root_choice", "help")
    return TurnResult(
        "I can help with internship tasks (2, 3, 4), Python learning, or submission guidance. "
        "Which area would you like?",
        "help",
    )


def _task_tree(session: SessionState, _: str) -> TurnResult:
    _set_context(session, "tasks", "task_selection", "task_tree")
    return TurnResult(
        "Task guidance: choose Task 2 (Fibonacci), Task 3 (file automation), or Task 4 (this rule-based chatbot).",
        "task_tree",
    )


def _task_two(session: SessionState, _: str) -> TurnResult:
    _set_context(session, "tasks", "task2_followup", "task2")
    return TurnResult(
        "Task 2 generates exactly count Fibonacci terms, validates invalid input, emits JSON, and benchmarks with timeit. "
        "Reproduce it with: python -m internship.task2 --count 10. Ask about output, validation, or benchmarking.",
        "task2",
    )


def _task_three(session: SessionState, _: str) -> TurnResult:
    _set_context(session, "tasks", "task3_followup", "task3")
    return TurnResult(
        "Task 3 previews then safely organizes synthetic-workspace files, extracts log records, and verifies a master CSV. "
        "Use an artifact child workspace and --apply only after preview. Ask about preview, CSV, or safety.",
        "task3",
    )


def _task_four(session: SessionState, _: str) -> TurnResult:
    _set_context(session, "tasks", "task4_followup", "task4")
    return TurnResult(
        "Task 4 is this local rule-based terminal chatbot. It normalizes text, routes intents with a dictionary, tracks session state, and handles fallbacks. "
        "It is being used now; final PDF work is not part of this session.",
        "task4",
    )


def _python_tree(session: SessionState, _: str) -> TurnResult:
    _set_context(session, "python", "python_topic", "python_tree")
    return TurnResult(
        "Python learning: choose fundamentals, lists and loops, functions and validation, or regex and file handling.",
        "python_tree",
    )


def _python_lists(session: SessionState, _: str) -> TurnResult:
    _set_context(session, "python", "python_topic", "python_lists")
    return TurnResult(
        "Lists keep ordered values. A for loop visits each item: for value in values: ... . "
        "For Task 2, the list stores Fibonacci terms in generation order. Ask about functions, regex, or another Python topic.",
        "python_lists",
    )


def _python_functions(session: SessionState, _: str) -> TurnResult:
    _set_context(session, "python", "python_topic", "python_functions")
    return TurnResult(
        "Functions group reusable behavior. Validate inputs at the boundary, raise clear exceptions, and return predictable values. "
        "Task 2's fibonacci(count) is an example of this pattern.",
        "python_functions",
    )


def _python_regex(session: SessionState, _: str) -> TurnResult:
    _set_context(session, "python", "python_topic", "python_regex")
    return TurnResult(
        "Regular expressions describe text patterns. Task 3 uses them for synthetic email and TXN identifiers, then records source paths and line numbers. "
        "File handling should validate paths and decode text explicitly.",
        "python_regex",
    )


def _python_fundamentals(session: SessionState, _: str) -> TurnResult:
    _set_context(session, "python", "python_topic", "python_fundamentals")
    return TurnResult(
        "Python fundamentals include variables, conditionals, loops, functions, and clear error handling. "
        "Choose lists, functions, or regex for a focused explanation.",
        "python_fundamentals",
    )


def _submission_tree(session: SessionState, _: str) -> TurnResult:
    _set_context(session, "submission", "submission_followup", "submission")
    return TurnResult(
        "Submission guidance: the notice says complete at least 3 of 4 tasks and combine work into one PDF. "
        "It names 18 October 2026, but no exact deadline hour is verified. Ask about the PDF, deadline, or Task 1.",
        "submission",
    )


def _submission_followup(session: SessionState, text: str) -> TurnResult:
    tokens = _tokens(text)
    if tokens & {"rule", "rules", "requirement", "requirements", "certificate"}:
        message = "The supplied notice says to complete and submit at least 3 of the 4 assigned tasks for the Internship Completion Certificate. The chatbot cannot determine an individual certificate decision."
        intent = "submission_rule"
    elif "deadline" in tokens or "october" in tokens:
        message = "The supplied notice names 18 October 2026. Its exact cutoff time and timezone are not confirmed."
        intent = "submission_deadline"
    elif "pdf" in tokens or "report" in tokens:
        message = "The notice requires one combined PDF for the selected task reports. Final PDF generation and form submission are not performed by this chatbot."
        intent = "submission_pdf"
    elif ("task" in tokens and "1" in tokens) or "linkedin" in tokens:
        message = "Task 1 and LinkedIn are optional under the available project instructions and remain outside the mandatory Tasks 2–4 workflow."
        intent = "submission_task1"
    else:
        return _clarification(
            session,
            "I can clarify the three-of-four rule, one-PDF requirement, deadline date, or optional Task 1. Which one?",
            "Choose the three-of-four rule, PDF, deadline, or Task 1.",
        )
    _set_context(session, "submission", "submission_followup", intent)
    return TurnResult(message, intent)


def _task_four_followup(session: SessionState, text: str) -> TurnResult:
    """Answer only supported Task 4 follow-ups; clarify unrelated requests."""
    tokens = _tokens(text)
    if tokens & {"operate", "operation", "work", "works", "working"}:
        _set_context(session, "tasks", "task4_followup", "task4_operation")
        return TurnResult(
            "The terminal loop reads one line at a time, normalizes it, routes it, and prints a reply. EOF, Ctrl+C, reset, and exit have explicit safe paths.",
            "task4_operation",
        )
    if tokens & {"intent", "intents", "route", "routes", "routing"}:
        _set_context(session, "tasks", "task4_followup", "task4_intents")
        return TurnResult(
            "Task 4 uses a dictionary of intent handlers. Global controls and explicit topic switches are checked before the current pending help choice.",
            "task4_intents",
        )
    if tokens & {"normalize", "normalization", "unicode", "punctuation", "casefold"}:
        _set_context(session, "tasks", "task4_followup", "task4_normalization")
        return TurnResult(
            "Task 4 applies Unicode NFKC normalization, casefolding, punctuation handling, and whitespace normalization before token-based routing.",
            "task4_normalization",
        )
    if tokens & {"state", "session", "history", "memory"}:
        _set_context(session, "tasks", "task4_followup", "task4_session")
        return TurnResult(
            "The session keeps the current tree, pending choice, last intent, turn count, and only the most recent 20 normalized turns in memory. It is not persisted.",
            "task4_session",
        )
    if {"tell", "more"} <= tokens or tokens & {"overview", "explain"}:
        _set_context(session, "tasks", "task4_followup", "task4_overview")
        return TurnResult(
            "This Task 4 bot uses normalized text, a functional intent map, nested contextual choices, and bounded in-memory session history. Ask about operation, intents, normalization, or session state.",
            "task4_overview",
        )
    return _clarification(
        session,
        "I do not recognize that as a Task 4 question. Ask about operation, intents, normalization, or session state; or type help/reset.",
        "Choose operation, intents, normalization, or session state.",
    )


INTENT_HANDLERS: dict[str, Callable[[SessionState, str], TurnResult]] = {
    "help": _general_help,
    "task_tree": _task_tree,
    "task2": _task_two,
    "task3": _task_three,
    "task4": _task_four,
    "python_tree": _python_tree,
    "python_lists": _python_lists,
    "python_functions": _python_functions,
    "python_regex": _python_regex,
    "python_fundamentals": _python_fundamentals,
    "submission": _submission_tree,
}


def detect_intent(normalized: str, session: SessionState) -> str:
    """Detect global intents and explicit tree changes before pending follow-ups."""
    tokens = _tokens(normalized)
    if not normalized:
        return "blank"
    if normalized in {"exit", "quit", "bye", "goodbye"}:
        return "exit"
    if normalized in {"reset", "cancel", "back"}:
        return "reset"
    if normalized in {"help", "menu", "options"}:
        return "help"
    if "submission" in tokens or "submit" in tokens:
        return "submission"
    if ("deadline" in tokens or "pdf" in tokens) and session.current_tree != "submission":
        return "submission"
    if "python" in tokens:
        return "python_tree"
    if session.current_tree != "python" and (tokens & {"regex", "regular", "lists", "loops"}):
        return "python_tree"
    if ("task" in tokens and "2" in tokens) or normalized in {"2", "task2"}:
        return "task2"
    if ("task" in tokens and "3" in tokens) or normalized in {"3", "task3"}:
        return "task3"
    if ("task" in tokens and "4" in tokens) or normalized in {"4", "task4", "chatbot"}:
        return "task4"
    if "tasks" in tokens or "internship" in tokens:
        return "task_tree"
    return "pending" if session.pending_choice else "unknown"


def _pending_response(session: SessionState, normalized: str) -> TurnResult:
    tokens = _tokens(normalized)
    # Deliberate nested state logic: each pending tree accepts only contextual choices.
    if session.pending_choice == "root_choice":
        if tokens & {"task", "tasks", "internship"}:
            return _task_tree(session, normalized)
        elif tokens & {"python", "learn"}:
            return _python_tree(session, normalized)
        elif tokens & {"submission", "submit"}:
            return _submission_tree(session, normalized)
        return _clarification(session, "Please choose tasks, python, or submission.", "Choose tasks, python, or submission.")
    if session.pending_choice == "task_selection":
        if normalized in {"2", "task 2", "task2"}:
            return _task_two(session, normalized)
        elif normalized in {"3", "task 3", "task3"}:
            return _task_three(session, normalized)
        elif normalized in {"4", "task 4", "task4", "chatbot"}:
            return _task_four(session, normalized)
        return _clarification(session, "Please select Task 2, Task 3, or Task 4.", "Select Task 2, Task 3, or Task 4.")
    if session.pending_choice == "python_topic":
        if tokens & {"list", "lists", "loop", "loops"}:
            return _python_lists(session, normalized)
        elif tokens & {"function", "functions", "validation", "validate"}:
            return _python_functions(session, normalized)
        elif tokens & {"regex", "regular", "file", "files", "handling"}:
            return _python_regex(session, normalized)
        elif tokens & {"fundamental", "fundamentals", "basic", "basics"}:
            return _python_fundamentals(session, normalized)
        return _clarification(
            session,
            "That is ambiguous here. Choose fundamentals, lists and loops, functions and validation, or regex and file handling.",
            "Choose fundamentals, lists and loops, functions and validation, or regex and file handling.",
        )
    if session.pending_choice == "task2_followup":
        if tokens & {"benchmark", "timeit", "timing"}:
            return TurnResult("Benchmark Task 2 with: python -m internship.task2 --benchmark --benchmark-counts 10 100 1000 --repeats 5 --number 100.", "task2_benchmark")
        elif tokens & {"output", "json", "result"}:
            return TurnResult("Task 2 prints a JSON array, for example count 10 gives [0,1,1,2,3,5,8,13,21,34].", "task2_output")
        elif tokens & {"validation", "negative", "invalid"}:
            return TurnResult("Negative counts raise ValueError; bool, float, string, and None are rejected rather than coerced.", "task2_validation")
        return _clarification(
            session,
            "For Task 2, ask about output, validation, or benchmarking; or switch topics with python, tasks, or submission.",
            "Choose output, validation, benchmarking, or an explicit topic switch.",
        )
    if session.pending_choice == "task3_followup":
        if tokens & {"preview", "apply", "safety"}:
            return TurnResult("Task 3 previews first. Apply only inside an isolated artifacts/task3 child workspace, after strict path and UTF-8 checks.", "task3_safety")
        elif tokens & {"csv", "record", "log"}:
            return TurnResult("Task 3 writes and reads back a UTF-8 master CSV with source path, line number, kind, and value.", "task3_csv")
        return _clarification(
            session,
            "For Task 3, ask about preview/safety or CSV/log records.",
            "Choose preview/safety or CSV/log records.",
        )
    if session.pending_choice == "task4_followup":
        return _task_four_followup(session, normalized)
    if session.pending_choice == "submission_followup":
        return _submission_followup(session, normalized)
    return TurnResult("I lost the earlier context. Type help to choose a topic.", "unknown")


def handle_turn(text: str, session: SessionState) -> TurnResult:
    """Route one user turn and mutate only the supplied in-memory session."""
    normalized = normalize(text)
    _record(session, normalized)
    intent = detect_intent(normalized, session)
    if intent == "exit":
        session.active = False
        session.last_intent = "exit"
        return TurnResult("Goodbye. This session was local and no information was saved or submitted.", "exit", True)
    if intent == "reset":
        session.current_tree = None
        session.pending_choice = "root_choice"
        session.last_intent = "reset"
        session.history = [normalized]
        session.fallback_count = 0
        return TurnResult("Context reset. Choose tasks, python, or submission.", "reset")
    if intent == "blank":
        session.last_intent = "blank"
        return TurnResult("Please enter a topic, or type help for tasks, python, and submission guidance.", "blank")
    if intent in INTENT_HANDLERS:
        return INTENT_HANDLERS[intent](session, normalized)
    if intent == "pending":
        result = _pending_response(session, normalized)
        session.last_intent = result.intent
        if result.intent != "ambiguous":
            session.clarification_count = 0
            session.fallback_count = 0
        return result
    session.fallback_count += 1
    session.last_intent = "unknown"
    if session.fallback_count >= 2:
        return TurnResult("I still do not recognize that request. Type help, or reset to clear the current context.", "unknown")
    return TurnResult("I do not recognize that request. Try tasks, python, submission, help, reset, or exit.", "unknown")


def run_cli(input_fn: Callable[[str], str] = input, output_fn: Callable[[str], None] = print, error_fn: Callable[[str], None] | None = None) -> int:
    """Run the interactive terminal loop with graceful normal termination paths."""
    error_fn = error_fn or (lambda message: print(message, file=sys.stderr))
    session = SessionState()
    output_fn(_opening())
    try:
        while session.active:
            try:
                user_text = input_fn("you> ")
            except EOFError:
                output_fn("End of input. Goodbye; no session data was saved or submitted.")
                return 0
            except KeyboardInterrupt:
                output_fn("Interrupted safely. Goodbye; no session data was saved or submitted.")
                return 0
            result = handle_turn(user_text, session)
            output_fn(result.text)
            if result.should_exit:
                return 0
    except Exception as error:
        error_fn(f"Chatbot internal error: {type(error).__name__}: {error}")
        return 1
    return 0


def main() -> int:
    return run_cli()


if __name__ == "__main__":
    sys.exit(main())
