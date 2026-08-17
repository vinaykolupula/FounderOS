import unittest
from app.services.notebook import NotebookMemoryService, compute_revision_token, MAX_FACTS


class TestNotebookMemoryService(unittest.TestCase):
    """Function-to-function tests for Scoped Notebook Memory and fact indexing."""

    def test_compute_revision_token(self):
        text = "# FounderOS Institutional Memory\n- Fact 1"
        token1 = compute_revision_token(text)
        token2 = compute_revision_token(text)
        self.assertEqual(token1, token2)
        self.assertEqual(len(token1), 64)  # SHA-256 hex string

    def test_fold_capture_adds_new_facts_with_date_and_author(self):
        initial = "# FounderOS Institutional Memory\n"
        new_facts = ["Target CAC payback is 9 months", "PostgreSQL database migrated to primary cluster"]
        updated, count, rev = NotebookMemoryService.fold_capture(initial, new_facts, author="founder")

        self.assertEqual(count, 2)
        self.assertIn("Target CAC payback is 9 months", updated)
        self.assertIn("PostgreSQL database migrated to primary cluster", updated)
        self.assertIn("[logged_by: founder]", updated)
        self.assertEqual(len(rev), 64)

    def test_fold_capture_duplicate_suppression(self):
        initial = "# FounderOS Institutional Memory\n"
        new_facts = ["Target CAC payback is 9 months"]
        updated1, count1, _ = NotebookMemoryService.fold_capture(initial, new_facts, author="founder")
        self.assertEqual(count1, 1)

        # Attempt adding same fact again
        updated2, count2, _ = NotebookMemoryService.fold_capture(updated1, new_facts, author="founder")
        self.assertEqual(count2, 0)
        self.assertEqual(updated1, updated2)

    def test_query_facts_keyword_search(self):
        memory = (
            "# FounderOS Institutional Memory\n"
            "- (2026-08-16) Stripe integration completed for annual tier [logged_by: CRO]\n"
            "- (2026-08-16) Linear sync established for engineering tickets [logged_by: CTO]\n"
            "- (2026-08-16) Target NRR is 120% for enterprise accounts [logged_by: VP CS]\n"
        )

        stripe_results = NotebookMemoryService.query_facts(memory, "Stripe annual")
        self.assertEqual(len(stripe_results), 1)
        self.assertIn("Stripe integration completed", stripe_results[0])

        nrr_results = NotebookMemoryService.query_facts(memory, "NRR enterprise")
        self.assertEqual(len(nrr_results), 1)
        self.assertIn("Target NRR is 120%", nrr_results[0])

        empty_results = NotebookMemoryService.query_facts(memory, "Kubernetes non-existent")
        self.assertEqual(len(empty_results), 0)


if __name__ == "__main__":
    unittest.main()
