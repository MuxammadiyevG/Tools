#!/usr/bin/env python3
"""
YouTube → MP3 yuklovchi CLI dastur
Ishlatish: python3 yt_mp3.py <YouTube_URL> [variantlar]
"""

import argparse
import sys
from pathlib import Path

try:
    import yt_dlp
except ImportError:
    print("❌ yt-dlp topilmadi. O'rnatish uchun: pip install yt-dlp")
    sys.exit(1)


def progress_hook(d):
    if d["status"] == "downloading":
        percent = d.get("_percent_str", "?%").strip()
        speed   = d.get("_speed_str", "?").strip()
        eta     = d.get("_eta_str", "?").strip()
        print(f"\r⏬ Yuklanmoqda: {percent}  Tezlik: {speed}  Qoldi: {eta}   ", end="", flush=True)
    elif d["status"] == "finished":
        print(f"\n✅ Yuklab olindi: {d['filename']}")
        print("🔄 MP3 ga o'tkazilmoqda...")
    elif d["status"] == "error":
        print(f"\n❌ Xato yuz berdi!")


def download_mp3(url: str, output_dir: str, filename=None):
    output_dir = Path(output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if filename:
        outtmpl = str(output_dir / f"{filename}.%(ext)s")
    else:
        outtmpl = str(output_dir / "%(title)s.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": outtmpl,
        "progress_hooks": [progress_hook],
        "quiet": False,
        "no_warnings": False,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            },
            {
                "key": "FFmpegMetadata",
                "add_metadata": True,
            },
        ],
    }

    print(f"\n🎵 YouTube MP3 Yuklovchi")
    print(f"{'─' * 40}")
    print(f"🔗 URL    : {url}")
    print(f"📁 Papka  : {output_dir}")
    print(f"🎚  Sifat : 320 kbps (maksimal)")
    print(f"{'─' * 40}\n")

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            print(f"🎬 Video  : {info.get('title', 'Noma\'lum')}")
            print(f"👤 Kanal  : {info.get('uploader', 'Noma\'lum')}")
            duration = info.get("duration", 0)
            print(f"⏱  Davom  : {duration // 60}:{duration % 60:02d}\n")
            ydl.download([url])

        print(f"\n✅ Tayyor! MP3 fayl '{output_dir}' papkasiga saqlandi.")
    except yt_dlp.utils.DownloadError as e:
        print(f"\n❌ Yuklab olishda xato: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Foydalanuvchi tomonidan to'xtatildi.")
        sys.exit(0)


def main():
    parser = argparse.ArgumentParser(
        prog="yt_mp3",
        description="🎵 YouTube videolarini MP3 formatida yuklab oluvchi dastur",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Misollar:
  python3 yt_mp3.py https://youtu.be/dQw4w9WgXcQ
  python3 yt_mp3.py https://youtu.be/dQw4w9WgXcQ -o ~/Musiqa
  python3 yt_mp3.py https://youtu.be/dQw4w9WgXcQ -n "qoshiq_nomi"
        """,
    )

    parser.add_argument("url", help="YouTube video yoki playlist URL manzili")
    parser.add_argument(
        "-o", "--output",
        default="./yuklamalar",
        metavar="PAPKA",
        help="Saqlash papkasi (standart: ./yuklamalar)",
    )
    parser.add_argument(
        "-n", "--name",
        default=None,
        metavar="FAYL_NOMI",
        help="Maxsus fayl nomi (.mp3 kengaytmasisiz)",
    )

    args = parser.parse_args()

    if not ("youtube.com" in args.url or "youtu.be" in args.url):
        print("⚠️  Ogohlantirish: URL YouTube manzili emas, baribir urinib ko'riladi...")

    download_mp3(url=args.url, output_dir=args.output, filename=args.name)


if __name__ == "__main__":
    main()
