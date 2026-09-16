import unittest
from autocomplete import AutocompleteController

class TestAutocompleteControllerWordPrefix(unittest.TestCase):
    def setUp(self):
        # Create an instance without calling __init__ to avoid needing QApplication and QScintilla dependencies
        self.controller = AutocompleteController.__new__(AutocompleteController)

    def test_cursor_at_zero(self):
        self.assertEqual(self.controller._word_prefix("hello", 0), ("", 0))

    def test_cursor_negative(self):
        self.assertEqual(self.controller._word_prefix("hello", -5), ("", -5))

    def test_cursor_end_of_word(self):
        self.assertEqual(self.controller._word_prefix("hello world", 11), ("world", 6))

    def test_cursor_middle_of_word(self):
        self.assertEqual(self.controller._word_prefix("hello world", 8), ("wo", 6))

    def test_cursor_start_of_word(self):
        self.assertEqual(self.controller._word_prefix("hello world", 6), ("", 6))

    def test_with_numbers_and_underscores(self):
        self.assertEqual(self.controller._word_prefix("my_var_123", 10), ("my_var_123", 0))
        self.assertEqual(self.controller._word_prefix("func(my_var_123)", 15), ("my_var_123", 5))

    def test_cursor_after_punctuation(self):
        self.assertEqual(self.controller._word_prefix("hello.", 6), ("", 6))
        self.assertEqual(self.controller._word_prefix("hello(", 6), ("", 6))
        self.assertEqual(self.controller._word_prefix("hello ", 6), ("", 6))

    def test_cursor_beyond_length(self):
        # Current implementation of text[start:cursor_pos] handles out of bounds by truncating to string length
        self.assertEqual(self.controller._word_prefix("hello", 10), ("hello", 0))

    def test_empty_string(self):
        self.assertEqual(self.controller._word_prefix("", 0), ("", 0))

if __name__ == '__main__':
    unittest.main()
