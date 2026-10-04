from manim import *
BG = "#0E0F12"; INK = "#ECECEC"; DIM = "#8A8F98"; ACCENT = "#F7D96F"; OTHER = "#58C4DD"
config.background_color = BG

class TitleCard(Scene):
    def construct(self):
        title = Tex("Self-attention", font_size=110, color=INK)
        sub = Tex("in about a minute", font_size=56, color=DIM).next_to(title, DOWN, buff=0.35)
        words = VGroup(*[Tex(w, font_size=46, color=(ACCENT if w == "bank" else INK)) for w in ["the", "muddy", "river", "bank"]]).arrange(RIGHT, buff=0.55)
        boxes = VGroup(*[SurroundingRectangle(w, buff=0.18, corner_radius=0.12, color=(ACCENT if i == 3 else DIM), stroke_width=2.5) for i, w in enumerate(words)])
        row = VGroup(words, boxes).next_to(sub, DOWN, buff=0.75)
        top = VGroup(title, sub, row).move_to(UP * 0.95)
        line = Line(LEFT * 5.2, RIGHT * 5.2, color=DIM, stroke_width=1.5).to_edge(DOWN, buff=1.05)
        made = Tex(r"Made with \textbf{The Karpathy Ladder}, a Claude Code skill", font_size=38, color=INK).next_to(line, DOWN, buff=0.2)
        repo = Tex(r"\texttt{github.com/FutureAtoms/karpathy-ladder}", font_size=32, color=OTHER).next_to(made, DOWN, buff=0.14)
        self.add(top, line, made, repo)
