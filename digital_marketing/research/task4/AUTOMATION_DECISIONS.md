# Proposed automation decision table

The simulator returns eligible-draft decisions only. It cannot send email.
Authenticated event feeds, consent records, preference links and product claims
would need a separately authorized implementation. All delays are hours from
entry, not from the preceding message. A resumed cart exits the old reminders.

| Qualifying event | Entry filters to enforce upstream | Sequence / expiry |
| --- | --- | --- |
| subscription_confirmed | Confirmed marketing opt-in, no purchase, no higher-priority flow | 0, 48, 120h; expires 168h |
| product_view_twice | Two consented product views in seven days, no purchase/cart | 24, 72h; expires 168h |
| cart_abandoned | Start clock at last cart activity; no purchase; separate consent | 4, 52h; expires 96h; activity exits |
| delivery_confirmed | Prior purchase, verified delivery, consent, no unresolved support | 336, 504, 720h; expires 840h |

| Event / gate | Transition |
| --- | --- |
| purchase | Exit active flow; mark purchase. A later delivery event may enter care; repeat purchase exits care. |
| unsubscribe / consent withdrawal / hard bounce / complaint / global suppression | Clear active flow, persist synthetic suppression, block all later entries/messages. |
| Duplicate entry | Do not restart time or steps. Completed, expired or replaced flows do not replay in this pilot. |
| Competing entry | One active flow. Post-purchase > cart > browse > welcome; higher replaces lower, lower is blocked. |
| Global cap | Minimum 24h between messages, maximum three per rolling 168h. Defer without advancing; never burst overdue steps. |
| support_open / support_resolved | Pause / resume without bypassing cap or extending expiry. |
| inactivity / elapsed expiry | Do not expire early; at deadline exit without a further message. |
| Final message | Complete immediately after its eligible-draft decision. |

Subject, preview, body, CTA, conversion event, consent and exit fields for all
ten messages are in `strategy_data.json`. The report appendix renders them from
these same records. The simulator retains only synthetic state in memory.
