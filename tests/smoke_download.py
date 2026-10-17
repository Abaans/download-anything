"""Bounded local transport checks. No user files, accounts or public sources."""
import hashlib
import http.server
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import threading
import time
from urllib.parse import urlsplit


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def run(args, timeout=30):
    return subprocess.run(args, capture_output=True, text=True, timeout=timeout)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    names = ["aria2c", "yt-dlp", "ffmpeg", "ffprobe"]
    executables = {name: shutil.which(name) for name in names}
    missing = [name for name, path in executables.items() if path is None]
    if missing:
        raise SystemExit("Missing required tools: " + ", ".join(missing))
    versions = {}
    for name, executable in executables.items():
        flag = "-version" if name.startswith("ff") else "--version"
        result = run([executable, flag])
        require(result.returncode == 0, f"Cannot read {name} version")
        versions[name] = result.stdout.splitlines()[0]

    with tempfile.TemporaryDirectory(prefix="download smoke ") as directory:
        root = Path(directory)
        output = root / "saved files"
        output.mkdir()
        payload = bytes(range(256)) * 4096
        large_payload = bytes(range(256)) * 65536
        source = root / "sample.mp4"
        generated = run([executables["ffmpeg"], "-v", "error", "-nostdin", "-f", "lavfi", "-i", "color=c=blue:s=160x90:r=12", "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=44100", "-t", "1", "-c:v", "mpeg4", "-c:a", "aac", str(source)])
        require(generated.returncode == 0, generated.stderr)
        routes = {"/file.bin": payload, "/large.bin": large_payload, "/sample.mp4": source.read_bytes()}
        requests = []

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *_args):
                pass

            def do_HEAD(self):
                self.serve(False)

            def do_GET(self):
                self.serve(True)

            def serve(self, include_body):
                path = urlsplit(self.path).path
                data = routes.get(path)
                if data is None:
                    self.send_error(404)
                    return
                start, end = 0, len(data) - 1
                requested = self.headers.get("Range")
                if requested:
                    try:
                        low, high = requested.removeprefix("bytes=").split("-", 1)
                        start, end = int(low), int(high) if high else end
                        if not 0 <= start <= end < len(data):
                            raise ValueError("Invalid range")
                    except ValueError:
                        self.send_error(416)
                        return
                requests.append((path, requested, start))
                self.send_response(206 if requested else 200)
                self.send_header("Content-Type", "video/mp4" if path.endswith("mp4") else "application/octet-stream")
                self.send_header("Content-Length", str(end - start + 1))
                self.send_header("Accept-Ranges", "bytes")
                self.send_header("ETag", '"synthetic-v1"')
                if requested:
                    self.send_header("Content-Range", f"bytes {start}-{end}/{len(data)}")
                self.end_headers()
                if not include_body:
                    return
                try:
                    for index in range(start, end + 1, 65536):
                        self.wfile.write(data[index:min(index + 65536, end + 1)])
                        self.wfile.flush()
                        if path == "/large.bin":
                            time.sleep(0.01)
                except (BrokenPipeError, ConnectionResetError):
                    pass

        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        server.daemon_threads = True
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        address = f"http://127.0.0.1:{server.server_port}"
        process = None
        try:
            def aria(filename, route, resume=False, single=False):
                return [executables["aria2c"], "--no-conf=true", "--no-netrc=true", f"--continue={str(resume).lower()}", "--allow-overwrite=false", "--auto-file-renaming=false", f"--max-connection-per-server={1 if single else 4}", f"--split={1 if single else 4}", "--min-split-size=5M", "--max-tries=3", "--retry-wait=5", "--connect-timeout=20", "--timeout=60", "--check-certificate=true", "--file-allocation=none", "--follow-torrent=false", "--follow-metalink=false", f"--dir={output}", f"--out={filename}", "--", address + route]

            filename = "Field guide $sample.bin"
            direct = run(aria(filename, "/file.bin"))
            require(direct.returncode == 0, direct.stderr + direct.stdout)
            require((output / filename).read_bytes() == payload, "Direct transfer bytes differ")
            print("PASS: direct transfer and literal filename")

            collision = output / "existing.bin"
            collision.write_bytes(b"preserve existing file")
            refused = run(aria(collision.name, "/file.bin"))
            require(refused.returncode != 0, "Collision should fail")
            require(collision.read_bytes() == b"preserve existing file", "Existing file changed")
            print("PASS: existing-file protection")

            absent = run(aria("missing.bin", "/missing.bin"))
            require(absent.returncode != 0, "404 should fail")
            require(not (output / "missing.bin").exists() or (output / "missing.bin").stat().st_size == 0, "404 produced a misleading file")
            print("PASS: missing source fails")

            process = subprocess.Popen(aria("resumed.bin", "/large.bin", single=True), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(0.8)
            require(process.poll() is None, "Transfer did not remain interruptible")
            process.send_signal(signal.SIGINT)
            process.wait(timeout=10)
            partial = output / "resumed.bin"
            require(partial.is_file() and (output / "resumed.bin.aria2").is_file(), "No resumable partial/control file")
            require(0 < partial.stat().st_size < len(large_payload), "Partial size invalid")
            checkpoint = len(requests)
            resumed = run(aria(partial.name, "/large.bin", resume=True, single=True))
            require(resumed.returncode == 0, resumed.stdout + resumed.stderr)
            require(partial.read_bytes() == large_payload, "Resumed bytes differ")
            require(any(path == "/large.bin" and start > 0 for path, _range, start in requests[checkpoint:]), "No positive-offset range used during resume")
            require(not (output / "resumed.bin.aria2").exists(), "Completed transfer still has control file")
            print("PASS: interrupted transfer resumes to exact bytes")

            media = run([executables["yt-dlp"], "--ignore-config", "--no-cache-dir", "--no-playlist", "--continue", "--no-overwrites", "--retries", "3", "--fragment-retries", "3", "--socket-timeout", "30", "-f", "bv*+ba/b", "--merge-output-format", "mkv", "--downloader", "http,https:aria2c", "--downloader-args", "aria2c:--no-conf=true --no-netrc=true -x4 -s4 --max-tries=3 --retry-wait=5", "-P", str(output), "-o", "Synthetic video.%(ext)s", "--print", "after_move:filepath", "--", address + "/sample.mp4"])
            require(media.returncode == 0, media.stdout + media.stderr)
            video = output / "Synthetic video.mp4"
            require(video.is_file() and digest(video) == digest(source), "Saved video differs")
            probe = run([executables["ffprobe"], "-v", "error", "-show_entries", "format=duration,size:stream=codec_type,codec_name,width,height", "-of", "json", str(video)])
            require(probe.returncode == 0, probe.stderr)
            info = json.loads(probe.stdout)
            require(float(info["format"]["duration"]) > 0, "Invalid duration")
            require({"video", "audio"} <= {stream["codec_type"] for stream in info["streams"]}, "Missing media streams")
            require(any(stream.get("width") == 160 and stream.get("height") == 90 for stream in info["streams"]), "Wrong video size")
            print("PASS: yt-dlp/aria2 video has exact bytes, duration, dimensions and audio")
            print(json.dumps({"versions": versions, "checks": 5, "status": "passed"}, indent=2))
        finally:
            if process is not None and process.poll() is None:
                process.kill()
                process.wait(timeout=5)
            server.shutdown()
            server.server_close()
            worker.join(timeout=5)


if __name__ == "__main__":
    main()
