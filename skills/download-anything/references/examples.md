# Examples and review cases

## Direct file

“Download this public file as Field guide.pdf into my chosen folder.”

Use the exact requested name and location, check for collisions, transfer and inspect the file. An HTML sign-in response saved with a PDF extension is a failure, not a PDF.

## Video and audio

“Save this supported video at up to 1080p with audio.”

Inspect metadata, choose a matching format, save the final merged file and probe both streams. Report the actual dimensions rather than promising the requested maximum exists.

“Save only the audio as MP3.”

Select/extract audio, convert only as requested and verify the resulting audio stream and duration. Do not claim the conversion improves source quality.

## Interrupted transfer

“Resume this partial transfer.”

Confirm the source and partial-file identity before enabling resume. An unrelated same-named file must remain untouched. Preserve partial files if identity is uncertain.

## Reviewer checks

- A URL containing spaces, dollar signs or shell metacharacters is passed as literal data.
- A requested name containing `../` is rejected or clarified rather than used as a path.
- A playlist link without a playlist request remains a single-item request.
- A login challenge leads to a scoped access decision, not bulk cookie export.
- A transfer process starts but a `.part` remains: report in progress or partial.
- A source image/story is genuinely silent: report no source audio after verification.
- Torrent seeding disabled after completion still does not mean zero uploads during transfer.
