"""A quiet piano bed: single soft notes about once a second on a slow
Am-F-C-G progression, short decays, a low-pass near 2 kHz and a little reverb.
Sustained synth pads were painful to listen to, so this stays sparse."""
import numpy as np


def piano_bed(seconds: float, sr: int = 48000, seed: int = 3) -> np.ndarray:
    n = int(sr * seconds)
    out = np.zeros((n, 2))
    rng = np.random.default_rng(seed)

    def hz(m):
        return 440 * 2 ** ((m - 69) / 12)

    def note(m, t0, vel, length, pan):
        f = hz(m)
        L = int(length * sr)
        tt = np.arange(L) / sr
        env = (1 - np.exp(-tt / 0.006)) * np.exp(-tt / (1.6 if m > 60 else 2.4))
        sig = sum(a * np.sin(2 * np.pi * f * k * (1 + 0.0004 * k * k) * tt) * np.exp(-tt * k * 0.35)
                  for k, a in ((1, 1.0), (2, 0.32), (3, 0.12), (4, 0.05)))
        sig = sig * env * vel
        s0 = int(t0 * sr)
        s1 = min(n, s0 + L)
        if s1 > s0:
            out[s0:s1, 0] += sig[: s1 - s0] * (1 - pan) * 1.2
            out[s0:s1, 1] += sig[: s1 - s0] * pan * 1.2

    chords = [[57, 64, 69, 72], [53, 60, 65, 69], [48, 55, 60, 64], [55, 62, 67, 71]]
    bass = [45, 41, 48, 43]
    t, i = 1.0, 0
    while t < seconds - 4:
        c, b = chords[(i // 4) % 4], bass[(i // 4) % 4]
        if i % 4 == 0:
            note(b, t, 0.35, 5.0, 0.45)
        note(c[i % 4], t + 0.02, 0.22 + 0.04 * rng.random(), 4.0, 0.35 + 0.3 * rng.random())
        t += 1.0
        i += 1

    N = 1 << int(np.ceil(np.log2(n)))
    freqs = np.fft.rfftfreq(N, 1 / sr)
    lp = 1 / (1 + (freqs / 2000) ** 4)
    dry = np.stack([np.fft.irfft(np.fft.rfft(out[:, c], N) * lp, N)[:n] for c in range(2)], 1)
    ir_len = int(sr * 2.5)
    ir = rng.normal(0, 1, (ir_len, 2)) * np.exp(-np.arange(ir_len) / (sr * 0.7))[:, None]
    ir[0] = 0
    wet = np.stack([np.fft.irfft(np.fft.rfft(dry[:, c], N) * np.fft.rfft(ir[:, c], N) * lp, N)[:n] for c in range(2)], 1)
    mix = dry + 0.35 * wet / np.max(np.abs(wet)) * np.max(np.abs(dry))
    mix = mix / np.max(np.abs(mix)) * 0.5
    fade = int(sr * 2)
    mix[:fade] *= np.linspace(0, 1, fade)[:, None]
    return mix.astype(np.float32)
