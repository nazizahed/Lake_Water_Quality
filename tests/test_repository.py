import unittest

from scripts.validate_repository import (
    validate_example_data,
    validate_notebooks,
    validate_readme,
)


class RepositoryQualityTests(unittest.TestCase):
    def test_notebooks_are_documented_and_output_free(self):
        self.assertEqual(validate_notebooks(), [])

    def test_readme_links_and_fences(self):
        self.assertEqual(validate_readme(), [])

    def test_example_era5_schema(self):
        self.assertEqual(validate_example_data(), [])


if __name__ == "__main__":
    unittest.main()
