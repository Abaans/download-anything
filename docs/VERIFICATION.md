# Verification

Release: **0.1.0**. Checked locally on **18 October 2026**, on macOS.

## Automated checks

- Seven packaging tests pass: repository validation, isolated installation of every skill into a path containing spaces, missing-reference rejection, out-of-package-reference rejection, symlink rejection, malformed-metadata rejection, and the exact README installation recipe with existing-installation protection.
- Each installed skill carries its own MIT license, matching name, discovery metadata and bundled references.
- The Codex skill-creator validator accepts each `SKILL.md`.
- The final ZIP is reopened, CRC-checked, compared byte-for-byte with the source tree, extracted to a temporary directory and tested there again. Archive hashes and the owner's review notes are kept outside the published source tree.

The included GitHub Actions workflow runs the packaging suite and validator. Its checkout action is pinned; it needs read-only repository access and no account credentials. The [GitHub Actions tab](https://github.com/Abaans/download-anything/actions) records the remote run for each published commit.

## What the checks do not prove

Structural tests check packaging and installation. They do not run an agent against the prose, measure trigger quality, or certify every instruction. The example prompts are manual review cases, not automated behavioral evaluations.

## Download transport smoke test

`python3 tests/smoke_download.py` passed all five local checks:

1. Direct HTTP download matches the synthetic source bytes, including a filename with spaces and a literal dollar sign.
2. An existing destination causes a failure and its bytes remain intact.
3. A missing HTTP source fails without a misleading completed file.
4. An interrupted transfer preserves its partial/control file, resumes using a positive-offset HTTP range and produces the exact source bytes.
5. A generated MP4 downloaded with yt-dlp and aria2 matches its source and ffprobe confirms duration, 160 × 90 dimensions and both video and audio streams.

Observed tools: aria2 1.37.0, yt-dlp 2026.08.19, FFmpeg/ffprobe 9.0.1. The test starts a temporary loopback server, uses synthetic data, and cleans up its own temporary directory and server. It does not use user accounts or public media sources.

Not exercised: site-specific extractors, authentication, cloud-share resolution, HLS/DASH, separate-stream merging, conversion, subtitles, FTP/SFTP, torrents, Metalink or another operating system. Passing this test does not mean every link is supported. The GitHub workflow runs only the packaging tests; run the transport test separately where its tools are installed.
