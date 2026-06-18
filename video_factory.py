#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AI Short Video Factory - 短视频批量生产流水线（对标 MoneyPrinterTurbo）。"""
import argparse, json, os, shutil, subprocess, wave, math
from pathlib import Path

HOOKS = ["夏天最怕闷汗？", "为什么男生都在换这条？", "3 秒看懂它凭什么火"]
SELLS = ["冰感面料接触凉感系数 Q-max 0.28", "无痕加宽腰头不勒不卷", "80% 锦纶+20% 氨纶高弹"]
CTAS = ["点击下方小黄车", "评论区扣 1 送尺码表", "拍 2 件立减 20"]

def gen_copy(topic, idx):
    return {"hook": HOOKS[idx % len(HOOKS)], "body": f"{topic}：" + "；".join(SELLS), "cta": CTAS[idx % len(CTAS)]}

def match_assets(topic, assets_dir):
    d = Path(assets_dir)
    if not d.exists():
        return ["assets/placeholder_1.mp4", "assets/placeholder_2.mp4"]
    return [str(f) for f in sorted(d.glob("*.mp4")) + sorted(d.glob("*.jpg"))][:6] or ["assets/placeholder_1.mp4"]

def tts_placeholder(text, out_wav):
    """无 edge-tts 时的静音占位（按时长 4 字/秒估算），保证时间轴正确。"""
    dur = max(2.0, len(text) / 4.0)
    with wave.open(str(out_wav), "w") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(16000)
        w.writeframes(b"\x00\x00" * int(16000 * dur))
    return dur

def make_srt(copy, total_dur, out_path):
    seg = [(copy["hook"], 0, total_dur * 0.25), (copy["body"], total_dur * 0.25, total_dur * 0.85), (copy["cta"], total_dur * 0.85, total_dur)]
    srt = ""
    for i, (text, s, e) in enumerate(seg, 1):
        srt += f"{i}\n{_ts(s)} --> {_ts(e)}\n{text}\n\n"
    Path(out_path).write_text(srt, encoding="utf-8")

def _ts(t):
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int(s % 1 * 1000):03d}"

def assemble(video_id, copy, assets, srt, out_dir, dry_run):
    out = Path(out_dir) / video_id
    out.mkdir(parents=True, exist_ok=True)
    if dry_run or not shutil.which("ffmpeg"):
        manifest = {"id": video_id, "copy": copy, "assets": assets, "srt": str(srt), "note": "dry-run/无 ffmpeg，仅输出装配清单"}
        (out / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        return str(out / "manifest.json")
    cmd = ["ffmpeg", "-y", "-i", assets[0], "-vf", "scale=1080:1920", "-i", str(srt)]
    final = out / "final.mp4"
    subprocess.run(cmd + ["-c:v", "libx264", str(final)], check=False)
    return str(final)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", required=True); ap.add_argument("--count", type=int, default=1)
    ap.add_argument("--assets", default="assets"); ap.add_argument("--out", default="outputs")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    assets = match_assets(args.topic, args.assets)
    for i in range(args.count):
        copy = gen_copy(args.topic, i)
        vid = f"{args.topic}_{i+1:02d}"
        wav = Path(args.out) / vid / "voice.wav"
        wav.parent.mkdir(parents=True, exist_ok=True)
        dur = tts_placeholder(copy["hook"] + copy["body"], wav)
        srt = Path(args.out) / vid / "sub.srt"
        make_srt(copy, dur, srt)
        result = assemble(vid, copy, assets, srt, args.out, args.dry_run)
        print(f"[{vid}] hook={copy['hook'][:18]}… 配音{dur:.1f}s -> {result}")

if __name__ == "__main__":
    main()
