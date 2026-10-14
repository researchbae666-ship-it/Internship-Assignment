"""Validate reviewer-attributed snapshots; never turn them into a post inventory."""
import json
from datetime import date
from pathlib import Path

DIRECTORY = Path(__file__).resolve().parent
ACCOUNTS = {'Stanley 1913': 'stanley1913_brand', 'Hydro Flask': 'hydroflask', 'Owala': 'owala'}


def load():
    data = json.loads((DIRECTORY / 'observations.json').read_text())
    return validate(data)


def validate(data):
    if data['source_note'] != 'VERIFIED_SOURCE_NOTE_2026-10-14.md':
        raise ValueError('Unexpected provenance note')
    note = (DIRECTORY / data['source_note']).read_text()
    days = (date.fromisoformat(data['snapshot_end']) - date.fromisoformat(data['snapshot_start'])).days
    if days != 26 or data['nominal_interval_days'] != days:
        raise ValueError('Not the documented nominal 26-day interval')
    if data['collected_date_utc'] != '2026-10-14' or data['engagement_month'] != '2026-10':
        raise ValueError('Source dates do not match the reviewer note')
    if 'not Codex retrieval' not in data['provenance'] or 'No raw HTML snapshot' not in note:
        raise ValueError('Independent secondary provenance required')
    if len(data['rows']) != 3 or {r['brand'] for r in data['rows']} != set(ACCOUNTS):
        raise ValueError('Exactly three distinct approved brands required')
    for row in data['rows']:
        handle = ACCOUNTS[row['brand']]
        if row['handle'] != handle or row['url'] != f'https://hypeauditor.com/instagram/{handle}/':
            raise ValueError('Brand/account/source mismatch')
        for field in ('start_total', 'end_total'):
            if type(row[field]) is not int or row[field] < 0:
                raise ValueError('Invalid cumulative count')
        rate = row['vendor_estimated_october_engagement_percent']
        if type(rate) not in (float, int) or not 0 <= rate <= 100:
            raise ValueError('Invalid vendor rate')
        source_row = next(line for line in note.splitlines() if f'`@{handle}`' in line)
        if row['url'] not in source_row or f"{row['start_total']:,}" not in source_row or f"{row['end_total']:,}" not in source_row:
            raise ValueError('Counts do not match supplied note')
        rate_row = next(line for line in note.splitlines() if line.startswith('| ' + row['brand'] + ' |'))
        if f'{rate:.2f}%' not in rate_row:
            raise ValueError('Rate does not match supplied note')
        for field in ('verified_period_post_count', 'exact_28_day_posts_per_week', 'independently_calculated_period_engagement_percent'):
            if row[field] is not None:
                raise ValueError('First-party period measurements must remain unavailable')
    return data


def calculate(data):
    validate(data)
    rows = []
    for source in data['rows']:
        row = dict(source)
        row['net_change'] = row['end_total'] - row['start_total']
        row['nominal_net_change_per_week_proxy'] = row['net_change'] / data['nominal_interval_days'] * 7
        row['proxy_unit'] = 'net cumulative-count change per nominal week; NOT verified publication frequency'
        rows.append(row)
    return rows
