"""Self-attention in under a minute: a 3Blue1Brown-style Manim scene.

Each block below is one row of explainer-scenes.md. The block waits for the
start time of its sentence (from timings.json, which narrate.py writes), so
each visual lands on the words that name it.

Render: TIMINGS=/path/to/timings.json manim -qh scene.py SelfAttention
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path

import numpy as np
from manim import *

# ---------------------------------------------------------------- look
BG = "#0E0F12"
INK = "#ECECEC"
DIM = "#8A8F98"
ACCENT = "#F7D96F"   # bank: its query and its new vector (the thing explained)
OTHER = "#58C4DD"    # keys and values of the words (contrast)

config.background_color = BG

TEX = TexTemplate()
TEX.add_to_preamble(r"\usepackage{xcolor}")

# ---------------------------------------------------------------- toy numbers
# Two-dimensional toy vectors, so that the dot product is visible as alignment.
WORDS = ["the", "muddy", "river", "bank"]
Q_BANK = np.array([1.4, 0.7])
KEYS = {"the": (-0.5, 1.0), "muddy": (1.2, -0.4), "river": (2.2, 1.4), "bank": (0.3, 1.8)}
VALUES = {"the": (-0.8, 0.6), "muddy": (0.6, -1.0), "river": (2.0, 1.5), "bank": (-0.8, 1.2)}
OTHER_QUERIES = {"the": (1.0, -0.9), "muddy": (-1.0, 0.7), "river": (0.5, 1.5)}
D_K = 2

RAW = [round(float(Q_BANK @ np.array(KEYS[w])), 9) + 0.0 for w in WORDS]
SCALED = [r / math.sqrt(D_K) for r in RAW]
_e = [math.exp(s) for s in SCALED]
WEIGHTS = [x / sum(_e) for x in _e]
W_SHOWN = [round(w, 2) for w in WEIGHTS]
assert abs(sum(W_SHOWN) - 1.0) < 1e-9, W_SHOWN
Z = sum(w * np.array(VALUES[word]) for w, word in zip(WEIGHTS, WORDS))

# ---------------------------------------------------------------- layout
ROW_X = [-1.5, 0.8, 3.1, 5.4]        # token columns from scene 2 on
TOKEN_Y = 3.05
GRID_Y = {"q": 1.75, "k": 0.35, "v": -1.05}
PLANE_ORIGIN = np.array([-4.3, -1.45, 0])
PLANE_UNIT = 1.4
TABLE_Y = [1.0, 0.15, -0.7, -1.55]
HEAD_Y = 1.9
COL_WORD, COL_SCORE, BAR_X0, BAR_UNIT = 1.2, 2.8, 3.7, 2.4


def load_timings() -> dict:
    path = Path(os.environ.get("TIMINGS", Path(__file__).with_name("timings.json")))
    data = json.loads(path.read_text())
    return data


def v3(xy) -> np.ndarray:
    return np.array([xy[0], xy[1], 0.0])


def token(word: str, size: float, color=INK) -> VGroup:
    t = Tex(word, font_size=size, color=color)
    box = SurroundingRectangle(t, buff=0.2, corner_radius=0.12, color=color if color != INK else DIM,
                               stroke_width=2.5)
    box.stretch_to_fit_height(size / 48 * 0.82)   # same height for every word
    box.move_to(t)
    return VGroup(box, t)


def cell_arrow(vec, center, color, width=5, scale=0.45, opacity=1.0) -> Arrow:
    d = v3(vec) * scale
    return Arrow(center - d / 2, center + d / 2, buff=0, color=color, stroke_width=width,
                 max_tip_length_to_length_ratio=0.3, max_stroke_width_to_length_ratio=12,
                 stroke_opacity=opacity, fill_opacity=opacity)


class SelfAttention(Scene):
    # ------------------------------------------------------------ timing
    def at(self, t: float) -> None:
        dt = t - self.renderer.time
        if dt > 1e-3:
            self.wait(dt)
        elif dt < -0.05:
            print(f"[timing] {t:.2f}: the animation is late by {-dt:.2f} s")

    def p(self, xy) -> np.ndarray:
        return PLANE_ORIGIN + v3(xy) * PLANE_UNIT

    def plane_arrow(self, xy, color, width=7, opacity=1.0, start=(0, 0)) -> Arrow:
        return Arrow(self.p(start), self.p(np.array(start) + np.array(xy)), buff=0, color=color,
                     stroke_width=width, max_tip_length_to_length_ratio=0.18,
                     max_stroke_width_to_length_ratio=14, stroke_opacity=opacity, fill_opacity=opacity)

    def tip_label(self, mob: Mobject, xy, gap=0.22) -> Mobject:
        u = v3(xy) / np.linalg.norm(xy)
        tip = self.p(xy)
        off = gap + abs(u[0]) * mob.width / 2 + abs(u[1]) * mob.height / 2
        return mob.move_to(tip + u * off)

    # ------------------------------------------------------------ film
    def construct(self) -> None:
        T = {s["id"]: s for s in load_timings()["sentences"]}
        total = load_timings()["total"]
        start = lambda i: T[i]["start"]

        # ===== Scene 1: a sentence, and the word bank =====================
        title = Tex("Self-attention", font_size=84, color=INK).move_to(UP * 2.35)
        xs1 = [-3.6, -1.2, 1.2, 3.6]
        toks = VGroup(*[token(w, 60).move_to(RIGHT * x) for w, x in zip(WORDS, xs1)])

        self.at(0.15)
        self.play(Write(title), run_time=1.3)
        self.at(start("s01") + 1.2)
        self.play(LaggedStart(*[FadeIn(t, shift=UP * 0.25) for t in toks], lag_ratio=0.3), run_time=1.8)

        self.at(start("s02"))
        bank1 = token("bank", 60, ACCENT).move_to(toks[3])
        self.play(Transform(toks[3], bank1), run_time=0.6)
        arcs1 = VGroup(*[
            ArcBetweenPoints(toks[3].get_top() + UP * 0.08, toks[i].get_top() + UP * 0.08,
                             angle=PI * 0.4, color=DIM, stroke_width=3)
            for i in range(3)
        ])
        self.play(LaggedStart(*[Create(a) for a in arcs1], lag_ratio=0.2), run_time=0.9)

        # ===== Scene 2: query, key and value from learned matrices =========
        self.at(T["s02"]["end"] + 0.25)
        toks_top = VGroup(*[
            token(w, 44, ACCENT if w == "bank" else INK).move_to(RIGHT * x + UP * TOKEN_Y)
            for w, x in zip(WORDS, ROW_X)
        ])
        self.play(FadeOut(title, shift=UP * 0.3), FadeOut(arcs1), run_time=0.4)
        self.play(Transform(toks, toks_top), run_time=0.8)

        def row_formula(sym, mat):
            return MathTex(rf"\vec{{{sym}}} = W_{{{mat}}}\,\vec{{x}}", font_size=42, color=INK)

        names = {
            "q": Tex("query", font_size=40, color=ACCENT),
            "k": Tex("key", font_size=40, color=OTHER),
            "v": Tex("value", font_size=40, color=OTHER),
        }
        forms = {"q": row_formula("q", "Q"), "k": row_formula("k", "K"), "v": row_formula("v", "V")}
        for r in ("q", "k", "v"):
            names[r].move_to(UP * GRID_Y[r]).to_edge(LEFT, buff=0.85)
            forms[r].next_to(RIGHT * -4.85 + UP * GRID_Y[r], RIGHT, buff=0)
        x_note = Tex(r"$\vec{x}$: the word as a vector", font_size=34, color=DIM).move_to(DOWN * 2.45 + LEFT * 3.7)
        learned = Tex(r"$W_Q,\ W_K,\ W_V$: learned in training", font_size=34, color=DIM)
        learned.move_to(DOWN * 2.45 + RIGHT * 2.9)

        self.at(start("s03") + 0.9)                  # "learned in training"
        self.play(FadeIn(learned, shift=UP * 0.15), run_time=0.5)
        self.at(start("s03") + 1.7)                  # "give each word three vectors"
        self.play(LaggedStart(*[Write(forms[r]) for r in ("q", "k", "v")], lag_ratio=0.35), run_time=1.5)
        self.play(FadeIn(x_note), run_time=0.4)

        grid = {}
        for r, src in (("q", None), ("k", KEYS), ("v", VALUES)):
            arrows = []
            for w, x in zip(WORDS, ROW_X):
                center = RIGHT * x + UP * GRID_Y[r]
                if r == "q":
                    vec = Q_BANK if w == "bank" else OTHER_QUERIES[w]
                    color, op = (ACCENT, 1.0) if w == "bank" else (DIM, 0.7)
                else:
                    vec, color, op = src[w], OTHER, 1.0
                arrows.append(cell_arrow(vec, center, color, opacity=op))
            grid[r] = VGroup(*arrows)

        for sid, r in (("s04", "q"), ("s05", "k"), ("s06", "v")):
            self.at(start(sid))
            self.play(FadeIn(names[r], shift=RIGHT * 0.2),
                      LaggedStart(*[GrowArrow(a) for a in grid[r]], lag_ratio=0.18), run_time=1.3)
            if r == "q":
                self.play(Indicate(grid["q"][3], color=ACCENT, scale_factor=1.25), run_time=0.6)

        # ===== Scene 3: dot product of the query with each key =============
        self.at(T["s06"]["end"])
        plane = NumberPlane(
            x_range=[-1.5, 3, 1], y_range=[-1.5, 2.5, 1],
            x_length=4.5 * PLANE_UNIT, y_length=4.0 * PLANE_UNIT,
            background_line_style={"stroke_color": OTHER, "stroke_width": 1.2, "stroke_opacity": 0.28},
            axis_config={"stroke_color": DIM, "stroke_width": 2},
        )
        plane.shift(PLANE_ORIGIN - plane.c2p(0, 0))
        q_arrow = self.plane_arrow(Q_BANK, ACCENT, width=8)
        k_arrows = VGroup(*[self.plane_arrow(KEYS[w], OTHER) for w in WORDS])
        k_labels = VGroup(*[self.tip_label(Tex(w, font_size=36, color=OTHER), KEYS[w]) for w in WORDS])
        qu = v3(Q_BANK) / np.linalg.norm(Q_BANK)
        q_label = MathTex(r"\vec{q}", font_size=46, color=ACCENT).move_to(
            self.p(Q_BANK) + rotate_vector(qu, -PI / 2) * 0.42 + qu * 0.05)
        caption = Tex(r"query", r" and ", r"keys", font_size=36)
        caption[0].set_color(ACCENT), caption[1].set_color(DIM), caption[2].set_color(OTHER)
        caption.move_to(plane.c2p(-1.5, -1.5), aligned_edge=DL).shift(RIGHT * 0.25 + UP * 0.22)
        caption.add_background_rectangle(color=BG, opacity=1.0, buff=0.08)

        self.play(
            FadeOut(VGroup(*names.values(), *forms.values(), x_note, learned)),
            FadeOut(VGroup(*grid["q"][:3])), FadeOut(grid["v"]),
            FadeIn(plane),
            ReplacementTransform(grid["q"][3], q_arrow),
            *[ReplacementTransform(grid["k"][i], k_arrows[i]) for i in range(4)],
            run_time=1.4,
        )
        self.play(FadeIn(q_label), FadeIn(k_labels), FadeIn(caption), run_time=0.5)

        head = MathTex(r"\vec{q}_{\,\text{bank}} \cdot \vec{k}", font_size=42, color=INK).move_to(
            RIGHT * COL_SCORE + UP * HEAD_Y)
        row_words = VGroup(*[Tex(w, font_size=38, color=INK).move_to(RIGHT * COL_WORD + UP * y)
                             for w, y in zip(WORDS, TABLE_Y)])
        scores = VGroup(*[DecimalNumber(r, num_decimal_places=2, font_size=40, color=INK)
                          .move_to(RIGHT * COL_SCORE + UP * y) for r, y in zip(RAW, TABLE_Y)])

        self.at(start("s07") + 1.3)
        self.play(Write(head), FadeIn(row_words), run_time=0.6)
        for i in range(4):
            self.play(Indicate(k_arrows[i], color=INK, scale_factor=1.08),
                      FadeIn(scores[i], shift=LEFT * 0.2), run_time=0.42)

        self.at(start("s08") + 0.5)
        reach = np.linalg.norm(KEYS["river"]) * 1.08
        ang = DashedLine(self.p(Q_BANK * 1.06), self.p(Q_BANK / np.linalg.norm(Q_BANK) * reach), color=ACCENT,
                         stroke_width=3, dash_length=0.1).set_opacity(0.85)
        self.play(k_arrows[2].animate.set_stroke(width=11), Create(ang),
                  scores[2].animate.set_color(ACCENT).scale(1.25), run_time=1.0)
        self.play(Indicate(k_labels[2], color=ACCENT), run_time=0.7)

        # ===== Scene 4: scale, then softmax ================================
        self.at(start("s09") + 0.9)
        head2 = MathTex(r"\frac{\vec{q}\cdot\vec{k}}{\sqrt{d_k}}", font_size=42, color=INK).move_to(head)
        self.play(FadeOut(head, shift=UP * 0.2), run_time=0.3)
        self.play(FadeIn(head2, shift=UP * 0.2), run_time=0.5)
        dk_note = Tex(r"key size $d_k = 2$", font_size=34, color=DIM).move_to(RIGHT * 5.15 + UP * HEAD_Y)
        self.play(FadeIn(dk_note), run_time=0.4)
        scaled = VGroup(*[DecimalNumber(s, num_decimal_places=2, font_size=40,
                                        color=ACCENT if i == 2 else INK).move_to(RIGHT * COL_SCORE + UP * y)
                          for i, (s, y) in enumerate(zip(SCALED, TABLE_Y))])
        scaled[2].scale(1.25)
        self.play(*[FadeOut(scores[i], shift=UP * 0.3) for i in range(4)],
                  *[FadeIn(scaled[i], shift=UP * 0.3) for i in range(4)], run_time=0.9)
        scores = scaled

        self.at(start("s10") + 0.15)
        soft = Tex("softmax", font_size=40, color=INK).move_to(RIGHT * 4.7 + UP * HEAD_Y)
        self.play(FadeOut(dk_note), run_time=0.25)
        self.play(Write(soft), run_time=0.5)
        bars = VGroup(*[
            Rectangle(width=max(w * BAR_UNIT, 0.02), height=0.36, stroke_width=0,
                      fill_color=OTHER, fill_opacity=0.9).move_to(RIGHT * BAR_X0 + UP * y, aligned_edge=LEFT)
            for w, y in zip(WEIGHTS, TABLE_Y)
        ])
        wnums = VGroup(*[DecimalNumber(w, num_decimal_places=2, font_size=36, color=INK)
                         .next_to(b, RIGHT, buff=0.18) for w, b in zip(WEIGHTS, bars)])
        self.play(LaggedStart(*[GrowFromEdge(b, LEFT) for b in bars], lag_ratio=0.15),
                  LaggedStart(*[FadeIn(n) for n in wnums], lag_ratio=0.15), run_time=1.2)
        parts = []
        for i, w in enumerate(W_SHOWN):
            parts += [f"{w:.2f}", "+"]
        parts[-1] = "= 1"
        total_line = MathTex(*parts, font_size=40, color=INK).move_to(RIGHT * 3.45 + DOWN * 2.5)
        self.play(Write(total_line), run_time=1.0)

        # ===== Scene 5: weighted sum of the values =========================
        self.at(T["s10"]["end"] + 0.05)
        v_caption = Tex("values", font_size=36, color=OTHER).move_to(caption, aligned_edge=LEFT)
        v_caption.add_background_rectangle(color=BG, opacity=1.0, buff=0.08)
        self.play(FadeOut(VGroup(q_arrow, q_label, k_arrows, k_labels, ang, caption)), run_time=0.35)

        v_arrows = VGroup(*[self.plane_arrow(VALUES[w], OTHER) for w in WORDS])
        v_labels = VGroup(*[self.tip_label(Tex(w, font_size=36, color=OTHER), VALUES[w]) for w in WORDS])
        self.play(FadeIn(v_caption), LaggedStart(*[GrowArrow(a) for a in v_arrows], lag_ratio=0.15),
                  FadeIn(v_labels), run_time=0.8)

        ghosts = VGroup(*[self.plane_arrow(VALUES[w], OTHER, width=4, opacity=0.25) for w in WORDS])
        scaled_v = VGroup(*[self.plane_arrow(WEIGHTS[i] * np.array(VALUES[w]), OTHER, width=8)
                            for i, w in enumerate(WORDS)])
        self.at(start("s11") + 0.62)
        self.add(ghosts)
        self.play(*[Transform(v_arrows[i], scaled_v[i]) for i in range(4)],
                  v_labels.animate.set_opacity(0.45),
                  LaggedStart(*[Indicate(b, color=INK, scale_factor=1.05) for b in bars], lag_ratio=0.1),
                  run_time=1.1)

        order = [2, 3, 1, 0]                  # river first, then the small ones, tip to tail
        pos = np.zeros(2)
        chain = []
        for i in order:
            vec = WEIGHTS[i] * np.array(VALUES[WORDS[i]])
            chain.append(self.plane_arrow(vec, OTHER, width=8, start=pos))
            pos = pos + vec
        self.at(start("s12"))
        self.play(*[Transform(v_arrows[i], chain[n]) for n, i in enumerate(order)], run_time=0.7)
        z_arrow = self.plane_arrow(Z, ACCENT, width=9)
        self.play(GrowArrow(z_arrow), run_time=0.7)
        zu = v3(Z) / np.linalg.norm(Z)
        z_label = Tex("new bank", font_size=40, color=ACCENT)
        z_label.move_to(self.p(Z) + rotate_vector(zu, PI / 2) * 0.55 + LEFT * 0.35)
        self.play(FadeIn(z_label, shift=UP * 0.15), run_time=0.5)

        self.at(start("s13") + 0.2)
        river_dir = DashedLine(self.p((0, 0)), self.p(np.array(VALUES["river"]) * 1.12), color=OTHER,
                               stroke_width=3, dash_length=0.12).set_opacity(0.8)
        self.play(Create(river_dir), v_labels[2].animate.set_opacity(1.0),
                  bars[2].animate.set_fill(ACCENT), wnums[2].animate.set_color(ACCENT), run_time=1.0)
        self.play(Indicate(z_arrow, color=ACCENT, scale_factor=1.06), Indicate(z_label, color=ACCENT),
                  run_time=0.9)

        # ===== Scene 6: one formula for every word =========================
        self.at(T["s13"]["end"] + 0.1)
        xs6 = [x - 2.25 for x in ROW_X]
        toks6 = VGroup(*[token(w, 44, ACCENT if w == "bank" else INK).move_to(RIGHT * x + UP * 1.35)
                         for w, x in zip(WORDS, xs6)])
        rest = VGroup(plane, v_caption, ghosts, v_arrows, v_labels, z_arrow, z_label, river_dir,
                      head2, soft, row_words, scores, bars, wnums, total_line)
        self.play(FadeOut(rest), run_time=0.5)
        self.play(Transform(toks, toks6), run_time=0.6)

        arcs6 = VGroup()
        for i in range(3):
            w = WEIGHTS[i]
            arcs6.add(ArcBetweenPoints(toks[3].get_top() + UP * 0.08, toks[i].get_top() + UP * 0.08,
                                       angle=PI * 0.42, color=OTHER,
                                       stroke_width=1.5 + 14 * w, stroke_opacity=0.35 + 0.65 * w / max(WEIGHTS)))
        self.play(LaggedStart(*[Create(a) for a in arcs6], lag_ratio=0.15), run_time=0.8)

        formula = MathTex(
            r"\mathrm{Attention}(Q,K,V) = \mathrm{softmax}\!\left(\frac{"
            r"\textcolor[HTML]{F7D96F}{Q}\textcolor[HTML]{58C4DD}{K}^{\top}}{\sqrt{d_k}}\right)"
            r"\textcolor[HTML]{58C4DD}{V}",
            font_size=60, tex_template=TEX,
        ).move_to(DOWN * 0.65)
        self.play(Write(formula), run_time=1.5)

        message = Tex(r"Each word becomes a blend of the values,\\"
                      r"weighted by how well its query matches each key.", font_size=42, color=INK)
        message.move_to(DOWN * 2.6)
        self.at(T["s14"]["end"] + 0.1)
        self.play(FadeIn(message, shift=UP * 0.2), run_time=0.8)
        self.at(total)
