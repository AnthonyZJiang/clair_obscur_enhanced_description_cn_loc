## Workflow

#### On new game update
1. Use FModel to export following files:
    a. localisation file `Sandfall\Content\Localization\Game\zh-Hans\Game.locres` in both `json` and `raw` format from `packchunk0-Windows.pak`.
    b. File `Sandfall\Content\Gameplay\Lumina\DT_PassiveEffects.json` from `packchunk0-Windows.utoc`.
    c. Folder `Sandfall\Content\StringTables` from `packchunk0-Windows.pak`.
2. Move the exported `Content` folder under `Sandfall` to `data/Sandfall-ori`.
3. Use FModel to unpack everything in `EnhancedDescriptions` mod, and move `Content` folder to `data/Sandfall-ori`.
4. Run `generate_work_file.py` to generate `localisation_work_file.json`.
5. Edit translations in the work file.
6. Run `generate_mod.py` to generate the mod. 

---
#### Credit
https://github.com/efonte/ue-localization-tools
http://fluffyquack.com/tools/unrealpak.rar