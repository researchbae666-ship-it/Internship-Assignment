# Measurement methodology

## Inclusion and missing values

Use only posts from a verified official account whose public URL and publication
date are retained in `observations.json`. Include posts published within the
shared 28-day window. Missing values remain `null` / unavailable; they are never
converted to zero or estimated from a benchmark.

## Cadence

For each brand and platform:

```text
posts per week = observed included post count / 28 observation days × 7
```

Unit: posts per week. This describes only the verified sample, not an account's
lifetime activity.

## Visible-interaction proxy

Only when the same official account exposes all three inputs:

```text
visible interaction proxy (%) =
    (visible likes + visible comments) / publicly visible follower count × 100
```

The numerator and denominator must be recorded beside the result. This is a
visible-interaction proxy, not platform analytics or a universal engagement
rate. Views, reactions, shares, saves, and subscriber counts are not silently
substituted for those inputs. Platform measures with incompatible denominators
are presented separately and not ranked against each other.
