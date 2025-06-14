from game.layouts.layout_quiz import LayoutScreen

# Questions data
questions_data = [
    {
        "question": "assets/image/quiz/_hard/topic1/q1/quiz.png",
        "answer": "b",
        "btn_a_src": "assets/image/quiz/_hard/topic1/q1/a.png",
        "btn_b_src": "assets/image/quiz/_hard/topic1/q1/b.png",
        "btn_c_src": "assets/image/quiz/_hard/topic1/q1/c.png",
    },
    {
        "question": "assets/image/quiz/_hard/topic1/q2/quiz.png",
        "answer": "a",
        "btn_a_src": "assets/image/quiz/_hard/topic1/q2/a.png",
        "btn_b_src": "assets/image/quiz/_hard/topic1/q2/b.png",
        "btn_c_src": "assets/image/quiz/_hard/topic1/q2/c.png",
    },
    {
        "question": "assets/image/quiz/_hard/topic1/q3/quiz.png",
        "answer": "c",
        "btn_a_src": "assets/image/quiz/_hard/topic1/q3/a.png",
        "btn_b_src": "assets/image/quiz/_hard/topic1/q3/b.png",
        "btn_c_src": "assets/image/quiz/_hard/topic1/q3/c.png",
    },
    {
        "question": "assets/image/quiz/_hard/topic1/q4/quiz.png",
        "answer": "b",
        "btn_a_src": "assets/image/quiz/_hard/topic1/q4/a.png",
        "btn_b_src": "assets/image/quiz/_hard/topic1/q4/b.png",
        "btn_c_src": "assets/image/quiz/_hard/topic1/q4/c.png",
    },
    {
        "question": "assets/image/quiz/_hard/topic1/q5/quiz.png",
        "answer": "a",
        "btn_a_src": "assets/image/quiz/_hard/topic1/q5/a.png",
        "btn_b_src": "assets/image/quiz/_hard/topic1/q5/b.png",
        "btn_c_src": "assets/image/quiz/_hard/topic1/q5/c.png",
    },
    {
        "question": "assets/image/quiz/_hard/topic1/q6/quiz.png",
        "answer": "b",
        "btn_a_src": "assets/image/quiz/_hard/topic1/q6/a.png",
        "btn_b_src": "assets/image/quiz/_hard/topic1/q6/b.png",
        "btn_c_src": "assets/image/quiz/_hard/topic1/q6/c.png",
    },
    {
        "question": "assets/image/quiz/_hard/topic1/q7/quiz.png",
        "answer": "c",
        "btn_a_src": "assets/image/quiz/_hard/topic1/q7/a.png",
        "btn_b_src": "assets/image/quiz/_hard/topic1/q7/b.png",
        "btn_c_src": "assets/image/quiz/_hard/topic1/q7/c.png",
    },
    {
        "question": "assets/image/quiz/_hard/topic1/q8/quiz.png",
        "answer": "c",
        "btn_a_src": "assets/image/quiz/_hard/topic1/q8/a.png",
        "btn_b_src": "assets/image/quiz/_hard/topic1/q8/b.png",
        "btn_c_src": "assets/image/quiz/_hard/topic1/q8/c.png",
    },
    {
        "question": "assets/image/quiz/_hard/topic1/q9/quiz.png",
        "answer": "a",
        "btn_a_src": "assets/image/quiz/_hard/topic1/q9/a.png",
        "btn_b_src": "assets/image/quiz/_hard/topic1/q9/b.png",
        "btn_c_src": "assets/image/quiz/_hard/topic1/q9/c.png",
    },
    {
        "question": "assets/image/quiz/_hard/topic1/q10/quiz.png",
        "answer": "b",
        "btn_a_src": "assets/image/quiz/_hard/topic1/q10/a.png",
        "btn_b_src": "assets/image/quiz/_hard/topic1/q10/b.png",
        "btn_c_src": "assets/image/quiz/_hard/topic1/q10/c.png",
    },
]


class Topic1HardScreen(LayoutScreen):
    """Topic 1 hard mode quiz screen with 30s timeout per question"""

    def __init__(self, app, **kw):
        super().__init__(
            app=app,
            questions_data=questions_data,
            home_destination="go_topic1",
            bar_timeout_src="assets/image/quiz/bar_timeout/topic1.png",
            timeout_duration=10.0,
            group_key_store="topic1",
            key_store="_hard",
            question_size_hint=(0.9, 0.5),      # Size of question - All questions in questions_data
            options_size_hint=(0.8, 0.12),      # Size of options - All questions in questions_data
            **kw
        )