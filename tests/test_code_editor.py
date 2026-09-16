import sys
import os
import unittest

# Ensure Qt works headlessly
os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PySide6.QtWidgets import QApplication
from code_editor import CodeEditor
from theme import ThemeManager

class TestCodeEditorFindMatchingBracket(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # We need a QApplication instance to instantiate CodeEditor
        cls.app = QApplication.instance() or QApplication(sys.argv)
        cls.theme_manager = ThemeManager()

    def setUp(self):
        self.editor = CodeEditor(self.theme_manager)

    def test_find_matching_bracket_forward(self):
        # Basic matching forward
        text = "(test)"
        self.assertEqual(self.editor._find_matching_bracket(text, 0, "("), 5)

        text = "[test]"
        self.assertEqual(self.editor._find_matching_bracket(text, 0, "["), 5)

        text = "{test}"
        self.assertEqual(self.editor._find_matching_bracket(text, 0, "{"), 5)

    def test_find_matching_bracket_backward(self):
        # Basic matching backward
        text = "(test)"
        self.assertEqual(self.editor._find_matching_bracket(text, 5, ")"), 0)

        text = "[test]"
        self.assertEqual(self.editor._find_matching_bracket(text, 5, "]"), 0)

        text = "{test}"
        self.assertEqual(self.editor._find_matching_bracket(text, 5, "}"), 0)

    def test_find_matching_bracket_nested_forward(self):
        text = "( ( ) )"
        # Outer bracket
        self.assertEqual(self.editor._find_matching_bracket(text, 0, "("), 6)
        # Inner bracket
        self.assertEqual(self.editor._find_matching_bracket(text, 2, "("), 4)

    def test_find_matching_bracket_nested_backward(self):
        text = "( ( ) )"
        # Outer bracket
        self.assertEqual(self.editor._find_matching_bracket(text, 6, ")"), 0)
        # Inner bracket
        self.assertEqual(self.editor._find_matching_bracket(text, 4, ")"), 2)

    def test_find_matching_bracket_unmatched(self):
        text = "(test"
        self.assertEqual(self.editor._find_matching_bracket(text, 0, "("), -1)

        text = "test)"
        self.assertEqual(self.editor._find_matching_bracket(text, 4, ")"), -1)

        text = "( ( )"
        self.assertEqual(self.editor._find_matching_bracket(text, 0, "("), -1)

    def test_find_matching_bracket_interleaved(self):
        text = "( [ ) ]"
        # The logic currently simply searches for the corresponding bracket character,
        # ignoring other types of brackets.
        # depth counting on "(" will just look for ")" and ignore "[" or "]"
        self.assertEqual(self.editor._find_matching_bracket(text, 0, "("), 4)

if __name__ == '__main__':
    unittest.main()
