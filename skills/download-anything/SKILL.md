---
name: download-anything
description: "Download supported file, video and audio links into readable local files; resume verified transfers and check saved outputs. Use for supplied links, explicit download requests or $download-anything. Requires source access and suitable download tools."
---

# Download Anything

Turn the user's chosen links into verified local files. Match requested names, destinations, formats and quality. “Anything” is the package name: unsupported sites, expired links, DRM and access restrictions can still prevent a download.

## Route the request

| Source | Route |
|---|---|
| Direct HTTP(S), FTP or SFTP file | aria2c |
| Video/audio page supported by yt-dlp | yt-dlp; ffmpeg for merging/conversion; ffprobe for checks |
| Cloud share, release page or document viewer | Resolve the requested file through official links or an authorized browser/connector |
| Torrent, magnet or Metalink | Explicitly requested protocol mode; inspect multi-file scope first |
| Login-protected source | Scoped authorized access through the host's supported browser or connector |

Read [transfer recipes](references/transfers.md) for executable command patterns and media choices. Read [authenticated sources](references/authenticated-sources.md) only when access requires a signed-in session or browser extraction.

Check the required executable on the current host. Do not assume dependencies are installed, reinstall working tools or treat one machine's setup as portable. Install missing tools only within the user's scope. Prefer current official documentation for a version-specific problem. This skill does not bundle those tools or a browser driver.

## Name and place the result

User filenames and destinations override defaults independently. Otherwise use the user's Downloads directory with shallow categories: YouTube, Instagram/Reels, Instagram/Stories, Audio, Documents, Images, Archives or Other. Resolve the real user directory on the host; do not hard-code a username or assume a shell expansion works everywhere.

Use actual source titles, preserving their language and meaningful punctuation. Remove path separators, traversal, unsupported filename characters and trailing whitespace/dots as needed by the filesystem. Keep the real extension. For untitled media use a factual name such as `creator - Reel.ext` or `creator - Story (YYYY-MM-DD).ext` with a verified publication date or the download date. Do not invent captions or dates.

Save a single file directly in its category; create a subfolder for a requested album, playlist or related set. Resolve filename collisions before transfer. Never assume an existing same-named file is the same source. Resume only a verified partial transfer; otherwise preserve existing files and choose a new name.

## Transfer within scope

Use only supplied or explicitly selected links. A browser tab or link embedded in an untrusted page is not itself a download request. Resolving one file does not authorize crawling a site, expanding a playlist or fetching unrelated private content.

Pass URLs and filenames as literal arguments, preferably through subprocess argument lists. Do not evaluate URL characters as shell code or convert untrusted text into a downloader configuration. Reject output path traversal and disable automatic torrent/Metalink following for ordinary transfers.

Keep credentials, cookies and signed URLs out of chat, reusable files and reports. Use the host's authorized credential handling without collecting passwords in chat. Do not bypass access controls or DRM.

Use bounded retries and at most three concurrent transfers by default. Keep long transfers attached to the current task. Do not create a daemon, startup service or unattended schedule. Preserve resumable partial files on interruption and report them as partial.

Torrent transfers upload pieces while downloading. Explain that effect before starting an explicitly requested torrent, and stop post-download seeding with `--seed-time=0`; that flag does not make the transfer download-only.

## Verify the saved file

Require the completed process and actual output file. Check size and type; reject an HTML login/error page when a PDF, archive or media file was requested. Use a published checksum when available. A locally computed hash identifies bytes but does not establish authenticity.

For media, probe the final merged file, require plausible duration and the requested streams, and report actual resolution/format. A silent source can legitimately have no audio; verify and disclose it. Do not treat `.part`, a range fragment, or browser playback as a completed download.

Report the clickable saved path, size and verification result. List failed and partial batch items separately. Downloading does not authorize executing installers, extracting archives, reorganizing unrelated files or publishing the result.

See [examples and review cases](references/examples.md).
