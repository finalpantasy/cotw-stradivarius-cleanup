# COTW Stradivarius selective save cleanup

An experimental, copy-only Python tool for removing the unwanted **.270 Stradivarius** from a disposable theHunter: Call of the Wild profile. It prepares a separate output file and a review manifest; it never deploys a save, starts the game, changes Steam Cloud, or edits installed mods.

This is a **post-grant cleanup**, not an automatic new-character grant-prevention mod. In the observed test, removal persisted through two full loads, including a control using unmodified Rookie Warden - Zero-to-Hero Edition v1.0.2. That is limited evidence for the tested build, not a guarantee across updates, maps or entitlements. See [test notes](TEST_NOTES.md).

## Exact target and supported format

- Weapon: `.270 Stradivarius`, internal name `equipment_weapon_ba_rifle_270_03`.
- Inspected RTPC node / save item ID: `0x83a28d8e` / `2208468366`, corroborated by an in-game backpack transfer.
- Game code: `3331010`; wrapped ADF v4; root `PlayerProfileData_22`.
- Observed Steam build: `25131233`; archive version `3322479`; UI `0.13.10`, network `66`.

The Huntsman (`_01`) and Warden (`_02`) are distinct weapons. Unknown/older builds and unexpected layouts are rejected. No weapon-specific byte offset is assumed: profile field offsets come from the embedded schema.

## Prepare a copy

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

Automatic prevention still needs tracing of the new-profile/legacy grant path. The source here offers a narrowly validated post-creation cleanup path without clearing entitlement or grant-history fields. [Sources and format references](SOURCES.md).

No saves, game assets, mod binaries, screenshots, Steam configuration or credentials are included.
