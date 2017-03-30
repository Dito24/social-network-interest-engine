class TextTest:
    def __init__(self, text, expected=None, actual=None):
        if actual is None:
            actual = []
        if expected is None:
            expected = []

        self.text = text
        self.expected_output = expected
        self.actual_output = actual
