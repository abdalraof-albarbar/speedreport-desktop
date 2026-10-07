"""Writes config.public.json from the source repo's config.json, minus personal details."""
import json
import sys
from pathlib import Path

src = Path(sys.argv[1] if len(sys.argv) > 1 else "app/config.json")
cfg = json.loads(src.read_text(encoding="utf-8"))
cfg.update({"engineer_name": "", "email_sender": "", "download_url": "", "backup": {"enabled": False}})
Path("config.public.json").write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")
print("config.public.json written; engineer_name and email_sender are blank")
