"""One definition of a GPU's public identity.

The sanitizer and the data generator both need to agree on the id a card is
published under. They each carried their own copy of this function once, and
the copies drifted: every id was hashed twice on its way to the leaderboard,
and the id shown on the site matched nothing in database/.

The owner decided (2026-08-31) that the public identity IS the report's UUID,
verbatim. A GPU UUID identifies a card, not a host, it is load-bearing for
dedup, grouping and per-card history, and publishing it means the id on the
site can always be found in the report it came from. Reports imported while
this function hashed ids only have the pseudonym left -- those cards keep
their ``GPU-<12 hex>`` form, which is just another stable opaque string.

Keep this the single definition: any module that grows its own copy will
drift, and that is the bug this file exists to prevent.
"""

UNKNOWN_IDS = {"unknown", "n/a", "none", "[n/a]", ""}


def public_gpu_id(raw, unknown="Unknown"):
    """Return the id a GPU is published under: its UUID, unchanged.

    Applying this more than once is a no-op by construction, and unknown
    markers normalise to a single spelling so anonymous cards group sanely.
    """
    text = str(raw if raw is not None else "").strip()
    if text.lower() in UNKNOWN_IDS:
        return text or unknown
    return text
