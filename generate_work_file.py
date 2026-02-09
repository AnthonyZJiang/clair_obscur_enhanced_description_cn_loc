import json
from pathlib import Path


# Paths
BASE = Path("data")
ORI_STRINGTABLES = BASE / "Sandfall-ori" / "Content" / "Content" / "StringTables"
ENH_STRINGTABLES = BASE / "Sandfall-enhanced" / "Content" / "StringTables"
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


def load_loc_json(path):
    """Load Game.json, return empty dict if not found."""
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    differences = {}

    # Step 1: Compare key-value pairs between enhanced and ori
    matched = find_matching_json_files()
    for enh_path, ori_path in matched:
        with open(enh_path, encoding="utf-8") as f:
            enh_data = json.load(f)
        with open(ori_path, encoding="utf-8") as f:
            ori_data = json.load(f)

        enh_ns, enh_entries = extract_keys_to_entries(enh_data)
        ori_ns, ori_entries = extract_keys_to_entries(ori_data)

        if enh_entries is None or ori_entries is None:
            continue

        namespace = enh_ns or ori_ns
        enh_keys = set(enh_entries)
        ori_keys = set(ori_entries)
        common = enh_keys & ori_keys

        for key in common:
            if enh_entries[key] != ori_entries[key]:
                diff_key = f"{namespace}.{key}" if namespace else key
                differences[diff_key] = {
                    "enhanced": enh_entries[key],
                    "ori": ori_entries[key],
                }

    # Step 2: Add loc values from Game.json (ori)
    loc_ori = load_loc_json(LOC_ORI)
    for diff_key, diff_val in list(differences.items()):
        if "." in diff_key:
            ns, key = diff_key.split(".", 1)
            loc_val = None
            if ns in loc_ori and key in loc_ori[ns]:
                loc_val = loc_ori[ns][key]
        else:
            loc_val = None
            for ns_data in loc_ori.values():
                if isinstance(ns_data, dict) and diff_key in ns_data:
                    loc_val = ns_data[diff_key]
                    break
        diff_val["loc_ori"] = loc_val

    # Step 3: Add trans_improved and trans values from zh-Hans Game.json
    loc_mod = load_loc_json(LOC_MOD)

    for diff_key, diff_val in list(differences.items()):
        loc_val = None

        if "." in diff_key:
            ns, key = diff_key.split(".", 1)
            if ns in loc_mod and key in loc_mod[ns]:
                loc_val = loc_mod[ns][key]
        else:
            for ns_data in loc_mod.values():
                if isinstance(ns_data, dict) and diff_key in ns_data:
                    loc_val = ns_data[diff_key]
                    break

        diff_val["loc_mod"] = loc_val
        diff_val["loc_new"] = loc_val

    # Export to JSON file
    output_path = OUTPUT_WORK_FILE
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(differences, f, ensure_ascii=False, indent=2)

    print(f"Found {len(differences)} entries for localisation.")
    print(f"Exported to: {output_path}")


if __name__ == "__main__":
    main()
