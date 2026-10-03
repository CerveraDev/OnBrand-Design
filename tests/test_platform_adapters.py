import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

from tools.platform_adapters.cli import main
from tools.platform_adapters.contract import (
    PLATFORMS, ROOT, RUNTIMES, canonical_bytes, prepare, project_contract, run, sha256, write_json,
)
from tools.platform_adapters.install import install, installation_files
from tools.platform_adapters.json_semantics import json_semantic_bytes, json_semantic_equal
from tools.platform_adapters.parity import COMPONENTS, cache_reader, compare, evaluate, snapshot
from tools.rider_campaign_runtime.runtime import build_campaign_from_spec
from tests.test_rider_campaign_runtime import minimal_spec, refresh_copy_allocation, write_manifest, write_png
from scripts.create_project import render_tree, valid_slug


EXAMPLES = ROOT / "projects/the-rider/skills/onbrand-the-rider-email/examples"


def request_for(spec_path):
    return {
        **project_contract("the-rider"),
        "campaign_spec": str(spec_path), "inputs": {},
        "invocation": {"actor": "HUMAN", "explicit": True},
    }


class JsonSemanticTests(unittest.TestCase):
    def test_primitive_type_and_numeric_equivalence_matrix(self):
        groups = [(None,), (False,), (True,), (0, 0.0, -0.0), (1, 1.0), (1.5,),
                  ("",), ("0",), ("1",), ("true",), ([],), ({},)]
        for left_group, left_values in enumerate(groups):
            for right_group, right_values in enumerate(groups):
                for left in left_values:
                    for right in right_values:
                        with self.subTest(left=left, right=right):
                            equal = json_semantic_equal(left, right)
                            self.assertEqual(equal, left_group == right_group)
                            self.assertEqual(json_semantic_bytes(left) == json_semantic_bytes(right), equal)

    def test_object_key_order_and_nested_numeric_forms_are_equivalent(self):
        left = {"a": {"items": [True, 1, None, "x"]}, "b": -0.0}
        right = {"b": 0, "a": {"items": [True, 1.0, None, "x"]}}
        self.assertTrue(json_semantic_equal(left, right))
        self.assertEqual(sha256(json_semantic_bytes(left)), sha256(json_semantic_bytes(right)))

    def test_nested_object_array_and_scalar_type_changes_are_distinct(self):
        for left, right in ((True, 1), (False, 0), (None, ""), ("1", 1), ("true", True),
                            ([], {}), (None, False), (1.5, "1.5")):
            for wrap in (lambda value: value, lambda value: {"value": value},
                         lambda value: [value], lambda value: {"nested": [{"value": [value]}]}):
                with self.subTest(left=left, right=right):
                    self.assertFalse(json_semantic_equal(wrap(left), wrap(right)))

    def test_array_order_length_and_object_members_remain_significant(self):
        for left, right in (([1, 2], [2, 1]), ([None], []),
                            ({"a": None}, {}), ({"a": 1}, {"b": 1})):
            self.assertFalse(json_semantic_equal(left, right))

    def test_numeric_values_have_no_rounding_tolerance(self):
        self.assertFalse(json_semantic_equal(0.1 + 0.2, 0.3))
        self.assertFalse(json_semantic_equal(2 ** 53 + 1, float(2 ** 53 + 1)))
        self.assertFalse(json_semantic_equal(1, 1.0000000000000002))
        self.assertTrue(json_semantic_equal(2 ** 53, float(2 ** 53)))

    def test_nonfinite_and_non_json_values_are_rejected_recursively(self):
        for value in (float("nan"), float("inf"), -float("inf"), (1,), {1: "value"}):
            for wrap in (lambda item: item, lambda item: {"nested": [item]}):
                with self.subTest(value=value):
                    with self.assertRaises(ValueError):
                        json_semantic_equal(wrap(value), wrap(value))
                    with self.assertRaises(ValueError):
                        json_semantic_bytes(wrap(value))


class AdapterContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.spec_path = self.root / "approved.json"
        self.spec = minimal_spec()
        write_json(self.spec_path, self.spec)
        self.request_path = self.root / "request.json"
        self.request = request_for(self.spec_path)
        write_json(self.request_path, self.request)

    def rewrite(self):
        write_json(self.request_path, self.request)

    def test_approved_input_emits_same_json_for_all_platforms(self):
        source = self.spec_path.read_bytes()
        for platform in PLATFORMS:
            output = self.root / platform
            run(self.request_path, platform, output, explicit=True, build=False)
            emitted = json.loads((output / "campaign.runtime.json").read_text())
            emitted["campaign"]["output_dir"] = self.spec["campaign"]["output_dir"]
            self.assertEqual(canonical_bytes(emitted), canonical_bytes(self.spec))
            self.assertEqual(json.loads((output / "adapter-provenance.json").read_text())["platform"], platform)
        self.assertEqual(self.spec_path.read_bytes(), source)

    def test_explicit_flag_required_before_output_writes(self):
        for platform in PLATFORMS:
            with self.assertRaisesRegex(ValueError, "HUMAN"):
                run(self.request_path, platform, self.root / platform, explicit=False, build=False)
            self.assertFalse((self.root / platform).exists())

    def test_human_invocation_record_required(self):
        for invocation in ({"actor": "MODEL", "explicit": True}, {"actor": "HUMAN", "explicit": False},
                           {"actor": "HUMAN", "explicit": 1}, {"actor": "HUMAN", "explicit": True, "extra": 1}):
            self.request["invocation"] = invocation
            self.rewrite()
            with self.assertRaises(ValueError):
                prepare(self.request_path, "cli", explicit=True)

    def test_rejects_unsupported_contract_core_adapter_runtime_and_project(self):
        for field in ("contract_version", "core_version", "adapter_version", "runtime", "runtime_version", "project"):
            with self.subTest(field=field):
                request = request_for(self.spec_path)
                request[field] = "unsupported"
                write_json(self.request_path, request)
                with self.assertRaises(ValueError):
                    prepare(self.request_path, "cli", explicit=True)

    def test_rejects_unsupported_platform_and_campaign_schema(self):
        with self.assertRaises(ValueError):
            prepare(self.request_path, "unknown", explicit=True)
        self.spec["schema_version"] = "9.0"
        write_json(self.spec_path, self.spec)
        with self.assertRaisesRegex(ValueError, "schema"):
            prepare(self.request_path, "cli", explicit=True)

    def test_rejects_unknown_contract_fields(self):
        self.request["platform_rules"] = {}
        self.rewrite()
        with self.assertRaisesRegex(ValueError, "unknown"):
            prepare(self.request_path, "cli", explicit=True)

    def test_scaffold_project_never_borrows_rider_runtime(self):
        self.request.update(project_contract("cassia"))
        self.rewrite()
        with self.assertRaisesRegex(ValueError, "not implemented"):
            prepare(self.request_path, "cli", explicit=True)

    def test_checksums_and_approval_section_equality(self):
        for role, key in (("composition", "composition"), ("image", "image_workflow"), ("copy", "copy_allocation")):
            with self.subTest(role=role):
                approval = self.root / f"{role}.json"
                value = self.spec.get(key, {})
                write_json(approval, value)
                self.request["inputs"] = {role: {"path": approval.name, "sha256": sha256(approval.read_bytes())}}
                self.rewrite()
                if key in self.spec:
                    prepare(self.request_path, "cli", explicit=True)
                write_json(approval, {"unexpected": True})
                with self.assertRaisesRegex(ValueError, "checksum"):
                    prepare(self.request_path, "cli", explicit=True)
                self.request["inputs"][role]["sha256"] = sha256(approval.read_bytes())
                self.rewrite()
                with self.assertRaisesRegex(ValueError, "differs"):
                    prepare(self.request_path, "cli", explicit=True)

    def test_real_approved_fixture_and_attachments_are_shared(self):
        preparations = [prepare(EXAMPLES / "cross-platform.request.json", platform, explicit=True) for platform in PLATFORMS]
        self.assertTrue(all(item["spec"] == preparations[0]["spec"] for item in preparations))
        self.assertEqual(set(preparations[0]["provenance"]["input_sha256"]), {"composition", "selection"})

    def test_single_shared_runtime_entrypoint(self):
        self.assertIs(RUNTIMES["rider-campaign"][2], build_campaign_from_spec)

    def test_composition_attachment_boolean_to_number_audit_reproduction(self):
        request = json.loads((EXAMPLES / "cross-platform.request.json").read_text())
        request["campaign_spec"] = str(EXAMPLES / request["campaign_spec"])
        approval = json.loads((EXAMPLES / "rider-wellness-composition-plan.json").read_text())
        self.assertIs(approval["selected_modules"][0]["includes_header"], True)
        approval["selected_modules"][0]["includes_header"] = 1
        path = self.root / "composition.json"
        write_json(path, approval)
        request["inputs"] = {"composition": {"path": path.name, "sha256": sha256(path.read_bytes())}}
        write_json(self.request_path, request)
        for platform in PLATFORMS:
            with self.subTest(platform=platform):
                with self.assertRaisesRegex(ValueError, "Approval file differs"):
                    prepare(self.request_path, platform, explicit=True)

    def test_copy_attachment_number_to_boolean_is_rejected(self):
        approval = copy.deepcopy(self.spec["copy_allocation"])
        approval["content_units"][0]["max_occurrences"] = True
        path = self.root / "copy.json"
        write_json(path, approval)
        self.request["inputs"] = {"copy": {"path": path.name, "sha256": sha256(path.read_bytes())}}
        self.rewrite()
        with self.assertRaisesRegex(ValueError, "Approval file differs"):
            prepare(self.request_path, "cli", explicit=True)

    def test_approval_attachment_object_key_order_is_equivalent(self):
        approval = self.spec["copy_allocation"]
        path = self.root / "copy.json"
        write_json(path, dict(reversed(list(approval.items()))))
        self.request["inputs"] = {"copy": {"path": path.name, "sha256": sha256(path.read_bytes())}}
        self.rewrite()
        prepare(self.request_path, "cli", explicit=True)

    def test_selection_plan_type_change_is_rejected(self):
        request_path = EXAMPLES / "cross-platform.request.json"
        request = json.loads(request_path.read_text())
        request["campaign_spec"] = str(EXAMPLES / request["campaign_spec"])
        request["inputs"] = {"selection": dict(request["inputs"]["selection"])}
        request["inputs"]["selection"]["path"] = str(EXAMPLES / request["inputs"]["selection"]["path"])
        self.request = request
        self.rewrite()
        plan = json.loads((EXAMPLES / "rider-wellness-composition-plan.json").read_text())
        plan["selected_modules"][0]["includes_header"] = 1
        version, validator, builder, _ = RUNTIMES["rider-campaign"]
        with patch.dict(RUNTIMES, {"rider-campaign": (version, validator, builder, lambda value: plan)}):
            with self.assertRaisesRegex(ValueError, "Selection file differs"):
                prepare(self.request_path, "cli", explicit=True)

    def test_selection_must_match_canonical_composition(self):
        request = json.loads((EXAMPLES / "cross-platform.request.json").read_text())
        request["campaign_spec"] = str(EXAMPLES / request["campaign_spec"])
        request["inputs"] = {}
        selection = json.loads((EXAMPLES / "rider-wellness-composition-selection.json").read_text())
        selection["plan_id"] = "different-approved-plan"
        path = self.root / "selection.json"
        write_json(path, selection)
        request["inputs"]["selection"] = {"path": path.name, "sha256": sha256(path.read_bytes())}
        write_json(self.request_path, request)
        with self.assertRaisesRegex(ValueError, "Selection file differs"):
            prepare(self.request_path, "cli", explicit=True)

    def test_unrecognized_output_is_preserved(self):
        output = self.root / "output"
        output.mkdir()
        path = output / "campaign.runtime.json"
        path.write_text("user-owned content")
        with self.assertRaisesRegex(ValueError, "unrecognized"):
            run(self.request_path, "cli", output, explicit=True, build=False)
        self.assertEqual(path.read_text(), "user-owned content")

    def test_cli_returns_failure_for_missing_invocation(self):
        self.assertEqual(main(["emit", "--platform", "cli", "--request", str(self.request_path),
                               "--output", str(self.root / "failed")]), 3)

    def test_project_slug_cannot_create_overlength_skill_name(self):
        with self.assertRaises(ValueError):
            project_contract("../the-rider")
        with self.assertRaises(Exception):
            valid_slug("a" * 60)


