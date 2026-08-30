"""One definition of a GPU's public identity.

The sanitizer and the data generator both need to turn a GPU UUID into the
pseudonym published on the site. They each carried their own copy, and the
copies drifted: the sanitizer learned not to re-hash a value already in
pseudonym form, the generator never did. So every id was hashed twice on its
way to the leaderboard, and the id shown on the site matched nothing in
database/ -- a card with 152 reports could not be found under the id those
reports carried.

Identity is only ever compared for equality, so a hash preserves dedup,
grouping and per-card history exactly. Publishing the raw UUID buys nothing
and hands out a persistent hardware identifier that, next to the driver, OS
and run timestamps, fingerprints a specific machine.
"""

import hashlib
import os
import re

# A UUID has enough entropy that an unsalted hash is not brute-forceable, but
# anyone already holding one can confirm whether that card is in the dataset.
# Set PANTHEON_ID_SALT to close that off, and keep it stable: changing it
# renames every card and breaks continuity with everything already published.
PUBLIC_ID_SALT = os.environ.get("PANTHEON_ID_SALT", "")

UNKNOWN_IDS = {"unknown", "n/a", "none", "[n/a]", ""}

# A value already in pseudonym form must be left alone. Hashing it again gives
# the same physical GPU a different identity, so a card seen before and after
# an import splits in two.
PSEUDONYM = re.compile(r"^GPU-[0-9a-f]{12}$")


def public_gpu_id(raw, unknown="Unknown"):
    """Return a stable pseudonym for a GPU UUID.

    Passing a pseudonym back in returns it unchanged, so this is safe to apply
    more than once to the same value.
    """
    text = str(raw if raw is not None else "").strip()
    if text.lower() in UNKNOWN_IDS:
        return text or unknown
    if PSEUDONYM.match(text):
        return text
    return "GPU-" + hashlib.sha256(
        (PUBLIC_ID_SALT + text).encode("utf-8")).hexdigest()[:12]
