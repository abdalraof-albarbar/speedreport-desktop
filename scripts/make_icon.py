"""Builds the .exe icon (app.ico) from the logo in the source checkout."""
import sys
from pathlib import Path

from PIL import Image

src = Path(sys.argv[1] if len(sys.argv) > 1 else "app/speedreport/web/static/akakus-logo.png")
img = Image.open(src).convert("RGBA")
side = max(img.size)
canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
canvas.paste(img, ((side - img.width) // 2, (side - img.height) // 2), img)
canvas.save("app.ico", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print("app.ico written")
