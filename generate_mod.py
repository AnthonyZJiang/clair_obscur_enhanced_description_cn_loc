import json
import subprocess
from pathlib import Path

from pylocres import LocresFile

MODE_NAME = "EnhancedDescriptions_zhHans-tmxk_P"
BASE = Path(".")
OUTPUT_BASE = BASE / "output"
LOC_ORI = BASE / "data" / "Sandfall-ori" / "Content" / "Localization" / "Game" / "zh-Hans" / "Game.locres"
LOC_WORK_FILE = OUTPUT_BASE / "localisation_work_file.json"
MOD_BASE = OUTPUT_BASE / MODE_NAME
OUTPUT_LOCRES = MOD_BASE / "Sandfall" / "Content" / "Localization" / "Game" / "zh-Hans" / "Game.locres"


def encode_locres(locres, translations):
    """Encode locres file with new translations."""
    replaced_count = 0
    for key, translation in translations.items():
        ns, res_key = key.split(".")
        if ns in locres and res_key in locres[ns]:
            locres[ns][res_key].translation = translation["loc_new"]
            replaced_count += 1
    OUTPUT_LOCRES.parent.mkdir(parents=True, exist_ok=True)
    try:
        locres.write(str(OUTPUT_LOCRES))
    except Exception as e:
        print(f"Error writing updated locres file {OUTPUT_LOCRES}: {e}")
        raise SystemExit(1) from e
    
    print(f"Replaced {replaced_count} values")


def generate_pak():
    """Create a .pak file from MOD_BASE using UnrealPak.exe with compression."""
    unreal_pak_dir = BASE / "UnrealPak"
    unreal_pak_exe = unreal_pak_dir / "UnrealPak.exe"
    filelist_path = unreal_pak_dir / "filelist.txt"
    pak_output = BASE.resolve() / "output" / f"{MOD_BASE.name}.pak"

    if not MOD_BASE.exists():
        print(f"Error: MOD_BASE folder does not exist: {MOD_BASE}")
        raise SystemExit(1)

    if not unreal_pak_exe.exists():
        print(f"Error: UnrealPak.exe not found at {unreal_pak_exe}")
        raise SystemExit(1)

    mod_base_abs = MOD_BASE.resolve()
    filelist_content = f'"{mod_base_abs}\\*.*" "..\\..\\..\\*.*"\n'
    filelist_path.write_text(filelist_content, encoding="utf-8")

    try:
        subprocess.run(
            [str(unreal_pak_exe), str(pak_output), "-create=filelist.txt", "-compress"],
            cwd=str(unreal_pak_dir),
            check=True,
        )
        print(f"Created: {pak_output}")
    except subprocess.CalledProcessError as e:
        print(f"Error running UnrealPak: {e}")
        raise SystemExit(1) from e


def main():
    try:
        locres = LocresFile()
        locres.read(str(LOC_ORI))
    except Exception as e:
        print(f"Error reading locres file {LOC_ORI}: {e}")
        raise SystemExit(1)

    with open(LOC_WORK_FILE, encoding="utf-8") as f:
        translations = json.load(f)

    encode_locres(locres, translations)
    generate_pak()

if __name__ == "__main__":
    main()
