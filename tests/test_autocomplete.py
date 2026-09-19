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



class TestAutocompleteControllerCanCompleteHere(unittest.TestCase):
    def setUp(self):
        self.controller = AutocompleteController.__new__(AutocompleteController)

    def test_end_of_text(self):
        self.assertTrue(self.controller._can_complete_here("hello", 5))

    def test_before_space(self):
        self.assertTrue(self.controller._can_complete_here("hello world", 5))

    def test_before_alphanumeric(self):
        self.assertFalse(self.controller._can_complete_here("hello", 2))
        self.assertFalse(self.controller._can_complete_here("hello_world", 5))
        self.assertFalse(self.controller._can_complete_here("var1", 3))

    def test_before_punctuation(self):
        self.assertTrue(self.controller._can_complete_here("func()", 4))
        self.assertTrue(self.controller._can_complete_here("my_list[]", 7))


class TestAutocompleteControllerInStringOrComment(unittest.TestCase):
    def setUp(self):
        self.controller = AutocompleteController.__new__(AutocompleteController)

    def test_outside_string(self):
        self.assertFalse(self.controller._in_string_or_comment("var = 42", 8))

    def test_inside_single_quote(self):
        self.assertTrue(self.controller._in_string_or_comment("var = 'hello", 12))
        self.assertFalse(self.controller._in_string_or_comment("var = 'hello'", 13))

    def test_inside_double_quote(self):
        self.assertTrue(self.controller._in_string_or_comment('var = "hello', 12))
        self.assertFalse(self.controller._in_string_or_comment('var = "hello"', 13))

    def test_escaped_quotes(self):
        self.assertTrue(self.controller._in_string_or_comment("var = 'hello\\' world", 19))
        self.assertTrue(self.controller._in_string_or_comment('var = "hello\\\" world', 19))

    def test_inside_comment(self):
        self.assertTrue(self.controller._in_string_or_comment("var = 42 # a comment", 20))
        self.assertTrue(self.controller._in_string_or_comment("# starting comment", 10))

    def test_multiline_context(self):
        # Cursor is on the next line, which doesn't have a comment or string open
        self.assertFalse(self.controller._in_string_or_comment("var = 42 # comment\nvar2 = 43", 29))
        # Cursor is on the next line, but inside a string opened on that line
        self.assertTrue(self.controller._in_string_or_comment("var = 42\nvar2 = 'test", 21))


class TestAutocompleteControllerSanitizeSuggestion(unittest.TestCase):
    def setUp(self):
        self.controller = AutocompleteController.__new__(AutocompleteController)
        self.controller._max_suggestion_chars = 80

    def test_basic_stripping(self):
        # suggestion is stripped of lstrip("\r\n") initially, but when word_prefix exists, it is lstrip()
        # let's assume no prefix match
        self.assertEqual(self.controller._sanitize_suggestion("\n\rsugg", " "), "sugg")

    def test_word_prefix_removal(self):
        # If prefix ends with "hel", and suggestion is "hello", it strips "hel"
        self.assertEqual(self.controller._sanitize_suggestion("hello", "hel"), "lo")
        self.assertEqual(self.controller._sanitize_suggestion("  hello", "hel"), "lo")

    def test_max_length(self):
        self.controller._max_suggestion_chars = 5
        self.assertEqual(self.controller._sanitize_suggestion("longsuggestion", " "), "longs")

    def test_repeating_characters(self):
        self.assertEqual(self.controller._sanitize_suggestion("aaaaaaaaa", " "), "")
        self.assertEqual(self.controller._sanitize_suggestion("123456789", " "), "") # all digits and >8
        self.assertEqual(self.controller._sanitize_suggestion("abcdefghi", " "), "abcdefghi") # valid

    def test_first_char_alphanumeric_if_prefix(self):
        self.assertEqual(self.controller._sanitize_suggestion("hel lo", "hel"), "") # wait, lstrip makes it 'lo', let's check
        # Actually suggestion.lstrip() of '  hello' is 'hello', if it starts with 'hel', it becomes 'lo'
        # The first character of 'lo' is 'l' (alphanumeric).
        # If the remaining suggestion is non-alphanumeric, e.g., '!world', it should return ""
        self.assertEqual(self.controller._sanitize_suggestion("hel!world", "hel"), "")


class TestAutocompleteControllerExtractSymbols(unittest.TestCase):
    def setUp(self):
        self.controller = AutocompleteController.__new__(AutocompleteController)
        self.controller._last_symbol_text = ""
        self.controller._symbol_cache = []
        self.controller._COMMON_DOT_IDENTIFIERS = ["Console.WriteLine"]

    def test_extract_from_text(self):
        text = "def my_func():\n    var_1 = 42"
        symbols = self.controller._extract_symbols(text)
        self.assertIn("my_func", symbols)
        self.assertIn("var_1", symbols)
        self.assertIn("def", symbols) # keyword

    def test_cache_logic(self):
        text = "var_a = 1"
        symbols1 = self.controller._extract_symbols(text)
        # Modify cache directly to verify it's used
        self.controller._symbol_cache = ["cached_var"]
        symbols2 = self.controller._extract_symbols(text)
        self.assertEqual(symbols2, ["cached_var"])


class TestAutocompleteControllerAssignmentSymbolSuggestion(unittest.TestCase):
    def setUp(self):
        self.controller = AutocompleteController.__new__(AutocompleteController)

    def test_after_equals(self):
        text = "my_var = 1\nmy_var = "
        self.assertEqual(self.controller._assignment_symbol_suggestion(text, 20), "my_var")

    def test_after_equals_multiline(self):
        text = "my_var = 1\nprev_var = 2\nmy_var = "
        self.assertEqual(self.controller._assignment_symbol_suggestion(text, len(text)), "prev_var")

    def test_after_equals_with_spaces(self):
        text = "my_var = 1\nmy_var   =    "
        self.assertEqual(self.controller._assignment_symbol_suggestion(text, 25), "my_var")

    def test_not_after_equals(self):
        text = "my_var == "
        self.assertEqual(self.controller._assignment_symbol_suggestion(text, 10), "")

    def test_other_operators(self):
        text = "my_var = 1\nmy_var + "
        self.assertEqual(self.controller._assignment_symbol_suggestion(text, 20), "my_var")


class TestAutocompleteControllerSymbolSuggestion(unittest.TestCase):
    def setUp(self):
        self.controller = AutocompleteController.__new__(AutocompleteController)
        self.controller._last_symbol_text = ""
        self.controller._symbol_cache = []
        self.controller._COMMON_DOT_IDENTIFIERS = []

    def test_no_suggestion_if_cannot_complete(self):
        # Middle of word
        text = "hello"
        self.assertEqual(self.controller._symbol_suggestion(text, 2), "")

    def test_assignment_fallback(self):
        text = "my_var = 1\nmy_var = "
        self.assertEqual(self.controller._symbol_suggestion(text, 20), "my_var")

    def test_symbol_match(self):
        text = "my_long_variable = 1\nmy_lo"
        # Prefix is "my_lo"
        # It should suggest "ng_variable"
        self.assertEqual(self.controller._symbol_suggestion(text, 26), "ng_variable")

    def test_no_symbol_match(self):
        text = "my_long_variable = 1\nother_"
        self.assertEqual(self.controller._symbol_suggestion(text, 27), "")

if __name__ == '__main__':
    unittest.main()
