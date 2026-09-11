from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/release.yml"


class ReleaseWorkflowContractTests(unittest.TestCase):
    def setUp(self):
        self.text = WORKFLOW.read_text(encoding="utf-8")

    def test_privileged_workflow_run_is_bounded_to_same_repo_main_push(self):
        for required in ("workflow_run.conclusion == 'success'", "workflow_run.event == 'push'", "workflow_run.head_branch == 'main'", "workflow_run.head_repository.full_name == github.repository"):
            self.assertIn(required, self.text)

    def test_checkout_is_immutable_and_current_runtime(self):
        self.assertIn("actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1", self.text)
        self.assertNotIn("actions/checkout@v4", self.text)

    def test_tag_publication_is_fenced_against_main_movement(self):
        self.assertIn("git ls-remote origin refs/heads/main", self.text)
        self.assertIn('--force-with-lease="refs/heads/main:$RELEASE_SHA"', self.text)
        self.assertIn("git push --atomic", self.text)
        self.assertIn('"$RELEASE_SHA:refs/heads/main"', self.text)

    def test_existing_tag_must_resolve_to_release_sha(self):
        self.assertIn('existing_target="$(git rev-list -n 1 "$tag")"', self.text)
        self.assertIn('if [[ "$existing_target" != "$RELEASE_SHA" ]]', self.text)
        self.assertIn("Release tag collision", self.text)

    def test_published_tag_and_release_are_rechecked(self):
        self.assertIn('published_target="$(git rev-list -n 1 "$tag")"', self.text)
        self.assertIn('test "$published_target" = "$RELEASE_SHA"', self.text)
        self.assertIn('gh release view "$tag"', self.text)


if __name__ == "__main__":
    unittest.main()
