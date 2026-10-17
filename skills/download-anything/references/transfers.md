# Transfer recipes

Use literal argument lists when executing commands programmatically. The shell examples below are shapes to fill with validated values; their quoting is not permission to interpolate untrusted shell text. Resolve dependencies with the host's executable-discovery mechanism (`command -v` in a POSIX shell, `Get-Command` in PowerShell).

## Fresh direct transfer

Check the destination does not already exist. For a normal direct file:

```sh
aria2c --no-conf=true --no-netrc=true \
  --continue=false --allow-overwrite=false --auto-file-renaming=false \
  --max-connection-per-server=4 --split=4 --min-split-size=5M \
  --max-tries=3 --retry-wait=5 --connect-timeout=20 --timeout=60 \
  --check-certificate=true --file-allocation=none \
  --follow-torrent=false --follow-metalink=false \
  --dir='DESTINATION_DIRECTORY' --out='SAFE_FILENAME' -- 'SOURCE_URL'
```

Keep `--out` to a basename. Destination paths belong in `--dir`. A nonzero exit, unexpected content type or incomplete file needs investigation, not a success message.

For a resumed transfer, establish that source identity and remote content still match the exact partial file and its aria2 control metadata, then use `--continue=true`. An identical filename is insufficient. If identity or server resume support cannot be established, preserve the partial and restart to a distinct destination. Do not delete the existing file to make a command pass.

`--no-conf` and `--no-netrc` keep ambient settings from silently changing a transfer. A deliberately authorized protected credential configuration is a separate mode; never print it. See [authenticated sources](authenticated-sources.md).

## Video and audio pages

Inspect only the metadata needed to choose the output: title, duration, live status and available formats. Do not dump full metadata or signed stream URLs. Clarify duration before an open-ended live recording. Default to one video with audio; a music-video link does not imply audio-only extraction.

```sh
yt-dlp --ignore-config --no-playlist --continue --no-overwrites \
  --retries 3 --fragment-retries 3 --socket-timeout 30 \
  -f 'bv*+ba/b' --merge-output-format mkv \
  --downloader 'http,https:aria2c' \
  --downloader-args 'aria2c:--no-conf=true --no-netrc=true -x4 -s4 --max-tries=3 --retry-wait=5' \
  -P 'DESTINATION_DIRECTORY' -o '%(title).180B.%(ext)s' \
  --print after_move:filepath -- 'SOURCE_URL'
```

Inspect collisions before using a title-based output template. `--no-overwrites` can skip an existing file successfully; a zero exit alone does not prove that file belongs to this request. For explicit names, escape literal percent signs in the template and retain the extension placeholder. Do not attach signed source URLs to durable output.

- **Best streams:** MKV can preserve available codecs without conversion.
- **Requested MP4:** select compatible streams with `-f 'bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]' --merge-output-format mp4`. If absent, explain conversion tradeoffs. Renaming an extension is not conversion.
- **Audio only:** use `-f ba -x`; specify an output codec only when requested. For MP3 use `--audio-format mp3 --audio-quality 0`. Transcoding cannot restore lost source quality.
- **Requested size:** constrain format selection and report the actual result; do not claim upscaling created source detail.
- **Subtitles:** list available languages, select those requested and distinguish automatic captions.
- **Playlists:** expand only when requested; bound the selection when scope is ambiguous.

The external-downloader selector above applies aria2 to HTTP(S); let yt-dlp handle segmented HLS/DASH through its native path. If aria2 fails for a transport reason, try yt-dlp's native downloader once. On extraction or access failure, inspect the version and official guidance; do not repeatedly switch clients or harvest cookies to bypass a challenge.

## Media verification

```sh
ffprobe -v error \
  -show_entries format=duration,size:stream=codec_type,codec_name,width,height \
  -of json 'SAVED_FILE'
```

Require nonzero plausible duration, the requested streams and an actual final file. For a normal video-with-audio request, verify both streams. Compare a local frame against the selected source when browser extraction or ambiguous assets were involved. Report absent source audio explicitly.

## Torrent and Metalink modes

Use only when explicitly requested. Inspect listed files before choosing a subset. Prevent destinations from escaping the selected folder. Torrent traffic includes uploads during transfer even with `--seed-time=0`; do not promise download-only behavior. Provider-specific or unusual protocol options need current official documentation before use.

## Sources and dependencies

- [aria2 manual](https://aria2.github.io/manual/en/html/aria2c.html)
- [yt-dlp documentation and dependencies](https://github.com/yt-dlp/yt-dlp#readme)
- [FFmpeg tools](https://ffmpeg.org/documentation.html)

JavaScript runtime and extractor requirements can change with yt-dlp and the selected site. Check the installed version and current project guidance instead of hard-coding one host's setup.