class AdapterInstallTests(unittest.TestCase):
    def test_manual_wrappers_have_platform_specific_metadata_and_unique_ids(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory).resolve()
            for project in ("the-rider", "cassia"):
                for platform in ("codex", "claude"):
                    files = installation_files(project, platform, workspace)
                    install(project, platform, workspace)
                    self.assertEqual(install(project, platform, workspace), sorted(str(p) for p in files))
                    for path, content in files.items():
                        if path.name == "SKILL.md":
                            self.assertIn(f"name: {path.parent.name}", content)
                            self.assertEqual("disable-model-invocation: true" in content, platform == "claude")
                            reference = content.split("[the canonical workflow](")[1].split(")")[0]
                            self.assertTrue((path.parent / reference).resolve().is_file())
                        else:
                            self.assertIn("allow_implicit_invocation: false", content)
            self.assertEqual(len(list(workspace.rglob("SKILL.md"))), 8)

    def test_installer_refuses_existing_conflicting_files(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            files = installation_files("the-rider", "claude", workspace)
            path = next(iter(files))
            path.parent.mkdir(parents=True)
            path.write_text("user-owned skill")
            with self.assertRaisesRegex(ValueError, "overwrite"):
                install("the-rider", "claude", workspace)
            self.assertEqual(path.read_text(), "user-owned skill")

    def test_canonical_skills_keep_only_portable_frontmatter(self):
        sources = list((ROOT / "projects").glob("*/skills/*/SKILL.md"))
        sources += list((ROOT / "templates/project-starter").glob("*/SKILL.md"))
        for path in sources:
            frontmatter = path.read_text().split("---", 2)[1]
            self.assertNotIn("disable-model-invocation", frontmatter)
            self.assertNotIn("user-invocable", frontmatter)
            self.assertIn("allow_implicit_invocation: false", (path.parent / "agents/openai.yaml").read_text())

    def test_generator_scaffolds_adapter_descriptor_without_rider_rules(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory)
            replacements = {"__PROJECT_SLUG__": "new-project", "__PROJECT_NAME__": "New Project",
                            "__OWNER__": "Owner", "__AUTHOR__": "Author"}
            render_tree(ROOT / "templates/project-starter", destination, replacements)
            contract = json.loads((destination / "adapter.json").read_text())
            self.assertEqual(contract["project"], "new-project")
            self.assertIsNone(contract["runtime"])
            self.assertTrue((destination / "skills/onbrand-new-project-email/SKILL.md").is_file())


class AdapterParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        asset = write_png(cls.root / "pixel.png")
        spec = minimal_spec()
        spec["manifest"]["path"] = str(write_manifest(cls.root, asset))
        spec["modules"][0]["slots"] = {"headline": {"kind": "text", "value": "Internal Sample Headline"}}
        refresh_copy_allocation(spec)
        cls.spec_path = cls.root / "approved.json"
        write_json(cls.spec_path, spec)
        cls.request_path = cls.root / "request.json"
        write_json(cls.request_path, request_for(cls.spec_path))
        cls.snapshots = {}
        with patch("tools.rider_campaign_runtime.assets._read_asset",
                   side_effect=lambda source: (asset.read_bytes(), f"{sha256(source.encode())[:12]}.png")):
            for platform in PLATFORMS:
                run(cls.request_path, platform, cls.root / platform, explicit=True)
                cls.snapshots[platform] = snapshot(cls.root / platform, platform)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_all_critical_components_must_pass_at_100(self):
        report = compare(self.snapshots)
        self.assertTrue(report["passed"])
        self.assertEqual(report["aggregate_score"], 100)
        self.assertEqual(len(report["components"]), len(COMPONENTS))
        self.assertTrue(all(item["critical"] and item["score"] == 100 for item in report["components"]))

    def test_every_named_component_mismatch_blocks_even_high_aggregate(self):
        for component in COMPONENTS:
            with self.subTest(component=component):
                changed = copy.deepcopy(self.snapshots)
                changed["claude"][component] = {"unexpected_platform_difference": True}
                report = compare(changed)
                self.assertFalse(report["passed"])
                self.assertGreater(report["aggregate_score"], 90)
                self.assertFalse(next(item for item in report["components"] if item["id"] == component)["passed"])

    def test_boolean_to_number_campaign_audit_reproduction_blocks_gate(self):
        changed = copy.deepcopy(self.snapshots)
        changed["claude"]["campaign"]["variants"]["branded"] = 1
        report = compare(changed)
        self.assertFalse(report["passed"])
        self.assertLess(report["aggregate_score"], 100)
        for component in ("campaign", "variants"):
            result = next(item for item in report["components"] if item["id"] == component)
            self.assertFalse(result["passed"])
            self.assertEqual(result["score"], 66.67)
            self.assertNotEqual(result["sha256"]["cli"], result["sha256"]["claude"])

    def test_recursive_type_changes_block_every_component(self):
        for component in COMPONENTS:
            for left, right in ((True, 1), (False, 0), (None, ""), ("1", 1), ([], {})):
                with self.subTest(component=component, left=left, right=right):
                    changed = copy.deepcopy(self.snapshots)
                    for value in changed.values():
                        value[component]["audit_probe"] = {"nested": [{"items": [left]}]}
                    changed["codex"][component]["audit_probe"]["nested"][0]["items"][0] = right
                    report = compare(changed)
                    result = next(item for item in report["components"] if item["id"] == component)
                    self.assertFalse(report["passed"])
                    self.assertLess(report["aggregate_score"], 100)
                    self.assertFalse(result["passed"])
                    self.assertEqual(result["score"], 66.67)
                    self.assertNotEqual(result["sha256"]["cli"], result["sha256"]["codex"])

    def test_equivalent_numbers_have_matching_hashes_in_every_component(self):
        for component in COMPONENTS:
            with self.subTest(component=component):
                changed = copy.deepcopy(self.snapshots)
                for value in changed.values():
                    value[component]["audit_probe"] = {"nested": [1, 0]}
                changed["claude"][component]["audit_probe"] = {"nested": [1.0, -0.0]}
                report = compare(changed)
                result = next(item for item in report["components"] if item["id"] == component)
                self.assertTrue(report["passed"])
                self.assertEqual(result["score"], 100)
                self.assertEqual(len(set(result["sha256"].values())), 1)

    def test_nonfinite_component_number_is_rejected(self):
        changed = copy.deepcopy(self.snapshots)
        changed["claude"]["campaign"]["audit_probe"] = {"nested": [float("nan")]}
        with self.assertRaisesRegex(ValueError, "Non-finite"):
            compare(changed)

    def test_copy_owners_claims_exemptions_and_scores_are_not_normalized(self):
        for key in ("owner", "claim_policy", "dedupe_exemptions", "similarity", "thresholds"):
            with self.subTest(key=key):
                changed = copy.deepcopy(self.snapshots)
                changed["codex"]["copy_allocation"][key] = "unapproved change"
                self.assertFalse(compare(changed)["passed"])

    def test_missing_platform_or_component_is_rejected(self):
        changed = copy.deepcopy(self.snapshots)
        del changed["claude"]
        with self.assertRaises(ValueError):
            compare(changed)
        changed = copy.deepcopy(self.snapshots)
        del changed["cli"]["qa"]
        with self.assertRaises(ValueError):
            compare(changed)

    def test_identical_failed_qa_cannot_pass_parity(self):
        changed = copy.deepcopy(self.snapshots)
        for value in changed.values():
            value["qa"]["passed"] = False
        report = compare(changed)
        self.assertEqual(report["aggregate_score"], 100)
        self.assertFalse(report["passed"])

    def test_failed_qa_and_duplicate_check_ids_are_rejected(self):
        package = self.root / "cli/runtime-test"
        qa_path = package / "qa-report.json"
        original = qa_path.read_bytes()
        try:
            value = json.loads(original)
            value["passed"] = False
            write_json(qa_path, value)
            with self.assertRaisesRegex(ValueError, "not passing"):
                snapshot(self.root / "cli", "cli")
            value["passed"] = True
            value["checks"].append(value["checks"][0])
            write_json(qa_path, value)
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                snapshot(self.root / "cli", "cli")
        finally:
            qa_path.write_bytes(original)

    def test_altered_asset_and_stale_zip_are_rejected(self):
        package = self.root / "cli/runtime-test"
        asset = next((package / "images").iterdir())
        original = asset.read_bytes()
        try:
            asset.write_bytes(b"tampered")
            with self.assertRaisesRegex(ValueError, "checksum"):
                snapshot(self.root / "cli", "cli")
        finally:
            asset.write_bytes(original)
        html = next((package / "html").iterdir())
        original = html.read_bytes()
        try:
            html.write_bytes(original + b"unexpected")
            with self.assertRaisesRegex(ValueError, "ZIP bytes"):
                snapshot(self.root / "cli", "cli")
        finally:
            html.write_bytes(original)

    def test_provenance_extra_fields_and_output_path_are_rejected(self):
        path = self.root / "cli/adapter-provenance.json"
        original = path.read_bytes()
        try:
            value = json.loads(original)
            value["extra"] = True
            write_json(path, value)
            with self.assertRaisesRegex(ValueError, "unknown"):
                snapshot(self.root / "cli", "cli")
        finally:
            path.write_bytes(original)
        path = self.root / "cli/campaign.runtime.json"
        original = path.read_bytes()
        try:
            value = json.loads(original)
            value["campaign"]["output_dir"] = "unapproved path"
            write_json(path, value)
            with self.assertRaisesRegex(ValueError, "Undeclared"):
                snapshot(self.root / "cli", "cli")
        finally:
            path.write_bytes(original)

    def test_cache_preserves_source_bytes_and_rejects_unknown_remote(self):
        package = self.root / "cli/runtime-test"
        reader = cache_reader(package)
        record = json.loads((package / "asset-manifest.json").read_text())["assets"][0]
        data, _ = reader(record["source"])
        self.assertEqual(sha256(data), record["sha256"])
        with self.assertRaisesRegex(ValueError, "Uncached"):
            reader("https://example.com/new.png")

    def test_cache_size_boolean_cannot_match_one_byte_number(self):
        with tempfile.TemporaryDirectory() as directory:
            package = Path(directory)
            asset = package / "one-byte.bin"
            asset.write_bytes(b"x")
            write_json(package / "asset-manifest.json", {"assets": [{
                "source": "https://example.com/one-byte.bin", "package_path": asset.name,
                "sha256": sha256(b"x"), "size_bytes": True,
            }]})
            with self.assertRaisesRegex(ValueError, "checksum/size"):
                cache_reader(package)

    def test_provenance_stays_out_of_self_contained_zip(self):
        with ZipFile(self.root / "cli/runtime-test.zip") as archive:
            self.assertFalse(any("adapter-provenance" in name for name in archive.namelist()))
        self.assertNotEqual((self.root / "cli/adapter-provenance.json").read_bytes(),
                            (self.root / "codex/adapter-provenance.json").read_bytes())

    def test_parity_evaluator_never_overwrites_existing_outputs(self):
        with self.assertRaisesRegex(ValueError, "new directory"):
            evaluate(self.request_path, self.root / "cli", explicit=True)

    def test_extra_zip_directory_is_rejected(self):
        path = self.root / "cli/runtime-test.zip"
        original = path.read_bytes()
        try:
            with ZipFile(path, "a") as archive:
                archive.writestr("runtime-test/unexpected/", b"")
            with self.assertRaisesRegex(ValueError, "Invalid ZIP"):
                snapshot(self.root / "cli", "cli")
        finally:
            path.write_bytes(original)
