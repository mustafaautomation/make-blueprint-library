"""Unit tests for blueprint structure. They do not call Make."""

from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from makebp.build import compile_spec  # noqa: E402
from makebp.dsl import M, chat, retry, scenario, slack  # noqa: E402
from makebp.validate import validate_blueprint  # noqa: E402


def _spec():
    return scenario(
        id="unit-sample",
        title="Unit sample scenario",
        category="email",
        difficulty="beginner",
        tags=["email", "slack"],
        apps=["Gmail", "Slack"],
        description="A minimal scenario used only by the validator unit test.",
        problem="Prove the compiler emits a blueprint Make's import shape accepts.",
        audience="The test suite.",
        time_saved="None. This spec is a fixture.",
        schedule="Every 15 minutes.",
        sample={"subject": "Hello", "text": "A short note from billing@example.com"},
        steps=[
            M(
                "mail",
                "google-email:TriggerWatchEmails",
                "Watch the inbox",
                "Polling trigger for the fixture.",
                mapper={"q": "is:unread", "maxResults": 1},
            ),
            M(
                "note",
                "slack:CreateMessage",
                "Post the subject",
                "Confirms mapper references resolve to the trigger.",
                mapper=slack("New mail: {{mail.subject}}"),
                onerror=retry("Slack was down. Retry the message later."),
            ),
        ],
    )


class BlueprintTests(unittest.TestCase):
    def test_compiled_blueprint_validates(self):
        blueprint, _nodes = compile_spec(_spec())
        self.assertEqual(validate_blueprint(blueprint), [])
        self.assertEqual(blueprint["flow"][0]["id"], 1)
        self.assertNotIn("__IMTCONN__", blueprint["flow"][0]["parameters"])
        self.assertIn("parameters", blueprint["flow"][0]["metadata"])
        encoded = json.dumps(blueprint)
        self.assertNotIn("sk_live_", encoded)
        self.assertNotIn("hook.make.com", encoded)

    def test_unknown_module_fails(self):
        blueprint, _nodes = compile_spec(_spec())
        broken = copy.deepcopy(blueprint)
        broken["flow"][1]["module"] = "not-a-real-app:DoAThing"
        broken["flow"][1]["version"] = 1
        errors = validate_blueprint(broken)
        self.assertTrue(any("allowlist" in error for error in errors))

    def test_missing_mapper_target_fails(self):
        blueprint, _nodes = compile_spec(_spec())
        broken = copy.deepcopy(blueprint)
        broken["flow"][1]["mapper"]["text"] = "Hello {{99.subject}}"
        errors = validate_blueprint(broken)
        self.assertTrue(any("does not exist" in error for error in errors))

    def test_connection_id_fails(self):
        blueprint, _nodes = compile_spec(_spec())
        broken = copy.deepcopy(blueprint)
        broken["flow"][1]["parameters"] = {"__IMTCONN__": 2545853}
        errors = validate_blueprint(broken)
        self.assertTrue(any("connection" in error for error in errors))

    def test_router_requires_two_routes(self):
        blueprint, _nodes = compile_spec(_spec())
        broken = copy.deepcopy(blueprint)
        broken["flow"][1] = {
            "id": 2,
            "module": "builtin:BasicRouter",
            "version": 1,
            "parameters": {},
            "mapper": None,
            "metadata": {"designer": {"x": 300, "y": 0, "name": "Router"}},
            "routes": [{"flow": [broken["flow"][1]]}],
        }
        # The moved module keeps id 2, which now collides. Give the inner module a new id
        # and drop the original so the only failure we care about is the single route,
        # after fixing the id collision.
        inner = broken["flow"][1]["routes"][0]["flow"][0]
        inner["id"] = 3
        inner["mapper"]["text"] = "New mail: {{1.subject}}"
        errors = validate_blueprint(broken)
        self.assertTrue(any("at least two routes" in error for error in errors))

    def test_cross_route_reference_fails(self):
        spec = _spec()
        from makebp.dsl import route, router

        spec["steps"] = [
            spec["steps"][0],
            router(
                "branch",
                "Split",
                "Two routes.",
                [
                    route("A", "First", [M("alpha", "slack:CreateMessage", "A", "A", mapper=slack("{{mail.subject}}"))]),
                    route(
                        "B",
                        "Second",
                        [M("beta", "slack:CreateMessage", "B", "B", mapper=slack("{{alpha.text}}"))],
                    ),
                ],
            ),
        ]
        blueprint, _nodes = compile_spec(spec)
        errors = validate_blueprint(blueprint)
        self.assertTrue(any("not upstream" in error for error in errors), errors)


if __name__ == "__main__":
    unittest.main()
