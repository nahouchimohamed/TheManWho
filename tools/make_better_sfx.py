"""Richer procedural SFX for the demo."""
from __future__ import annotations

import math
import random
import struct
import wave
from pathlib import Path

SFX = Path(__file__).resolve().parents[1] / "assets" / "sfx"
RATE = 22050


def write_wav(path: Path, samples):
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        frames = b"".join(
            struct.pack("<h", max(-32767, min(32767, int(s * 32767)))) for s in samples
        )
        w.writeframes(frames)
    print("wrote", path.name)


def env(i, n, attack=0.02):
    a = min(1.0, i / max(1, int(RATE * attack)))
    r = 1.0 - i / n
    return a * r


def tone(freq, dur, vol=0.35, attack=0.01):
    n = int(RATE * dur)
    return [math.sin(2 * math.pi * freq * (i / RATE)) * vol * env(i, n, attack) for i in range(n)]


def noise(dur, vol=0.25):
    n = int(RATE * dur)
    return [(random.random() * 2 - 1) * vol * (1 - i / n) for i in range(n)]


def sweep(f0, f1, dur, vol=0.3):
    n = int(RATE * dur)
    out = []
    for i in range(n):
        t = i / n
        f = f0 + (f1 - f0) * t
        out.append(math.sin(2 * math.pi * f * (i / RATE)) * vol * (1 - t))
    return out


def mix(*tracks):
    length = max(len(t) for t in tracks)
    out = [0.0] * length
    for t in tracks:
        for i, v in enumerate(t):
            out[i] += v
    peak = max(0.001, max(abs(v) for v in out))
    return [max(-1.0, min(1.0, v / peak * 0.85)) for v in out]


def main():
    random.seed(7)
    write_wav(SFX / "swing.wav", mix(sweep(420, 140, 0.14, 0.22), noise(0.12, 0.18), tone(90, 0.08, 0.1)))
    write_wav(
        SFX / "parry.wav",
        mix(tone(1450, 0.05, 0.4), tone(2200, 0.04, 0.28), tone(900, 0.08, 0.15), noise(0.04, 0.12)),
    )
    write_wav(SFX / "hit.wav", mix(tone(70, 0.12, 0.45), tone(180, 0.08, 0.2), noise(0.09, 0.28)))
    write_wav(
        SFX / "deathblow.wav",
        mix(sweep(500, 80, 0.22, 0.3), tone(55, 0.3, 0.5), tone(220, 0.15, 0.22), noise(0.22, 0.32)),
    )
    write_wav(SFX / "jump.wav", mix(sweep(180, 360, 0.09, 0.2), tone(300, 0.06, 0.1)))
    write_wav(SFX / "telegraph.wav", mix(tone(160, 0.18, 0.18), tone(120, 0.22, 0.12), sweep(200, 90, 0.2, 0.1)))
    write_wav(SFX / "ally_death.wav", mix(tone(48, 0.35, 0.42), noise(0.28, 0.3), tone(90, 0.2, 0.15)))
    print("sfx done")


if __name__ == "__main__":
    main()
