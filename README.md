# COTW Stradivarius new-character patch and save cleanup

Two source-only Python tools for the unwanted **.270 Stradivarius** in theHunter: Call of the Wild with Rookie Warden - Zero-to-Hero Edition v1.0.2. Each prepares a separate output and review manifest. Neither automatically deploys files, starts the game, changes Steam Cloud or patches the executable.

**For new characters:** `prepare_new_character_patch.py` changes one grant-related flag in the equipment table. Two independently created fresh characters did not receive the rifle, and it remained absent after a full restart, without inventory cleanup. A separate lock-mode change failed. The successful patch keeps the original lock mode, $7,000 price, reward table and starting loadout. See [test notes](TEST_NOTES.md) for the exact coverage and remaining limits.

**For existing characters:** `prepare_selective_rifle_cleanup.py` remains available as a separate post-grant cleanup. The equipment patch does not remove a rifle that a save already owns.

## Prepare the new-character patch

Use Python 3.10 or newer; no additional packages. Extract your own untouched Rookie Warden v1.0.2 archive to a working folder. Run:

```sh
python prepare_new_character_patch.py "Rookie Warden/dropzone/settings/hp_settings/equipment_data.bin" "output/equipment_data.bin"
```

Use your actual extracted path. The generator accepts only the exact reviewed source SHA-256 `00a489abf8c65f196e3959cd0a487d85c74bd182c8543383b72b7a64dd2886e6`; it rejects other versions or already modified tables. It derives the target property from the RTPC structure, verifies the weapon name and node ID, changes uint32 property `0x3c814744` from 1 to 0, and requires exactly one changed byte. Its public property name is unknown; the isolated test identifies its grant-related effect.

Review the generated manifest. The output SHA-256 must be `733ae0959b6c4f254c80328d7408530e6332cb808933f00df75ac4e3b6813edd`.

With the game closed, back up your complete saves and current mod setup, then replace only `dropzone/settings/hp_settings/equipment_data.bin` in the **same unmodified Rookie Warden v1.0.2 setup** with the generated copy. Use the mod's normal launch instructions. Do this before creating a new character. Avoid replacing a table from a different version or another mod: this narrow generator does not merge changes.

Rollback restores your backed-up original equipment table. Keep complete save backups too; a later grant reconciliation or older save restore can change ownership. The game/mod binary is not included in this repository. Normal Huntsman .270 access remains available for caliber-required missions; ordinary purchase and quest completion have not been runtime tested.

## Exact target and supported format

- Weapon: `.270 Stradivarius`, internal name `equipment_weapon_ba_rifle_270_03`.
- Inspected RTPC node / save item ID: `0x83a28d8e` / `2208468366`, corroborated by an in-game backpack transfer.
- Game code: `3331010`; wrapped ADF v4; root `PlayerProfileData_22`.
- Observed Steam build: `25131233`; archive version `3322479`; UI `0.13.10`, network `66`.

The Huntsman (`_01`) and Warden (`_02`) are distinct weapons. Unknown/older builds and unexpected layouts are rejected. No weapon-specific byte offset is assumed: profile field offsets come from the embedded schema.

## Prepare an existing-save cleanup copy

Python 3.10 or newer, standard library only. Close the game normally and preserve a **complete coherent save-folder backup** first. Work on a disposable copy, never the only copy of a real profile.

In game, put the Stradivarius in the backpack **without equipping it**. Remove it from every saved loadout and vehicle storage. Quit normally. The current narrow tool expects exactly one owned rifle, quantity one, and one backpack entry. It refuses equipped/loadout/vehicle references rather than deleting dynamic-array elements.

Create `input/` inside this repository and place a **copy** of `thp_player_profile_adf` there. Input and output must stay under the scripts' directory. Run:

```sh
python prepare_selective_rifle_cleanup.py input/thp_player_profile_adf output/thp_player_profile_adf
```

The output file must not already exist. Inspect `output/thp_player_profile_adf.manifest.json` before considering deployment. Manifests contain local file paths; redact those before sharing them.

## What changes

Only three typed uint32 entries are cleared:

1. The matching `EquipmentOwned` entry.
2. Its paired `EquipmentAmount` entry.
3. The matching `EquipmentBackPack` entry.

Fixed-array lengths and indices stay intact. The tool checks the decompressed-byte allowlist, preserves the SAVE wrapper, reparses the output and verifies the semantic diff. Every other payload byte and the source copy remain unchanged. Weapon statistics, cosmetic records, unlock lists, grant ledgers, quests, cash and level are intentionally retained.

A purchased Stradivarius and a free Stradivarius look the same in these possession fields. Use this only when the owner explicitly wants that rifle removed. The tool does not revoke platform/DLC ownership.

## Deployment and rollback are separate

There is no automatic installer. Test the reviewed output in a backed-up disposable profile with the game closed. If Steam Cloud isolation is needed, obtain the account owner's approval and restore the prior per-game setting afterward. Do not edit Cloud caches, patch every historical backup slot, or mix files from unrelated checkpoints.

Rollback requires restoring the **complete pre-change checkpoint**. Restoring a mod table alone cannot restore removed inventory. Historical autosaves can still contain the rifle. A future migration, grant reconciliation or old-backup restore could bring it back.

Keep the normal Huntsman .270 and ammunition available for caliber-required missions. This tool does not change their definitions, prices or unlock requirements. Purchase, .270 mission completion, map changes and comprehensive paid-DLC compatibility were **not** runtime tested.

## Findings for Rookie Warden's author

The supplied v1.0.2 tables already price Stradivarius at $7,000 while retaining the Xmas 2017 direct-give cell. Blanking only `custom_rewards!E12` (`reward_social_xmas2017`, `Equipment Give Directly`) did **not** prevent ownership on a fresh character in the tested setup. The successful cleanup control used all original mod files, so that overlay is not required by the observed cleanup result. It is not included here as a fix.

The subsequent equipment-flag experiment prevented the observed initial grant while the original Xmas direct-give cell was retained. The grant routine itself has not been traced, and this does not establish the meaning of every use of that property on other equipment. Change only the identified rifle. The separate save cleanup retains entitlement and grant-history fields. [Sources and format references](SOURCES.md).

No saves, game assets, mod binaries, screenshots, Steam configuration or credentials are included.
