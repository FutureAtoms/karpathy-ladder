from manim import *
BG = "#0E0F12"; INK = "#ECECEC"; DIM = "#8A8F98"; ACCENT = "#F7D96F"; OTHER = "#58C4DD"
config.background_color = BG
class ClosingCard(Scene):
    def construct(self):
        head = Tex("Recap", font_size=80, color=INK).move_to(UP * 2.75)
        steps = [("query, key, value", INK), ("compare query with keys", INK), ("softmax: weights", INK), ("blend the values", ACCENT)]
        items = VGroup(*[Tex(t, font_size=40, color=c) for t, c in steps])
        boxes = VGroup(*[SurroundingRectangle(m, buff=0.2, corner_radius=0.12, color=(ACCENT if i == 3 else DIM), stroke_width=2.5) for i, m in enumerate(items)])
        cells = VGroup(*[VGroup(b, m) for b, m in zip(boxes, items)]).arrange(RIGHT, buff=0.75).move_to(UP * 1.15)
        if cells.width > 13: cells.scale_to_fit_width(13)
        arrows = VGroup(*[Arrow(cells[i].get_right(), cells[i + 1].get_left(), buff=0.08, color=DIM, stroke_width=3, max_tip_length_to_length_ratio=0.35) for i in range(3)])
        formula = MathTex(r"\mathrm{Attention}(Q,K,V)=\mathrm{softmax}\!\left(\frac{QK^\top}{\sqrt{d_k}}\right)V", font_size=46, color=INK).next_to(cells, DOWN, buff=0.6)
        line = Line(LEFT * 5.2, RIGHT * 5.2, color=DIM, stroke_width=1.5).to_edge(DOWN, buff=1.05)
        made = Tex(r"Made with \textbf{The Karpathy Ladder}, a Claude Code skill", font_size=38, color=INK).next_to(line, DOWN, buff=0.2)
        repo = Tex(r"\texttt{github.com/FutureAtoms/karpathy-ladder}", font_size=32, color=OTHER).next_to(made, DOWN, buff=0.14)
        self.add(head, cells, arrows, formula, line, made, repo)
