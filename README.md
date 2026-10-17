# Download Anything: file, video and audio downloads for Codex

![Download Anything: a cobalt download arrow sends PDF, MP4, ZIP, JPG and MP3 parcels into a saved-files tray](skills/download-anything/assets/download-anything.jpg)

A link. A local file.

Download Anything is an open-source Codex skill that turns supported links into verified local files. It uses aria2 for direct transfers, yt-dlp for supported video and audio pages, and FFmpeg when media needs merging or conversion. Give it a link, a filename or a quality preference; it checks the actual output before reporting success.

[Download the latest release](https://github.com/Abaans/download-anything/releases/latest) · [Install in Codex](#install-in-codex) · [Transfer recipes](skills/download-anything/references/transfers.md)

## Try it

```text
Use $download-anything to save this video at 1080p with audio.
Use $download-anything to download this document as “Field guide.pdf”.
Use $download-anything to extract the audio from this link as MP3.
Use $download-anything to resume this verified partial transfer.
```

## What it handles

| Request | Tools / conditions |
|---|---|
| Direct files over HTTP(S), FTP or SFTP | aria2c |
| Supported video/audio pages | yt-dlp, ffmpeg and ffprobe as needed |
| Cloud shares and document viewers | An authorized browser/connector capable of obtaining the file |
| Authenticated media | Scoped source access and a supported extraction route |
| Torrent, magnet or Metalink | Explicit protocol request and bounded file selection |

The name is broad; support depends on the source and tools. This skill does not bypass DRM or access controls, recover expired content, guarantee every website or turn browser playback into proof of a download. Torrents upload data during transfer, including when post-download seeding is disabled.

## Install in Codex

Download the [release ZIP](https://github.com/Abaans/download-anything/releases/latest) and extract it, or clone `https://github.com/Abaans/download-anything.git`. From that folder, run this copy-only installation:

```sh
python3 - <<'PYCODE'
import os
import shutil
from pathlib import Path

source = Path("skills/download-anything")
codex_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex"))).expanduser()
destination = codex_home / "skills" / "download-anything"
if not (source / "SKILL.md").is_file():
    raise SystemExit("Run from the extracted repository root.")
if destination.exists() or destination.is_symlink():
    raise SystemExit("An installation already exists; review and back it up before replacing it.")
destination.parent.mkdir(parents=True, exist_ok=True)
shutil.copytree(source, destination)
print(destination)
PYCODE
```

Refresh skill discovery or start a new chat. Invoke `$download-anything` with the link and any filename, destination, format or quality preferences. If you have an older `$download` skill, review which version you want active; this installation does not delete or replace it automatically.

To update, preserve any local edits before replacing this exact folder. To uninstall, remove only the installed `download-anything` folder.

## Requirements

Install only the tools required by your request, using their official instructions:

- [aria2](https://github.com/aria2/aria2) for direct transfers.
- [yt-dlp](https://github.com/yt-dlp/yt-dlp#installation) for supported media pages and current extractor/runtime requirements.
- [FFmpeg and ffprobe](https://ffmpeg.org/download.html) for media merging, conversion and verification.

The skill checks the current host rather than assuming a particular installation. Browser-based routes require capabilities supplied by your agent. Commands may need the host's appropriate shell or literal subprocess arguments.

## Output behavior

Explicit names and destinations win. Defaults use source titles and shallow folders in the user's Downloads directory. Existing files are preserved; partial transfers are reported as partial. Completion means the real file was checked for size/type and, for media, duration and streams.

See the [skill](skills/download-anything/SKILL.md), [transfer recipes](skills/download-anything/references/transfers.md) and [examples](skills/download-anything/references/examples.md).

## Verification and development

Use Python 3.10+ in an isolated environment with [development requirements](requirements-dev.txt). After creating and activating that environment, install them with `python3 -m pip install -r requirements-dev.txt`:

```sh
python3 -m unittest discover -s tests -v
python3 tools/validate.py
python3 tests/smoke_download.py
```

The smoke test uses synthetic files and a temporary loopback HTTP server. It checks a direct transfer, existing-file protection, a missing source, an interrupted/resumed transfer, and a generated video through yt-dlp. It requires aria2c, yt-dlp, ffmpeg and ffprobe. It does not contact public media sites or user accounts. See [verification](docs/VERIFICATION.md) for the distinction between tested transport behavior and untested site/account workflows.

## Questions

### Can it download any website?

Support depends on the source, access and installed tools. Expired links, DRM and unsupported extractors can block a transfer. The skill reports that limit instead of treating a partial or login page as the requested file.

### Is this a standalone downloader app?

It is an agent skill. Codex reads the workflow and uses your available tools. aria2, yt-dlp and FFmpeg remain separate projects with their own installation requirements.

### Will it overwrite my files?

The workflow checks filename collisions and preserves existing files. It resumes a partial transfer only after confirming the source and partial-file identity. The local smoke test checks both collision protection and interruption/resume.

### Can it download videos with audio?

For a supported source, it selects the requested video/audio streams and checks the saved result with ffprobe. You get the actual resolution and stream information; it cannot add audio or detail absent from the source.

### Does it work with private links?

Protected sources need authorized account access and a supported download route. The skill does not bundle credentials or bypass access controls. Those account workflows have not been exercised by the local test suite.

## For agents and maintainers

Use [skills.json](skills.json) for the package's name, path, requirements and documentation links, or [llms.txt](llms.txt) for a short text index. The [SKILL.md](skills/download-anything/SKILL.md) defines the workflow.

For brand design and shared-document workflows, see [Abaan's Agent Skills](https://github.com/Abaans/abaans-agent-skills). Report reproducible download problems through [GitHub Issues](https://github.com/Abaans/download-anything/issues); redact private URLs and credentials.

## License

[MIT](LICENSE). Maintained by Abaan. External tools and downloaded content retain their own terms; see [attribution](ATTRIBUTION.md).
