"""Generate a contact sheet for a directory of sprites.

Usage: python sprite_contact_sheet.py <dir> [output.png] [--cols N] [--thumb N] [--filter prefix1,prefix2]

If output is omitted, defaults to c:/tmp/contact_sheet.png
"""
import sys, os, glob, argparse
from PIL import Image, ImageDraw, ImageFont


def make_contact_sheet(src_dir, out_path, cols=6, thumb_size=140, filter_prefixes=None):
    """Generate a contact sheet from all PNGs in src_dir."""
    files = sorted(glob.glob(os.path.join(src_dir, "*.png")))
    if filter_prefixes:
        prefixes = [p.strip() for p in filter_prefixes.split(",")]
        files = [f for f in files if any(os.path.basename(f).startswith(p) for p in prefixes)]

    if not files:
        print("No files found.")
        return None

    print(f"Processing {len(files)} sprites...")

    label_h = 18
    cell_w = thumb_size + 10
    cell_h = thumb_size + label_h + 10
    rows = (len(files) + cols - 1) // cols
    canvas_w = cols * cell_w + 10
    canvas_h = rows * cell_h + 10

    canvas = Image.new("RGBA", (canvas_w, canvas_h), (40, 40, 40, 255))
    draw = ImageDraw.Draw(canvas)

    try:
        font = ImageFont.truetype("arial.ttf", 11)
    except Exception:
        font = ImageFont.load_default()

    for i, fpath in enumerate(files):
        col = i % cols
        row = i // cols
        x = col * cell_w + 5
        y = row * cell_h + 5

        # Checkerboard background for transparency visibility
        checker_size = 8
        for cy in range(thumb_size // checker_size):
            for cx in range(thumb_size // checker_size):
                color = (60, 60, 60) if (cx + cy) % 2 == 0 else (80, 80, 80)
                draw.rectangle([
                    x + 5 + cx * checker_size, y + cy * checker_size,
                    x + 5 + (cx + 1) * checker_size, y + (cy + 1) * checker_size
                ], fill=color)

        # Load and resize sprite
        try:
            img = Image.open(fpath).convert("RGBA")
            img.thumbnail((thumb_size - 10, thumb_size), Image.LANCZOS)
            paste_x = x + 5 + (thumb_size - 10 - img.width) // 2
            paste_y = y + (thumb_size - img.height) // 2
            canvas.paste(img, (paste_x, paste_y), img)
        except Exception:
            draw.text((x + 5, y + thumb_size // 2), "ERR", fill="red", font=font)

        # Label
        name = os.path.basename(fpath).replace(".png", "")
        if len(name) > 18:
            name = name[:17] + "…"
        draw.text((x + 3, y + thumb_size + 2), name, fill=(200, 200, 200), font=font)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    canvas.save(out_path)
    print(f"Saved: {out_path} ({canvas_w}x{canvas_h}, {len(files)} sprites)")
    return out_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate sprite contact sheet")
    parser.add_argument("dir", help="Source directory containing PNGs")
    parser.add_argument("output", nargs="?", default="c:/tmp/contact_sheet.png",
                        help="Output image path (default: c:/tmp/contact_sheet.png)")
    parser.add_argument("--cols", type=int, default=6, help="Columns (default: 6)")
    parser.add_argument("--thumb", type=int, default=140, help="Thumbnail size (default: 140)")
    parser.add_argument("--filter", dest="filter_prefixes",
                        help="Comma-separated filename prefixes to include")
    args = parser.parse_args()
    make_contact_sheet(args.dir, args.output, args.cols, args.thumb, args.filter_prefixes)
