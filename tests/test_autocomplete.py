import unittest
import pytest
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


def test_can_complete_here_at_end_of_string():
    """Test when cursor is at the end of the text."""
    # When cursor_pos == len(text), it should return True
    assert AutocompleteController._can_complete_here(None, "def foo():", 10) is True
    assert AutocompleteController._can_complete_here(None, "", 0) is True

def test_can_complete_here_before_whitespace():
    """Test when cursor is before a whitespace character."""
    # When next_char is a space, it should return True
    assert AutocompleteController._can_complete_here(None, "def foo(): ", 10) is True
    assert AutocompleteController._can_complete_here(None, "def foo():\n", 10) is True

def test_can_complete_here_before_word_character():
    """Test when cursor is before an alphanumeric or underscore character."""
    # When next_char matches [A-Za-z0-9_], it should return False
    assert AutocompleteController._can_complete_here(None, "def foo():", 4) is False # before 'f'
    assert AutocompleteController._can_complete_here(None, "my_var = 1", 3) is False # before '_'
    assert AutocompleteController._can_complete_here(None, "var1", 3) is False # before '1'

def test_can_complete_here_before_punctuation():
    """Test when cursor is before punctuation characters."""
    # When next_char is punctuation (not matching [A-Za-z0-9_]), it should return True
    assert AutocompleteController._can_complete_here(None, "def foo():", 7) is True # before '('
    assert AutocompleteController._can_complete_here(None, "my_var = 1", 7) is True # before '='

def test_can_complete_here_cursor_out_of_bounds():
    """Test when cursor is somehow out of bounds."""
    # Even if cursor > len, it hits the if cursor_pos < len(text) and returns True
    assert AutocompleteController._can_complete_here(None, "foo", 5) is True

if __name__ == '__main__':
    unittest.main()
