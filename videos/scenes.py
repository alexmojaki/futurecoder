from manim import (
    DOWN,
    LEFT,
    ORIGIN,
    RIGHT,
    UP,
    AnimationGroup,
    ApplyMethod,
    BulletedList,
    FadeInFrom,
    LaggedStart,
    Line,
    PangoText,
    Scene,
    ShowCreation,
    VGroup,
    Write,
    config,
)

Text = PangoText


class Main(Scene):
    def construct(self):
        self.wait(0.5)

        title = Text("futurecoder", font="monospace")

        lines = [
            Line(LEFT + direction, ORIGIN - direction * 0.06).set_stroke(width=5)
            for direction in [UP, DOWN]
        ]
        scale_factor = 0.3
        chevrons = (
            VGroup(
                *[
                    VGroup(*lines).copy().shift(LEFT * distance * 2)
                    for distance in [2, 1, 0]
                ]
            )
            .scale(scale_factor)
            .next_to(title, LEFT)
            .shift(LEFT * scale_factor)
        )
        self.play(
            LaggedStart(
                *[
                    AnimationGroup(*[ShowCreation(line) for line in chevron])
                    for chevron in chevrons
                ],
                lag_ratio=0.1
            ),
        )
        self.play(
            *[
                ApplyMethod(chevron.shift, RIGHT * (3 - i) * scale_factor)
                for i, chevron in enumerate(chevrons)
            ],
            *[
                FadeInFrom(char, LEFT * (len(title) + 1 - i) / len(title) / 2)
                for i, char in enumerate(title.chars)
            ]
        )

        logo = VGroup(chevrons, title)
        self.play(ApplyMethod(logo.to_edge, UP))

        spacer = Text("space").set_fill(opacity=0).set_stroke(opacity=0)
        (
            VGroup(
                slogan := Text("Learn to code for free"),
                spacer,
                interactive := Text("Interactive and engaging"),
                interactive_points := BulletedList(
                    "Type and run code at every step",
                    "Answer multiple choice questions",
                    "Solve exercises",
                ),
                spacer,
                easy := Text("Makes learning easy, not frustrating"),
                easy_points := BulletedList(
                    "Points out mistakes",
                    "Gives you tools to find and understand problems",
                    "Gradually guides you to a solution",
                    "Teaches Python, a popular and easy language",
                ),
            )
            .arrange(DOWN, aligned_edge=LEFT)
            .set_height(config["frame_height"] * 0.7)
            .next_to(logo, DOWN)
            .shift(DOWN * 0.5)
        )

        self.play(Write(slogan))

        for obj in [
            interactive,
            easy,
            *interactive_points,
            *easy_points,
        ]:
            self.play(FadeInFrom(obj, DOWN * 0.5))

        self.wait(1)


class Help(Scene):
    def construct(self):
        self.wait(0.5)

        spacer = Text("space").set_fill(opacity=0).set_stroke(opacity=0)
        (
            VGroup(
                title := Text("How to help"),
                spacer,
                points := BulletedList(
                    *"""\
Share futurecoder with your friends
Use the site and give us feedback
Donate to keep servers running
Contribute code on GitHub
Write course content
""".splitlines()
                ),
            )
            .arrange(DOWN, aligned_edge=LEFT)
            .set_height(config["frame_height"] * 0.7)
        )

        self.play(Write(title))

        self.wait(1)

        for obj in points:
            self.play(FadeInFrom(obj, DOWN * 0.5))

        self.wait(1)
