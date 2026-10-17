"""Exercise installed-package boundaries and the exact README copy recipe."""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from validate import validate_repository, validate_skill


class PackagingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="skill review ")
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name)
        self.skills = sorted((ROOT / "skills").iterdir())

    def copy_skill(self):
        destination = self.workspace / self.skills[0].name
        shutil.copytree(self.skills[0], destination)
        return destination

    def test_repository(self):
        self.assertEqual(validate_repository(ROOT), [])

    def test_every_skill_survives_an_isolated_install(self):
        for source in self.skills:
            with self.subTest(skill=source.name):
                target = self.workspace / "isolated install" / source.name
                shutil.copytree(source, target)
                self.assertEqual(validate_skill(target), [])

    def test_missing_reference_is_rejected(self):
        target = self.copy_skill()
        with (target / "SKILL.md").open("a") as handle:
            handle.write("\n[Missing reference](references/not-bundled.md)\n")
        self.assertTrue(any("missing resource" in e for e in validate_skill(target)))

    def test_external_local_reference_is_rejected(self):
        target = self.copy_skill()
        (self.workspace / "outside.md").write_text("private fixture")
        with (target / "SKILL.md").open("a") as handle:
            handle.write("\n[Outside](../outside.md)\n")
        self.assertTrue(any("escapes package" in e for e in validate_skill(target)))

    def test_symlink_resource_is_rejected(self):
        target = self.copy_skill()
        (target / "linked").symlink_to(self.workspace / "outside")
        self.assertTrue(any("symlinks" in e for e in validate_skill(target)))

    def test_broken_metadata_is_rejected(self):
        target = self.copy_skill()
        (target / "agents/openai.yaml").write_text("interface: [")
        self.assertTrue(any("invalid agent metadata" in e for e in validate_skill(target)))

    def test_readme_installs_and_refuses_to_replace_existing_skill(self):
        readme = (ROOT / "README.md").read_text()
        script = re.search(r"python3 - <<'PYCODE'\n(.*?)\nPYCODE", readme, re.S).group(1)
        destination = self.workspace / "custom codex home"
        environment = dict(os.environ, CODEX_HOME=str(destination), PYTHONDONTWRITEBYTECODE="1")
        first = subprocess.run([sys.executable, "-c", script], cwd=ROOT, env=environment, capture_output=True, text=True, timeout=10)
        self.assertEqual(first.returncode, 0, first.stderr)
        installed = list((destination / "skills").iterdir())
        self.assertEqual(len(installed), 1)
        self.assertEqual(validate_skill(installed[0]), [])
        marker = installed[0] / "local-note.txt"
        marker.write_text("preserve this local edit")
        second = subprocess.run([sys.executable, "-c", script], cwd=ROOT, env=environment, capture_output=True, text=True, timeout=10)
        self.assertNotEqual(second.returncode, 0)
        self.assertIn("already exists", second.stderr)
        self.assertEqual(marker.read_text(), "preserve this local edit")


if __name__ == "__main__":
    unittest.main()
