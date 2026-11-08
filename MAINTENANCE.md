# BECKO profile maintenance

Run `python3 scripts/generate_profile.py --offline` to regenerate from the checked-in snapshot, or set `GH_TOKEN` to a GitHub token and omit `--offline` to refresh. Use `python3 scripts/validate.py` for dependency-free asset checks.

The daily workflow uses only the built-in short-lived Actions token. It needs contents write access to commit generated assets; no custom secret is required. A protected default branch may require PR-based updates instead. Refreshes do not trigger another refresh because the push filter only watches scripts and workflow code.

A failed API refresh fails before replacing the previous snapshot. The workflow never commits a partial refresh if a later generation or validation step fails. Timestamped images make staleness visible. GitHub image caches can delay visible changes.

The native profile graph is controlled by GitHub. The activity dashboard uses exact calendar positions. Commit contributions are the GraphQL collection total; language percentages aggregate public non-fork source bytes.

All animated image references have reduced-motion picture sources. SVGs also include a reduced-motion media query where applicable. GitHub sanitization/proxy/browser behavior can vary; README content has no JavaScript. Verify animation in a browser after publishing and use static assets if a client cannot animate SVG.

Audit: six public repositories were returned on 2026-11-06: becko1602, eDoska, Becko, becko-arch-linux, Code and Test-1. The original README, original achievement graphics and manual snake artifact workflow are preserved in git history or the repository. Original achievement graphics remain available in README details. Existing unrelated local design files were not changed.

Public project sources: eDoska package manifest and source tree; Becko README and actions tree; becko-arch-linux pyproject and source. Local evidence: prep-platform, smartprice-ai and uzex-intelligence documentation and manifests. Local implementations are not advertised as public repositories or verified live deployments. FALCON remains a supplied concept.

Missing evidence: Codeforces URL, regional informatics result, individual event dates/certificates, public links for local projects. Social URLs are explicitly supplied by the author. The earlier Telegram handle is superseded by @becko1602. No KAIST requirements or test results are asserted.

Visual update: angular polygon BECKO lettering inspired by the supplied logo; midnight, cyan, ultraviolet and pink palette. Reference-style About Me, compact technology badges, GitHub Stats, hackathon highlights and developer quote. Snake artwork and its manual workflow are removed. The daily generator retains this layout.
