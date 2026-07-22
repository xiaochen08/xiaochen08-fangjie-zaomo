import importlib.util
import unittest
from copy import deepcopy
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "validate_combat_behavior.py"


def load_module():
    if not SCRIPT.exists():
        raise AssertionError("validate_combat_behavior.py is missing")
    spec = importlib.util.spec_from_file_location("validate_combat_behavior", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CombatBehaviorValidatorTests(unittest.TestCase):
    def setUp(self):
        self.actions = {
            "schema_version": 1,
            "project_id": "arena_mod",
            "asset_id": "iron_wolf_boss",
            "asset_version": "2.0.0",
            "model_sha256": "a" * 64,
            "rig_signature": "rig-iron-wolf-v2",
            "actions": [
                {"action_id": "animation.iron_wolf.guard"},
                {"action_id": "animation.iron_wolf.slash_1"},
                {"action_id": "animation.iron_wolf.slash_2"},
                {"action_id": "animation.iron_wolf.recover"},
                {"action_id": "animation.iron_wolf.phase_change"},
            ],
        }
        self.events = {
            "schema_version": 1,
            "project_id": "arena_mod",
            "asset_id": "iron_wolf_boss",
            "asset_version": "2.0.0",
            "model_sha256": "a" * 64,
            "rig_signature": "rig-iron-wolf-v2",
            "events": [
                {"event_id": "event.hitbox_on"},
                {"event_id": "event.hitbox_off"},
                {"event_id": "event.sword_whoosh"},
                {"event_id": "event.combat_cleanup"},
            ],
        }
        self.payload = {
            "schema_version": 1,
            "project_id": "arena_mod",
            "asset_id": "iron_wolf_boss",
            "asset_version": "2.0.0",
            "model_sha256": "a" * 64,
            "rig_signature": "rig-iron-wolf-v2",
            "animation_backend": "blender_epicfight",
            "runtime_ownership": {
                "owner_skill": "fjzm",
                "server_authoritative": True,
                "animation_workshop_role": "author_and_validate_contract",
            },
            "selection_policy": {
                "mode": "seeded_weighted",
                "seed_source": "entity_uuid_and_combat_cycle",
                "repetition_penalty": 0.35,
                "history_size": 2,
                "fallback_action_id": "animation.iron_wolf.guard",
            },
            "weapon_profiles": [
                {
                    "weapon_profile_id": "greatsword_two_hand",
                    "category": "greatsword",
                    "style": "two_hand",
                    "allowed_action_ids": [
                        "animation.iron_wolf.guard",
                        "animation.iron_wolf.slash_1",
                        "animation.iron_wolf.slash_2",
                        "animation.iron_wolf.recover",
                    ],
                }
            ],
            "interrupt_policies": [
                {
                    "interrupt_policy_id": "boss_standard",
                    "allowed_interrupts": [
                        "hurt",
                        "stun",
                        "knockdown",
                        "target_lost",
                        "phase_change",
                        "death",
                        "unload",
                    ],
                    "priority": ["death", "unload", "phase_change", "stun", "hurt", "target_lost"],
                    "cleanup_event_ids": ["event.hitbox_off", "event.combat_cleanup"],
                }
            ],
            "behavior_series": [
                {
                    "series_id": "ground_combo_a",
                    "weapon_profile_id": "greatsword_two_hand",
                    "weight": 60.0,
                    "cooldown_ticks": 20,
                    "loop": {"enabled": False, "max_iterations": 1},
                    "interrupt_policy_id": "boss_standard",
                    "conditions": {
                        "distance": {"min": 0.0, "max": 3.5},
                        "eye_height": {"min": -1.5, "max": 1.5},
                        "required_states": ["grounded", "line_of_sight"],
                    },
                    "steps": [
                        {
                            "action_id": "animation.iron_wolf.slash_1",
                            "play_speed": 1.0,
                            "transition": "blend",
                            "root_motion": "authored",
                            "cancel_window": [0.72, 1.0],
                            "event_ids": ["event.sword_whoosh", "event.hitbox_on", "event.hitbox_off"],
                            "branch": {"on_hit": "continue", "on_whiff": "recover"},
                        },
                        {
                            "action_id": "animation.iron_wolf.slash_2",
                            "play_speed": 1.08,
                            "transition": "conditional",
                            "root_motion": "authored",
                            "cancel_window": [0.68, 1.0],
                            "event_ids": ["event.sword_whoosh", "event.hitbox_on", "event.hitbox_off"],
                            "branch": {"on_hit": "recover", "on_whiff": "recover"},
                        },
                    ],
                }
            ],
            "phase_profiles": [
                {
                    "phase_id": "phase_1",
                    "health_range": [0.5, 1.0],
                    "allowed_series_ids": ["ground_combo_a"],
                    "transition_action_id": "animation.iron_wolf.phase_change",
                },
                {
                    "phase_id": "phase_2",
                    "health_range": [0.0, 0.5],
                    "allowed_series_ids": ["ground_combo_a"],
                    "transition_action_id": "animation.iron_wolf.phase_change",
                },
            ],
            "acceptance": {
                "all_transitions_previewed": True,
                "hit_and_whiff_branches_tested": True,
                "interrupt_cleanup_tested": True,
                "actual_runtime_evidence_required": True,
            },
        }

    def validate(self, payload=None, actions=None, events=None):
        return load_module().validate_combat_behavior(
            payload or self.payload,
            actions or self.actions,
            events or self.events,
        )

    def test_accepts_identity_locked_weighted_combat_graph(self):
        self.assertEqual(self.validate()["errors"], [])

    def test_rejects_unknown_action_and_event_ids(self):
        payload = deepcopy(self.payload)
        payload["behavior_series"][0]["steps"][0]["action_id"] = "animation.iron_wolf.missing"
        payload["behavior_series"][0]["steps"][0]["event_ids"].append("event.missing")
        joined = "\n".join(self.validate(payload)["errors"])
        self.assertIn("action-library.json", joined)
        self.assertIn("animation-events.json", joined)

    def test_rejects_nonpositive_weight_and_invalid_sensor_ranges(self):
        payload = deepcopy(self.payload)
        series = payload["behavior_series"][0]
        series["weight"] = 0
        series["conditions"]["distance"] = {"min": 4.0, "max": 2.0}
        series["conditions"]["eye_height"] = {"min": 2.0, "max": -2.0}
        joined = "\n".join(self.validate(payload)["errors"])
        self.assertIn("weight", joined)
        self.assertIn("distance", joined)
        self.assertIn("eye_height", joined)

    def test_requires_death_unload_interrupts_and_cleanup(self):
        payload = deepcopy(self.payload)
        policy = payload["interrupt_policies"][0]
        policy["allowed_interrupts"] = ["hurt"]
        policy["priority"] = ["hurt"]
        policy["cleanup_event_ids"] = []
        joined = "\n".join(self.validate(payload)["errors"])
        self.assertIn("death", joined)
        self.assertIn("unload", joined)
        self.assertIn("cleanup_event_ids", joined)

    def test_rejects_unbounded_loop_and_unreasonable_play_speed(self):
        payload = deepcopy(self.payload)
        payload["behavior_series"][0]["loop"] = {"enabled": True, "max_iterations": 0}
        payload["behavior_series"][0]["steps"][0]["play_speed"] = 4.0
        joined = "\n".join(self.validate(payload)["errors"])
        self.assertIn("max_iterations", joined)
        self.assertIn("play_speed", joined)

    def test_requires_hit_and_whiff_branches_and_valid_cancel_window(self):
        payload = deepcopy(self.payload)
        step = payload["behavior_series"][0]["steps"][0]
        step["branch"] = {"on_hit": "continue"}
        step["cancel_window"] = [0.9, 0.2]
        joined = "\n".join(self.validate(payload)["errors"])
        self.assertIn("on_whiff", joined)
        self.assertIn("cancel_window", joined)

    def test_rejects_non_ascii_runtime_ids(self):
        payload = deepcopy(self.payload)
        payload["behavior_series"][0]["series_id"] = "地面连招"
        joined = "\n".join(self.validate(payload)["errors"])
        self.assertIn("ASCII", joined)

    def test_requires_anti_repetition_fallback_and_seeded_choice(self):
        payload = deepcopy(self.payload)
        payload["selection_policy"] = {
            "mode": "random",
            "repetition_penalty": 0,
            "history_size": 0,
            "fallback_action_id": "animation.iron_wolf.missing",
        }
        joined = "\n".join(self.validate(payload)["errors"])
        self.assertIn("seeded_weighted", joined)
        self.assertIn("repetition_penalty", joined)
        self.assertIn("history_size", joined)
        self.assertIn("fallback_action_id", joined)

    def test_requires_complete_nonoverlapping_boss_phase_coverage(self):
        payload = deepcopy(self.payload)
        payload["phase_profiles"][1]["health_range"] = [0.1, 0.4]
        joined = "\n".join(self.validate(payload)["errors"])
        self.assertIn("health_range", joined)
        self.assertIn("cover", joined)

    def test_runtime_integration_remains_owned_by_main_skill(self):
        payload = deepcopy(self.payload)
        payload["runtime_ownership"]["owner_skill"] = "fjzm-animation"
        joined = "\n".join(self.validate(payload)["errors"])
        self.assertIn("owner_skill must be fjzm", joined)

    def test_rejects_cross_asset_or_rig_mismatch(self):
        actions = deepcopy(self.actions)
        events = deepcopy(self.events)
        actions["rig_signature"] = "wrong-rig"
        events["asset_id"] = "other_boss"
        joined = "\n".join(self.validate(actions=actions, events=events)["errors"])
        self.assertIn("rig_signature", joined)
        self.assertIn("asset_id", joined)

    def test_requires_runtime_transition_branch_interrupt_evidence(self):
        payload = deepcopy(self.payload)
        for key in payload["acceptance"]:
            payload["acceptance"][key] = False
        joined = "\n".join(self.validate(payload)["errors"])
        for phrase in (
            "all_transitions_previewed",
            "hit_and_whiff_branches_tested",
            "interrupt_cleanup_tested",
            "actual_runtime_evidence_required",
        ):
            self.assertIn(phrase, joined)


if __name__ == "__main__":
    unittest.main()
