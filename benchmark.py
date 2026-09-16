import time
from pygments.token import Token
from pygments import lex
from pygments.lexers import PythonLexer
from PySide6.QtGui import QSyntaxHighlighter, QTextDocument

import highlighter

class MockThemeManager:
    def __init__(self):
        # We need a dummy signal for theme_changed
        class DummySignal:
            def connect(self, callback):
                pass
        self.theme_changed = DummySignal()

    def get_color(self, key):
        from PySide6.QtGui import QColor
        return QColor(0, 0, 0)

def main():
    import os
    os.environ["QT_QPA_PLATFORM"] = "offscreen"

    from PySide6.QtWidgets import QApplication
    app = QApplication([])

    doc = QTextDocument()
    theme = MockThemeManager()
    hl = highlighter.Highlighter(doc, theme)

    # We will simulate high volume of tokens
    lexer = PythonLexer()
    # Let's generate a large chunk of python code
    code = """
def foo(x):
    if x > 10:
        print("Hello World!")
    else:
        return [i for i in range(x)]
""" * 1000

    tokens = list(lex(code, lexer))
    print(f"Generated {len(tokens)} tokens.")

    start_time = time.time()
    for token_type, value in tokens:
        hl._resolve_format(token_type)
    end_time = time.time()

    print(f"Time taken: {end_time - start_time:.6f} seconds")

if __name__ == "__main__":
    main()
