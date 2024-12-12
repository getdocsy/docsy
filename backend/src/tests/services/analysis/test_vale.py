import os
import unittest
import tempfile
from textwrap import dedent
import asyncio

from app.services.analysis.vale_analysis_service import (
    ValeFileAnalysis,
    analyze_file_vale,
    setup_vale_ini_file,
)


class TestValeAnalysis(unittest.TestCase):
    async def asyncSetUp(self):
        self.vale_ini_path = await setup_vale_ini_file()

    def setUp(self):
        # Run async setup
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.asyncSetUp())

        # Create test markdown file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(
                dedent(
                    """
                # Test Document

                This is very good. You should definitely use passive voice here.
                
                Things are being done in a way that is not optimal.
            """
                )
            )
            self.test_markdown_file = f.name

        # Create clean markdown file
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write(
                dedent(
                    """
                # Clear Documentation

                This document uses clear, active voice.
                
                We explain the concepts directly and concisely.
            """
                )
            )
            self.clean_markdown_file = f.name

    def tearDown(self):
        # Cleanup temporary files
        os.unlink(self.test_markdown_file)
        os.unlink(self.clean_markdown_file)

    def test_analyze_file_vale(self):
        result = self.loop.run_until_complete(
            analyze_file_vale(
                absolute_file_path=self.test_markdown_file,
                vale_ini_file_path=self.vale_ini_path,
                local_repo_path=os.path.dirname(self.test_markdown_file),
            )
        )
        self.assertIsInstance(result, ValeFileAnalysis)

    def test_analyze_clean_file_vale(self):
        result = self.loop.run_until_complete(
            analyze_file_vale(
                absolute_file_path=self.clean_markdown_file,
                vale_ini_file_path=self.vale_ini_path,
                local_repo_path=os.path.dirname(self.clean_markdown_file),
            )
        )
        self.assertIsInstance(result, ValeFileAnalysis)
        self.assertEqual(len(result.issues), 0)


if __name__ == "__main__":
    unittest.main()
