from pathlib import Path
import unittest
from unittest.mock import Mock

from src.database import DatabaseRepository
from src.parser import ForumParser


FIXTURE = Path(__file__).parent / "fixtures" / "habr_comments.html"


class ForumParserTests(unittest.TestCase):
    def setUp(self):
        self.parser = ForumParser()
        self.html = FIXTURE.read_text(encoding="utf-8")

    def test_parse_habr_fixture_extracts_ids_authors_and_html(self):
        records = self.parser.parse_html(self.html, "https://habr.com/ru/articles/1/")
        self.assertEqual([item["id"] for item in records], [123456, 123457])
        self.assertEqual(records[0]["name"], "alice")
        self.assertIn("<b>комментарий</b>", records[0]["message"])
        self.assertEqual(records[1]["name"], "bob")

    def test_parse_page_downloads_html_with_session_headers(self):
        response = Mock(text=self.html)
        self.parser.session.get = Mock(return_value=response)
        results = self.parser.parse_page("https://habr.com/ru/articles/1/")
        self.parser.session.get.assert_called_once_with(
            "https://habr.com/ru/articles/1/", timeout=15.0
        )
        response.raise_for_status.assert_called_once()
        self.assertEqual(len(results), 2)
        self.assertIn("User-Agent", self.parser.session.headers)

    def test_save_to_db_persists_records_and_skips_duplicates(self):
        records = self.parser.parse_html(self.html)
        with DatabaseRepository(":memory:") as repository:
            self.assertEqual(self.parser.save_to_db(records, repository), 2)
            self.assertEqual(self.parser.save_to_db(records, repository), 0)
            self.assertEqual(repository.get_by_name("alice")[0]["id"], 123456)


if __name__ == "__main__":
    unittest.main()
