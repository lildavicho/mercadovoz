from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from scripts.deployment.rotate_pilot_credentials import rotate


class SecureRotationTests(unittest.TestCase):
    def test_rotation_preserves_nonsecret_configuration_and_writes_private_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            env_path = root / "api.env"
            operator_path = root / "operator" / "p01-r2-access.json"
            env_path.write_text(
                "MERCADOVOZ_DB=/private/pilot.db\n"
                "MERCADOVOZ_PILOT_ACCESS_CODES={\"P01\":\"old\"}\n"
                "MERCADOVOZ_OPERATOR_TOKEN=old-token\n",
                encoding="utf-8",
            )

            result = rotate(
                env_path,
                operator_path,
                origin="https://pilot.example.test",
                round_id="P01_R2",
            )

            content = env_path.read_text(encoding="utf-8")
            record = json.loads(operator_path.read_text(encoding="utf-8"))
            self.assertIn("MERCADOVOZ_DB=/private/pilot.db", content)
            self.assertIn("MERCADOVOZ_PILOT_ROUND_ID=P01_R2", content)
            self.assertIn("MERCADOVOZ_ALLOWED_ORIGINS=https://pilot.example.test", content)
            self.assertNotIn("old-token", content)
            self.assertNotIn("old\"", content)
            self.assertEqual("P01", record["participant_id"])
            self.assertGreaterEqual(len(record["access_code"]), 32)
            self.assertEqual("false", result["secret_values_printed"])
            if os.name != "nt":
                self.assertEqual(0o600, env_path.stat().st_mode & 0o777)
                self.assertEqual(0o600, operator_path.stat().st_mode & 0o777)

    def test_rotation_rejects_insecure_origin_and_invalid_round(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(ValueError):
                rotate(root / "env", root / "code", origin="http://example.test", round_id="P01_R2")
            with self.assertRaises(ValueError):
                rotate(root / "env", root / "code", origin="https://example.test", round_id="round-two")


if __name__ == "__main__":
    unittest.main()
