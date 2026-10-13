"""Stateful and subprocess tests for the local Task 4 rule-based chatbot."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from internship import task4


ROOT = Path(__file__).resolve().parents[1]


class Task4CoreTests(unittest.TestCase):
    def test_normalization_handles_unicode_case_punctuation_and_whitespace(self) -> None:
        self.assertEqual(task4.normalize("  Ｐｙｔｈｏｎ—LISTS!!!  "), "python lists")
        self.assertEqual(task4.normalize("Café\t\nREGEX"), "café regex")
        self.assertEqual(task4.normalize("!!!"), "")
        with self.assertRaises(TypeError):
            task4.normalize(None)  # type: ignore[arg-type]

    def test_exact_token_matching_avoids_accidental_substrings(self) -> None:
        session = task4.SessionState()
        self.assertEqual(task4.detect_intent("this", session), "unknown")
        self.assertEqual(task4.detect_intent("submission", session), "submission")
        self.assertEqual(task4.detect_intent("task 2", session), "task2")

    def test_task_help_tree_explains_every_required_task(self) -> None:
        session = task4.SessionState()
        self.assertEqual(task4.handle_turn("tasks", session).intent, "task_tree")
        task2 = task4.handle_turn("2", session)
        self.assertEqual(task2.intent, "task2")
        self.assertIn("Fibonacci", task2.text)
        task3 = task4.handle_turn("task 3", session)
        self.assertEqual(task3.intent, "task3")
        self.assertIn("master CSV", task3.text)
        task4_reply = task4.handle_turn("task 4", session)
        self.assertEqual(task4_reply.intent, "task4")
        self.assertIn("rule-based", task4_reply.text)
        self.assertIn("final PDF work is not", task4_reply.text)

    def test_task2_contextual_followup_uses_existing_state(self) -> None:
        session = task4.SessionState()
        task4.handle_turn("task 2", session)
        reply = task4.handle_turn("how do i benchmark it", session)
        self.assertEqual(reply.intent, "task2_benchmark")
        self.assertIn("--benchmark", reply.text)
        self.assertEqual(session.current_tree, "tasks")
        self.assertEqual(session.pending_choice, "task2_followup")
        self.assertEqual(session.last_intent, "task2_benchmark")

    def test_python_tree_covers_all_topics(self) -> None:
        session = task4.SessionState()
        task4.handle_turn("python", session)
        self.assertIn("Lists keep ordered", task4.handle_turn("lists and loops", session).text)
        self.assertIn("Functions group", task4.handle_turn("functions", session).text)
        self.assertIn("Regular expressions", task4.handle_turn("regex", session).text)
        self.assertIn("fundamentals", task4.handle_turn("basics", session).text)

    def test_submission_tree_has_verified_boundaries(self) -> None:
        session = task4.SessionState()
        initial = task4.handle_turn("submission", session)
        self.assertIn("at least 3 of 4", initial.text)
        deadline = task4.handle_turn("deadline", session)
        self.assertIn("18 October 2026", deadline.text)
        self.assertIn("not confirmed", deadline.text)
        pdf = task4.handle_turn("pdf", session)
        self.assertIn("not performed", pdf.text)
        task_one = task4.handle_turn("Task 1 LinkedIn", session)
        self.assertIn("optional", task_one.text)

    def test_contextual_help_trees_update_last_intent(self) -> None:
        session = task4.SessionState()
        task4.handle_turn("task 2", session)
        self.assertEqual(session.last_intent, "task2")
        task4.handle_turn("benchmark", session)
        self.assertEqual(session.last_intent, "task2_benchmark")
        task4.handle_turn("output", session)
        self.assertEqual(session.last_intent, "task2_output")

        task4.handle_turn("task 3", session)
        task4.handle_turn("preview", session)
        self.assertEqual(session.last_intent, "task3_safety")
        task4.handle_turn("csv", session)
        self.assertEqual(session.last_intent, "task3_csv")

        task4.handle_turn("task 4", session)
        task4.handle_turn("normalization", session)
        self.assertEqual(session.last_intent, "task4_normalization")
        task4.handle_turn("session history", session)
        self.assertEqual(session.last_intent, "task4_session")

        task4.handle_turn("submission", session)
        task4.handle_turn("rule", session)
        self.assertEqual(session.last_intent, "submission_rule")
        task4.handle_turn("deadline", session)
        self.assertEqual(session.last_intent, "submission_deadline")
        task4.handle_turn("pdf", session)
        self.assertEqual(session.last_intent, "submission_pdf")

        task4.handle_turn("python", session)
        task4.handle_turn("lists", session)
        self.assertEqual(session.last_intent, "python_lists")

    def test_explicit_topic_change_overrides_pending_followup(self) -> None:
        session = task4.SessionState()
        task4.handle_turn("task 2", session)
        switched = task4.handle_turn("python concepts", session)
        self.assertEqual(switched.intent, "python_tree")
        self.assertEqual(session.current_tree, "python")
        self.assertEqual(session.pending_choice, "python_topic")

    def test_ambiguity_requests_clarification(self) -> None:
        session = task4.SessionState()
        task4.handle_turn("python", session)
        reply = task4.handle_turn("explain it", session)
        self.assertEqual(reply.intent, "ambiguous")
        self.assertIn("ambiguous", reply.text)
        self.assertEqual(session.pending_choice, "python_topic")

    def test_repeated_task_selection_ambiguity_escalates_and_recovers(self) -> None:
        session = task4.SessionState()
        task4.handle_turn("tasks", session)
        first = task4.handle_turn("something", session)
        second = task4.handle_turn("still something", session)
        self.assertEqual(first.intent, "ambiguous")
        self.assertEqual(second.intent, "ambiguous")
        self.assertIn("still need a clear choice", second.text)
        self.assertIn("help", second.text)
        self.assertEqual(session.last_intent, "ambiguous")
        self.assertEqual(session.clarification_count, 2)
        task4.handle_turn("task 3", session)
        self.assertEqual(session.last_intent, "task3")
        self.assertEqual(session.clarification_count, 0)

    def test_repeated_python_topic_ambiguity_escalates_and_recovers(self) -> None:
        session = task4.SessionState()
        task4.handle_turn("python", session)
        task4.handle_turn("explain it", session)
        second = task4.handle_turn("more", session)
        self.assertIn("still need a clear choice", second.text)
        task4.handle_turn("regex", session)
        self.assertEqual(session.last_intent, "python_regex")
        self.assertEqual(session.clarification_count, 0)

    def test_repeated_contextual_followup_ambiguity_escalates_and_recovers(self) -> None:
        session = task4.SessionState()
        task4.handle_turn("task 2", session)
        task4.handle_turn("explain", session)
        second = task4.handle_turn("another unclear question", session)
        self.assertIn("still need a clear choice", second.text)
        self.assertIn("output", second.text)
        task4.handle_turn("validation", session)
        self.assertEqual(session.last_intent, "task2_validation")
        self.assertEqual(session.clarification_count, 0)

    def test_reset_clears_clarification_recovery_state(self) -> None:
        session = task4.SessionState()
        task4.handle_turn("tasks", session)
        task4.handle_turn("unclear", session)
        repeated = task4.handle_turn("still unclear", session)
        self.assertIn("still need a clear choice", repeated.text)
        self.assertEqual(session.clarification_count, 2)
        turns_before_reset = session.turn_count

        reset = task4.handle_turn("reset", session)
        self.assertEqual(reset.intent, "reset")
        self.assertEqual(session.clarification_count, 0)
        self.assertEqual(session.history, ["reset"])
        self.assertEqual(session.turn_count, turns_before_reset + 1)
        self.assertEqual(session.pending_choice, "root_choice")

        first_after_reset = task4.handle_turn("unclear again", session)
        self.assertEqual(first_after_reset.intent, "ambiguous")
        self.assertIn("Please choose tasks", first_after_reset.text)
        self.assertNotIn("still need a clear choice", first_after_reset.text)
        self.assertEqual(session.clarification_count, 1)

    def test_session_independence_and_history_bound(self) -> None:
        first = task4.SessionState()
        second = task4.SessionState()
        task4.handle_turn("task 2", first)
        self.assertEqual(second.current_tree, None)
        for number in range(task4.HISTORY_LIMIT + 5):
            task4.handle_turn(f"unknown {number}", second)
        self.assertEqual(len(second.history), task4.HISTORY_LIMIT)
        self.assertEqual(second.turn_count, task4.HISTORY_LIMIT + 5)
        self.assertNotEqual(first.history, second.history)

    def test_reset_cancel_blank_unknown_and_exit(self) -> None:
        session = task4.SessionState()
        task4.handle_turn("task 3", session)
        reset = task4.handle_turn("reset", session)
        self.assertEqual(reset.intent, "reset")
        self.assertEqual(session.current_tree, None)
        self.assertEqual(session.pending_choice, "root_choice")
        self.assertEqual(session.history, ["reset"])
        self.assertEqual(task4.handle_turn("?!", session).intent, "blank")
        fresh = task4.SessionState()
        self.assertIn("do not recognize", task4.handle_turn("unfamiliar", fresh).text)
        self.assertIn("still do not recognize", task4.handle_turn("unfamiliar again", fresh).text)
        exit_reply = task4.handle_turn("exit", session)
        self.assertTrue(exit_reply.should_exit)
        self.assertFalse(session.active)

    def test_help_root_selection_cancel_and_task4_followup(self) -> None:
        session = task4.SessionState()
        help_reply = task4.handle_turn("HELP!!!", session)
        self.assertEqual(help_reply.intent, "help")
        self.assertEqual(session.pending_choice, "root_choice")
        self.assertEqual(task4.handle_turn("tasks", session).intent, "task_tree")
        self.assertEqual(task4.handle_turn("4", session).intent, "task4")
        self.assertEqual(task4.handle_turn("tell me more", session).intent, "task4_overview")
        cancelled = task4.handle_turn("cancel", session)
        self.assertEqual(cancelled.intent, "reset")
        self.assertEqual(session.current_tree, None)

    def test_task4_followup_recognizes_supported_questions_and_rejects_unrelated_text(self) -> None:
        session = task4.SessionState()
        task4.handle_turn("task 4", session)
        operation = task4.handle_turn("how does it work", session)
        self.assertEqual(operation.intent, "task4_operation")
        self.assertEqual(session.last_intent, "task4_operation")
        routing = task4.handle_turn("what intents are routed", session)
        self.assertEqual(routing.intent, "task4_intents")
        unknown = task4.handle_turn("what is the weather", session)
        self.assertEqual(unknown.intent, "ambiguous")
        self.assertIn("do not recognize", unknown.text)
        self.assertEqual(session.last_intent, "ambiguous")
        repeated = task4.handle_turn("still weather", session)
        self.assertIn("still need a clear choice", repeated.text)


class Task4CliTests(unittest.TestCase):
    def test_run_cli_handles_eof_and_keyboard_interrupt(self) -> None:
        outputs: list[str] = []
        self.assertEqual(task4.run_cli(input_fn=lambda _: (_ for _ in ()).throw(EOFError()), output_fn=outputs.append), 0)
        self.assertIn("End of input", outputs[-1])

        interrupted: list[str] = []
        self.assertEqual(task4.run_cli(input_fn=lambda _: (_ for _ in ()).throw(KeyboardInterrupt()), output_fn=interrupted.append), 0)
        self.assertIn("Interrupted safely", interrupted[-1])

    def test_run_cli_reports_unexpected_errors_with_failure_exit(self) -> None:
        errors: list[str] = []
        result = task4.run_cli(input_fn=lambda _: 7, output_fn=lambda _: None, error_fn=errors.append)  # type: ignore[return-value]
        self.assertEqual(result, 1)
        self.assertIn("Chatbot internal error: TypeError", errors[0])

    def test_scripted_subprocess_conversation_is_multi_intent_and_exits_cleanly(self) -> None:
        conversation = "\n".join(
            [
                "help",
                "task 2",
                "how do i benchmark it",
                "python concepts",
                "explain it",
                "lists",
                "submission",
                "deadline",
                "unrecognized wording",
                "reset",
                "exit",
            ]
        ) + "\n"
        result = subprocess.run(
            [sys.executable, "-m", "internship.task4"],
            cwd=ROOT,
            input=conversation,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Task 2 generates", result.stdout)
        self.assertIn("--benchmark", result.stdout)
        self.assertIn("Python learning", result.stdout)
        self.assertIn("ambiguous", result.stdout)
        self.assertIn("Lists keep ordered", result.stdout)
        self.assertIn("18 October 2026", result.stdout)
        self.assertIn("Context reset", result.stdout)
        self.assertIn("Goodbye", result.stdout)

    def test_subprocess_eof_terminates_gracefully(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "internship.task4"],
            cwd=ROOT,
            input="",
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("End of input", result.stdout)


if __name__ == "__main__":
    unittest.main()
