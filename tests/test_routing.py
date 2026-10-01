from dataclasses import dataclass, field
import unittest

from aidrax_core.routing import HealthState, Job, Node, NodeRouter


@dataclass
class MemoryState:
    jobs: dict[str, str] = field(default_factory=dict)
    assignments: dict[str, str] = field(default_factory=dict)

    def register(self, job_id: str) -> bool:
        if job_id in self.jobs:
            return False
        self.jobs[job_id] = "PENDING"
        return True

    def status(self, job_id: str) -> str:
        return self.jobs[job_id]

    def set_status(self, job_id: str, status: str) -> None:
        self.jobs[job_id] = status

    def assignment(self, job_id: str) -> str | None:
        return self.assignments.get(job_id)

    def assign(self, job_id: str, node_id: str) -> None:
        self.assignments[job_id] = node_id


@dataclass
class MemoryEvents:
    entries: list[tuple[str, dict[str, object]]] = field(default_factory=list)

    def publish(self, event: str, payload: dict[str, object]) -> None:
        self.entries.append((event, payload))


def node(node_id: str, health: HealthState, capabilities: set[str], load: int = 0) -> Node:
    return Node(node_id, health, frozenset(capabilities), load)


class RoutingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.state = MemoryState()
        self.events = MemoryEvents()
        self.router = NodeRouter(self.state, self.events)

    def test_ready_is_preferred_and_capability_is_required(self) -> None:
        selected = self.router.dispatch(
            Job("J-1", "video.render"),
            [
                node("hq", HealthState.READY, {"coding"}),
                node("studio", HealthState.READY, {"video.render"}, 80),
            ],
        )
        self.assertEqual("studio", selected)
        self.assertEqual("routing.dispatched", self.events.entries[-1][0])

    def test_degraded_is_fallback_only(self) -> None:
        selected = self.router.dispatch(
            Job("J-2", "coding"),
            [
                node("studio", HealthState.DEGRADED, {"coding"}),
                node("hq", HealthState.READY, {"coding"}, 90),
            ],
        )
        self.assertEqual("hq", selected)

    def test_owner_gate_and_missing_node_retain_the_job(self) -> None:
        self.assertIsNone(
            self.router.dispatch(
                Job("J-3", "system", protected_action=True),
                [node("hq", HealthState.READY, {"system"})],
            )
        )
        self.assertEqual("WAITING_OWNER_GATE", self.state.status("J-3"))
        self.assertIsNone(
            self.router.dispatch(
                Job("J-4", "video.render"),
                [node("studio", HealthState.UNREACHABLE, {"video.render"})],
            )
        )
        self.assertEqual("WAITING_FOR_CAPABLE_NODE", self.state.status("J-4"))

    def test_retry_preserves_job_identity_and_fails_over(self) -> None:
        job = Job("J-5", "coding")
        nodes = [
            node("studio", HealthState.READY, {"coding"}),
            node("hq", HealthState.READY, {"coding"}, 1),
        ]
        for _ in range(3):
            self.assertEqual("studio", self.router.dispatch(job, nodes))
            self.router.report_result("J-5", "studio", False)
        self.assertEqual("hq", self.router.dispatch(job, nodes))
        self.assertEqual({"J-5"}, set(self.state.jobs))

    def test_rejects_mismatched_node_result(self) -> None:
        self.router.dispatch(Job("J-6", "coding"), [node("hq", HealthState.READY, {"coding"})])
        with self.assertRaises(ValueError):
            self.router.report_result("J-6", "studio", True)


if __name__ == "__main__":
    unittest.main()
