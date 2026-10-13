"""Execute the proposed routing policy using synthetic states only."""
import unittest
from email_workflows import POLICY, State, transition, workflows


class WorkflowTests(unittest.TestCase):
    def test_each_workflow_enters_and_completes_in_order(self):
        for flow in workflows():
            with self.subTest(flow=flow["id"]):
                state = State(purchased=flow["id"] == "post_purchase")
                self.assertEqual("entered", transition(state, flow["entry_event"], 0))
                for message in flow["messages"]:
                    self.assertEqual("eligible_draft:" + message["id"], transition(state, "tick", message["delay_hours_from_entry"]))
                self.assertIsNone(state.active)
                self.assertIn(flow["id"], state.finished)

    def test_delays_and_duplicate_entry_preserve_clock(self):
        state = State()
        transition(state, "product_view_twice", 0)
        self.assertEqual("waiting", transition(state, "tick", 23))
        self.assertEqual("duplicate_blocked", transition(state, "product_view_twice", 23))
        self.assertEqual(0, state.entered_at)
        self.assertEqual("eligible_draft:browse-1", transition(state, "tick", 24))

    def test_all_suppression_events_exit_every_workflow(self):
        for flow in workflows():
            for event in ("unsubscribe", "consent_withdrawal", "hard_bounce", "complaint", "suppression"):
                with self.subTest(flow=flow["id"], event=event):
                    state = State(purchased=flow["id"] == "post_purchase")
                    transition(state, flow["entry_event"], 0)
                    self.assertEqual("suppressed", transition(state, event, 1))
                    self.assertEqual("suppressed", transition(state, "tick", 1000))
                    self.assertEqual([], state.sent_at)

    def test_no_consent_blocks_all_entries(self):
        for flow in workflows():
            state = State(consent=False, purchased=flow["id"] == "post_purchase")
            self.assertEqual("suppressed", transition(state, flow["entry_event"], 0))

    def test_purchase_exits_pre_purchase_and_repeat_purchase_exits_care(self):
        for flow in workflows():
            state = State(purchased=flow["id"] == "post_purchase")
            transition(state, flow["entry_event"], 0)
            self.assertEqual("purchase_exit", transition(state, "purchase", 1))
            self.assertIsNone(state.active)
            self.assertEqual("no_action", transition(state, "tick", 1000))

    def test_priority_prevents_overlapping_workflows(self):
        state = State()
        transition(state, "subscription_confirmed", 0)
        transition(state, "product_view_twice", 1)
        self.assertEqual("browse", state.active)
        self.assertEqual("entered", transition(state, "cart_abandoned", 2))
        self.assertEqual("cart", state.active)
        self.assertEqual("duplicate_blocked", transition(state, "product_view_twice", 3))
        self.assertEqual("cart", state.active)
        other = State()
        transition(other, "cart_abandoned", 0)
        self.assertEqual("lower_priority_blocked", transition(other, "subscription_confirmed", 1))

    def test_post_purchase_requires_purchase_and_delivery(self):
        state = State()
        self.assertEqual("ineligible", transition(state, "delivery_confirmed", 0))
        transition(state, "purchase", 0)
        self.assertEqual("no_action", transition(state, "tick", 336))
        self.assertEqual("entered", transition(state, "delivery_confirmed", 337))
        self.assertEqual("ineligible", transition(state, "cart_abandoned", 338))

    def test_frequency_gap_defers_without_advancing(self):
        state = State(sent_at=[0])
        transition(state, "cart_abandoned", 1)
        self.assertEqual("deferred_frequency_cap", transition(state, "tick", 5))
        self.assertEqual(0, state.next_step)
        self.assertEqual("eligible_draft:cart-1", transition(state, "tick", 24))

    def test_rolling_cap_defers_and_never_bursts_overdue_steps(self):
        state = State(sent_at=[-48, -24, 0])
        transition(state, "subscription_confirmed", 0)
        self.assertEqual("deferred_frequency_cap", transition(state, "tick", 24))
        self.assertEqual(0, state.next_step)
        self.assertEqual("eligible_draft:welcome-1", transition(state, "tick", 120))
        self.assertEqual("deferred_frequency_cap", transition(state, "tick", 120))

    def test_inactivity_and_deadline_expire_all_flows(self):
        for flow in workflows():
            state = State(purchased=flow["id"] == "post_purchase")
            transition(state, flow["entry_event"], 0)
            self.assertEqual("expired", transition(state, "tick", flow["expires_after_hours"]))
            state = State(purchased=flow["id"] == "post_purchase")
            transition(state, flow["entry_event"], 0)
            self.assertEqual("waiting_inactivity_deadline", transition(state, "inactivity", 1))
            self.assertEqual("inactivity_exit", transition(state, "inactivity", flow["expires_after_hours"]))

    def test_support_pause_and_resume(self):
        state = State(purchased=True)
        transition(state, "delivery_confirmed", 0)
        transition(state, "support_open", 335)
        self.assertEqual("paused_support", transition(state, "tick", 336))
        transition(state, "support_resolved", 337)
        self.assertEqual("eligible_draft:post_purchase-1", transition(state, "tick", 337))

    def test_completion_blocks_reentry(self):
        state = State()
        transition(state, "cart_abandoned", 0)
        transition(state, "tick", 4)
        transition(state, "tick", 52)
        self.assertEqual("duplicate_blocked", transition(state, "cart_abandoned", 100))

    def test_return_to_cart_exits_reminders(self):
        state = State()
        transition(state, "cart_abandoned", 0)
        self.assertEqual("cart_resumed_exit", transition(state, "cart_activity", 3))
        self.assertEqual("no_action", transition(state, "tick", 4))

    def test_consent_is_rechecked_between_messages(self):
        state = State()
        transition(state, "subscription_confirmed", 0)
        transition(state, "tick", 0)
        state.consent = False
        self.assertEqual("suppressed", transition(state, "tick", 48))
        self.assertEqual([0], state.sent_at)


if __name__ == "__main__":
    unittest.main(verbosity=2)
