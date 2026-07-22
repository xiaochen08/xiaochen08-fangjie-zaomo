import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "simulate_combat_director.py"
CONTRACT = ROOT / "contracts" / "combat-behavior-system.json"


def load_module():
    if not SCRIPT.exists():
        raise AssertionError("simulate_combat_director.py is missing")
    spec = importlib.util.spec_from_file_location("simulate_combat_director", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CombatDirectorSimulationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def state(self, **changes):
        state = {
            "entity_id": "iron-vanguard-test-001",
            "combat_cycle": 7,
            "weapon_profile_id": "greatsword_two_hand",
            "health_ratio": 0.8,
            "distance": 2.0,
            "eye_height": 0.0,
            "grounded": True,
            "line_of_sight": True,
        }
        state.update(changes)
        return state

    def test_range_and_phase_filter_the_eligible_series(self):
        module = load_module()
        phase_1 = module.eligible_series(self.contract, self.state(distance=5.0), {})
        self.assertEqual([item["series_id"] for item in phase_1], ["mid_gap_close"])
        phase_2 = module.eligible_series(self.contract, self.state(health_ratio=0.3, distance=7.0), {})
        self.assertEqual([item["series_id"] for item in phase_2], ["far_leap"])

    def test_invalid_height_or_line_of_sight_uses_fallback(self):
        module = load_module()
        for state in (self.state(eye_height=5.0), self.state(line_of_sight=False)):
            result = module.select_series(self.contract, state, history=[], cooldowns={})
            self.assertEqual(result["action_id"], "animation.iron_vanguard.guard")
            self.assertTrue(result["fallback"])

    def test_seeded_selection_is_reproducible(self):
        module = load_module()
        first = module.select_series(self.contract, self.state(distance=2.55), history=[], cooldowns={})
        second = module.select_series(self.contract, self.state(distance=2.55), history=[], cooldowns={})
        self.assertEqual(first, second)

    def test_recent_series_receives_the_repetition_penalty(self):
        module = load_module()
        eligible = module.eligible_series(self.contract, self.state(health_ratio=0.3, distance=2.55), {})
        weights = module.effective_weights(self.contract, eligible, ["close_combo_a"])
        self.assertLess(weights["close_combo_a"], weights["close_spin_finisher"])

    def test_hit_and_whiff_branches_are_resolved(self):
        module = load_module()
        step = self.contract["behavior_series"][0]["steps"][0]
        self.assertEqual(module.resolve_branch(step, "hit"), "continue")
        self.assertEqual(module.resolve_branch(step, "whiff"), "recover")

    def test_interrupts_return_priority_and_cleanup(self):
        module = load_module()
        policy = self.contract["interrupt_policies"][0]
        death = module.resolve_interrupt(policy, "death")
        hurt = module.resolve_interrupt(policy, "hurt")
        self.assertLess(death["priority_index"], hurt["priority_index"])
        self.assertIn("event.hitbox_off", death["cleanup_event_ids"])
        self.assertIn("event.combat_cleanup", death["cleanup_event_ids"])

    def test_acceptance_run_covers_boundaries_branches_and_interrupts(self):
        module = load_module()
        report = module.run_acceptance(self.contract, cycles=600)
        self.assertEqual(report["implementation_status"], "contract_simulated")
        self.assertFalse(report["runtime_verified"])
        self.assertTrue(all(report["checks"].values()))
        self.assertEqual(set(report["selection_counts"]), {"close_combo_a", "close_spin_finisher", "mid_gap_close", "far_leap"})
        self.assertGreater(report["selection_counts"]["close_combo_a"], 0)
        self.assertGreater(report["branch_checks"]["hit"], 0)
        self.assertGreater(report["branch_checks"]["whiff"], 0)
        self.assertEqual(set(report["interrupt_checks"]), {"hurt", "stun", "knockdown", "target_lost", "phase_change", "death", "unload"})
        self.assertIn("fallback_count", report)
        self.assertIn("immediate_repeat_count", report)
        self.assertEqual(sum(report["selection_counts"].values()) + report["fallback_count"], report["cycles"])
        self.assertEqual(report["immediate_repeat_count"], 0)


if __name__ == "__main__":
    unittest.main()
