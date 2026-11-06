"""Estado de los items del backlog y su ciclo de vida (Todo → In Progress → Done) en el Project."""

import contextlib
import io
import os
import unittest
from unittest.mock import patch

import mcp_projects as mcp
from crew import lifecycle as lc

PROJECT = {"id": "PVT_1", "title": "wallee-management"}


def item(status="Todo", **extra):
    return {"id": "PVTI_1", "title": "[W1] 1. Andamiaje", "state": "OPEN", "status": status, **extra}


class StatusReadingTests(unittest.TestCase):
    def test_status_comes_from_filter_items_or_from_list_items(self):
        filtered = mcp._normalize_project_item({"id": "a", "title": "t", "fieldValues": {"Title": "t", "Status": "In Progress"}})
        self.assertEqual(filtered["status"], "In Progress")
        by_id = mcp._normalize_project_item({"id": "b", "fieldValues": {"PVTF_x": "t", "PVTSSF_y": "Done"}})
        self.assertEqual(by_id["status"], "Done")
        self.assertEqual(mcp._normalize_project_item({"id": "c"})["status"], "")

    def test_status_field_id_and_update_call(self):
        rows = [{"id": "PVTI_1", "fieldValues": {"PVTF_title": "t", "PVTSSF_status": "In Progress"}}]
        with patch.object(mcp, "call_tool", return_value=rows) as call:
            self.assertEqual(mcp.status_field_id("PVT_1"), "PVTSSF_status")
            mcp.set_item_status("PVT_1", "PVTI_1", "Done")
        self.assertEqual(call.call_args.args, ("manage_project", {
            "action": "set_field_value", "projectId": "PVT_1", "itemId": "PVTI_1",
            "fieldId": "PVTSSF_status", "value": "Done"}))
        with self.assertRaises(ValueError):
            mcp.set_item_status("PVT_1", "PVTI_1", "Hecho")
        with patch.object(mcp, "call_tool", return_value=[]), self.assertRaises(RuntimeError):
            mcp.set_item_status("PVT_1", "PVTI_1", "Done")


class DisplayTests(unittest.TestCase):
    def test_status_is_shown_with_a_fallback_to_the_issue_state(self):
        self.assertIn("In Progress", lc.describe_item(item("In Progress")))
        self.assertIn("Done", lc.describe_item(item("Done")))
        self.assertIn("Open", lc.describe_item({"state": "OPEN"}))
        self.assertIn("Closed", lc.describe_item({"state": "closed"}))


class SetStatusTests(unittest.TestCase):
    def test_mcp_first_then_gh_then_a_combined_error(self):
        with patch.object(lc.mcp_projects, "set_item_status") as mcp_set, patch.object(lc, "_gh_set") as gh_set:
            self.assertIsNone(lc.set_status("P", "I", "Done"))
            gh_set.assert_not_called()
            mcp_set.side_effect = RuntimeError("GraphQL roto")
            self.assertIsNone(lc.set_status("P", "I", "Done"))
            gh_set.assert_called_once_with("P", "I", "Done")
            gh_set.side_effect = RuntimeError("sin permiso")
            error = lc.set_status("P", "I", "Done")
        self.assertIn("MCP: GraphQL roto", error)
        self.assertIn("gh: sin permiso", error)


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        quiet = contextlib.redirect_stdout(io.StringIO())
        quiet.__enter__()
        self.addCleanup(quiet.__exit__, None, None, None)
        env = patch.dict(os.environ, {"WALLEE_PROJECT_SYNC": "true"})
        env.start()
        self.addCleanup(env.stop)

    def test_start_moves_only_todo_items_to_in_progress(self):
        with patch.object(lc, "set_status", return_value=None) as setter:
            todo = item("Todo")
            self.assertTrue(lc.start_item(PROJECT, todo))
            self.assertEqual(todo["status"], "In Progress")
            setter.assert_called_once_with("PVT_1", "PVTI_1", "In Progress")
            setter.reset_mock()
            for other in (item("In Progress"), item("Done"), {"title": "sin id", "status": "Todo"}):
                self.assertFalse(lc.start_item(PROJECT, other))
            setter.assert_not_called()

    def test_finish_asks_and_marks_done(self):
        with patch.object(lc, "set_status", return_value=None) as setter:
            current = item("In Progress")
            self.assertTrue(lc.finish_item(PROJECT, current, ask=lambda _: ""))
            self.assertEqual(current["status"], "Done")
            setter.assert_called_once_with("PVT_1", "PVTI_1", "Done")
            setter.reset_mock()
            self.assertFalse(lc.finish_item(PROJECT, item("In Progress"), ask=lambda _: "n"))
            self.assertFalse(lc.finish_item(PROJECT, item("Done"), ask=lambda _: self.fail("no debe preguntar")))
            setter.assert_not_called()

    def test_failure_is_reported_without_raising_and_keeps_the_status(self):
        current = item("In Progress")
        with patch.object(lc, "set_status", return_value="MCP: x | gh: y"):
            self.assertFalse(lc.finish_item(PROJECT, current, ask=lambda _: ""))
        self.assertEqual(current["status"], "In Progress")

    def test_sync_can_be_disabled(self):
        with patch.dict(os.environ, {"WALLEE_PROJECT_SYNC": "false"}), patch.object(lc, "set_status") as setter:
            self.assertFalse(lc.start_item(PROJECT, item("Todo")))
            self.assertFalse(lc.finish_item(PROJECT, item("In Progress"), ask=lambda _: ""))
            setter.assert_not_called()


if __name__ == "__main__":
    unittest.main()
