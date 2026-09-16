import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from config import Config, DEFAULT_CONFIG


class TestConfig(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.mock_home = patch('config.Path.home', return_value=Path(self.temp_dir.name))
        self.mock_home.start()

    def tearDown(self):
        self.mock_home.stop()
        self.temp_dir.cleanup()

    def test_default_initialization(self):
        # Settings file does not exist initially
        config = Config()

        # Check properties are set to defaults
        self.assertEqual(config.font_family, DEFAULT_CONFIG['editor']['font_family'])
        self.assertEqual(config.theme, DEFAULT_CONFIG['appearance']['theme'])
        self.assertEqual(config.autocomplete_enabled, DEFAULT_CONFIG['autocomplete']['enabled'])

    def test_save_and_set(self):
        config = Config()

        # Modify a property
        config.set('editor', 'font_family', 'Comic Sans')
        config.save()

        # Verify JSON file
        settings_file = Path(self.temp_dir.name) / '.pyglow' / 'settings.json'
        self.assertTrue(settings_file.exists())

        with open(settings_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.assertEqual(data['editor']['font_family'], 'Comic Sans')

    def test_load_valid_json(self):
        # Create a valid JSON file first
        settings_dir = Path(self.temp_dir.name) / '.pyglow'
        settings_dir.mkdir(parents=True)
        settings_file = settings_dir / 'settings.json'

        custom_data = {
            'editor': {
                'font_family': 'Arial'
            }
        }

        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(custom_data, f)

        # Load config
        config = Config()

        # Custom setting should be loaded
        self.assertEqual(config.font_family, 'Arial')
        # Default settings should be merged
        self.assertEqual(config.theme, DEFAULT_CONFIG['appearance']['theme'])

    def test_load_invalid_json(self):
        # Create an invalid JSON file
        settings_dir = Path(self.temp_dir.name) / '.pyglow'
        settings_dir.mkdir(parents=True)
        settings_file = settings_dir / 'settings.json'

        with open(settings_file, 'w', encoding='utf-8') as f:
            f.write("invalid json content")

        # Load config, should not raise an error and fallback to defaults
        config = Config()
        self.assertEqual(config.font_family, DEFAULT_CONFIG['editor']['font_family'])

if __name__ == '__main__':
    unittest.main()
