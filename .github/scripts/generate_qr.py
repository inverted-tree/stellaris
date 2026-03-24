#!/usr/bin/env python3
"""Generate QR code SVGs for all Hugo posts."""

import sys
import shutil
from pathlib import Path

import qrcode
import qrcode.image.svg


def get_posts(content_dir):
    """Yield url_path strings for all non-index markdown files."""
    for md in sorted(content_dir.rglob("*.md")):
        if md.name == "_index.md":
            continue
        rel = md.relative_to(content_dir)
        if md.stem == "index":
            # page bundle: content/posts/foo/index.md → posts/foo
            yield str(rel.parent)
        else:
            yield str(rel.with_suffix(""))  # e.g. posts/post-1


def generate_qr(url, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    qr = qrcode.QRCode(image_factory=qrcode.image.svg.SvgPathImage, box_size=10)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image()
    img.save(str(output_path))
    # Post-process: grey fill, transparent background
    svg = output_path.read_text()
    svg = svg.replace('fill="#000000"', 'fill="#888888"')
    output_path.write_text(svg)


def main():
    base_url = sys.argv[1].rstrip("/")
    repo_root = Path(__file__).resolve().parent.parent.parent
    content_dir = repo_root / "content"
    static_qr_dir = repo_root / "static" / "qr"
    shutil.rmtree(static_qr_dir, ignore_errors=True)

    for url_path in get_posts(content_dir):
        post_url = f"{base_url}/{url_path}/"
        out_path = static_qr_dir / f"{url_path}.svg"
        generate_qr(post_url, out_path)
        print(f"  {out_path.relative_to(repo_root)} → {post_url}")


if __name__ == "__main__":
    main()
