"""Shared safety and Rules-of-Engagement text, used by every front-end.

Centralized so the CLI, the web GUI, and exports state the same thing.
"""

#: One-line Rules-of-Engagement reminder printed on every build and export.
ROE_BANNER = (
    "Rules of Engagement: authorized targets only. dorkforge generates queries; "
    "it does not run them. Do not act on third-party findings without authorization."
)

#: Notice shown whenever broad (internet-wide) results are produced.
BROAD_NOTICE = (
    "Broad results are internet-wide, third-party data, research-only. "
    "Do not act on findings without authorization."
)

#: Per-row advisory marker, so the status travels with each result row and is
#: not merely a single banner line.
TARGETED_ADVISORY = "authorized-scope"
BROAD_ADVISORY = "third-party;research-only;unauthorized-scope"
