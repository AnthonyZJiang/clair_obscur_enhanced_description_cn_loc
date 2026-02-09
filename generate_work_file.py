"""Generate localisation work file from enhanced vs original StringTable diffs."""

import json
from pathlib import Path


# Paths
BASE = Path("data")
ORI_STRINGTABLES = BASE / "Sandfall-ori"
ENH_STRINGTABLES = BASE / "Sandfall-enhanced"
LOC_ORI = BASE / "Sandfall-ori" / "Content" / "Localization" / "Game" / "zh-Hans" / "Game.json"
LOC_MOD = BASE / "Sandfall-mod" / "Content" / "Localization" / "Game" / "zh-Hans" / "Game.json"
OUTPUT_WORK_FILE = Path("output") / "localisation_work_file.json"


def find_matching_json_files():
    """Find JSON files that exist in both enhanced and ori (by filename)."""
    enh_files = list(ENH_STRINGTABLES.rglob("*.json"))
    ori_files = {p.name: p for p in ORI_STRINGTABLES.rglob("*.json") if p.name != "Game.json"}
    matched = []
    for enh_path in enh_files:
        if enh_path.name == "Game.json":
            continue
        if enh_path.name in ori_files:
            matched.append((enh_path, ori_files[enh_path.name]))
    return matched


def extract_keys_to_entries(data):
    """Extract KeysToEntries from StringTable JSON, or None if not a StringTable."""
    if isinstance(data, list) and len(data) > 0:
        item = data[0]
        if isinstance(item, dict) and "StringTable" in item:
            st = item["StringTable"]
            namespace = st.get("TableNamespace", "")
            entries = st.get("KeysToEntries", {})
            return namespace, entries
    return None, None


def load_json(path):
    """Load JSON file."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def compute_differences_for_pair(enh_path, ori_path):
    """Compute enhanced vs original differences for a single StringTable file pair."""
    enh_data = load_json(enh_path)
    ori_data = load_json(ori_path)

    enh_ns, enh_entries = extract_keys_to_entries(enh_data)
    ori_ns, ori_entries = extract_keys_to_entries(ori_data)

    if enh_entries is None or ori_entries is None:
        return {}

    namespace = enh_ns or ori_ns
    common_keys = set(enh_entries) & set(ori_entries)

    differences = {}
    for key in common_keys:
        if enh_entries[key] != ori_entries[key]:
            diff_key = f"{namespace}.{key}" if namespace else key
            differences[diff_key] = {
                "enhanced": enh_entries[key],
                "ori": ori_entries[key],
            }

    return differences


def collect_all_differences():
    """Collect differences from all matched enhanced/ori file pairs."""
    all_differences = {}
    matched = find_matching_json_files()
    if not matched:
        raise ValueError("No matching JSON files found")
    for enh_path, ori_path in matched:
        pair_diffs = compute_differences_for_pair(enh_path, ori_path)
        all_differences.update(pair_diffs)
    return all_differences


def lookup_loc_value(diff_key, loc_data):
    """Look up a diff_key in localization data (nested namespace structure)."""
    if not loc_data:
        return None

    if "." in diff_key:
        ns, key = diff_key.split(".", 1)
        if ns in loc_data and key in loc_data[ns]:
            return loc_data[ns][key]
        return None

    for ns_data in loc_data.values():
        if isinstance(ns_data, dict) and diff_key in ns_data:
            return ns_data[diff_key]
    return None


def enrich_with_loc_values(differences, loc_data, *keys):
    """Add loc lookup values to each difference entry under the given keys."""
    for diff_key, diff_val in differences.items():
        loc_val = lookup_loc_value(diff_key, loc_data)
        for key in keys:
            diff_val[key] = loc_val


def export_to_json(differences, output_path):
    """Write differences to JSON file."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(differences, f, ensure_ascii=False, indent=2)


def main():
    """Generate localisation work file from enhanced vs original diffs."""
    differences = collect_all_differences()

    loc_ori = load_json(LOC_ORI)
    enrich_with_loc_values(differences, loc_ori, "loc_ori")

    loc_mod = load_json(LOC_MOD)
    enrich_with_loc_values(differences, loc_mod, "loc_mod", "loc_new")

    export_to_json(differences, OUTPUT_WORK_FILE)

    print(f"Found {len(differences)} entries for localisation.")
    print(f"Exported to: {OUTPUT_WORK_FILE}")


if __name__ == "__main__":
    main()
