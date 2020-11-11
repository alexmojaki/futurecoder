from manim import *


class Logo(Scene):
    def construct(self):
        lines = [
            Line(LEFT + direction, ORIGIN - direction * 0.06).set_stroke(width=20)
            for direction in [UP, DOWN]
        ]
        chevron = VGroup(*lines)
        chevrons = [chevron.copy().shift(LEFT * distance * 2) for distance in [2, 1, 0]]
        self.play(
            LaggedStart(
                *[
                    AnimationGroup(*[ShowCreation(line) for line in chevron])
                    for chevron in chevrons
                ],
                lag_ratio=0.1
            )
        )
        self.play(
            ApplyMethod(chevrons[0].shift, RIGHT * 2),
            ApplyMethod(chevrons[1].shift, RIGHT),
        )
        self.wait()


class Futurecoder(Scene):
    def construct(self):
        spacer = Text("space").set_fill(opacity=0).set_stroke(opacity=0)
        group = (
            VGroup(
                Text("futurecoder", font="monospace"),
                spacer,
                Text("Learn to code for free"),
                spacer,
                Text("Interactive and engaging"),
                BulletedList(
                    "Type and run code at every step",
                    "Answer multiple choice questions",
                    "Solve exercises",
                ),
                spacer,
                Text("Makes learning easy, not frustrating"),
                BulletedList(
                    "Points out mistakes",
                    "Gives you tools to find and understand problems",
                    "Gradually guides you to a solution",
                    "Teaches Python, a popular and easy language",
                ),
            )
            .arrange(DOWN, aligned_edge=LEFT)
            .set_height(config.frame_height * 0.9)
        )
        flat = []
        for obj in group:
            if obj is spacer:
                continue
            if isinstance(obj, Text):
                flat.append(obj)
            else:
                flat.extend(obj)
        for obj in flat:
            self.play(FadeInFrom(obj, DOWN * 0.5))
            self.wait()
