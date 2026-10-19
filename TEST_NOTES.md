# Test notes

Observed on 18 October 2026 with the installed licensed game and a separate disposable profile. Original saves and installed mods were backed up and isolated. No downloaded editor/tool binary was executed; the parsers and output generator are independently written Python using the standard library.

| Stage | Observation |
| --- | --- |
| Exact original Rookie Warden v1.0.2 | Stradivarius showed **Owned** at store/storage despite its $7,000 price. |
| Fresh character, only the Xmas direct-give cell blanked | Still **Owned**, level 1, rifle score 0/450, $0 cash. Single-cell prevention failed on this setup. |
| In-game transfer to backpack | Only new backpack ID was `0x83a28d8e`; this matches the equipment definition node named `equipment_weapon_ba_rifle_270_03`. The starter rifle was also removed from the backpack, so the whole save diff is not described as a one-action-only fixture. |
| Selective cleanup, first full load and normal exit | Owner reported Store no longer said Owned. Closed-save inspection confirmed target absent, every other owned ID retained, and inspected unlock/grant lists unchanged. |
| Second full load with all 67 original Rookie Warden files | Target remained absent in the resulting main profile; other owned IDs, `EquipmentUnlocked`, `GivenDLCItems` and `UnlockedHuntClubEquipment` were retained. |

The cleanup output differed in nine decompressed bytes, entirely within the three allowed uint32 entries. All other decompressed bytes and wrapper bytes were identical before loading the game. Fixed-array holes were accepted in this test. Other item quantities can change through ordinary game/reward behavior during play; no blanket runtime claim about every quantity is made.

The final checkpoint loaded at a claimed Layton outpost with store/storage nearby. An earlier position-vector copy did not teleport a fresh character: startup reset its position. Copying map discovery state persisted, and normal in-game fast travel was used. No teleport implementation is shipped.

## New-character prevention follow-up

Fresh characters were created in independently empty save roots with the same account, installed game build and exact 67-file Rookie Warden setup. No inventory cleanup was performed in these prevention tests.

| Candidate | Closed-save observation |
| --- | --- |
| Only Stradivarius `Locked` property (`0xb304f782`) 6 to 0 | Failed: a fresh level-1, XP-0, cash-0 character owned one Stradivarius. |
| Only Stradivarius property `0x3c814744` 1 to 0; original Locked=6 retained | Passed first creation: Stradivarius absent from ownership/backpack; every other starting item and quantity matched the failed control when compared by item ID. |
| Full restart with the successful flag candidate | Stradivarius remained absent from the resulting closed main profile. |
| Independent repeat with the same flag candidate and another empty save root | Passed again: a different character ID, level 1, XP 0 and cash 0; Stradivarius absent, all other initial item IDs/quantities and inspected grant/unlock lists matched the control. |

The flag candidate changes **one byte** of `equipment_data.bin`; every other byte, the reward table and initial loadout are unchanged. Its public property name is not established. The test supports a grant-related effect for this item, without identifying the full executable path or claiming the flag means the same thing for other equipment. Both successful fresh creations used Layton on the same account and build; other starting reserves/accounts remain untested.

`EquipmentUnlocked`, `GivenDLCItems` and `UnlockedHuntClubEquipment` matched between the two initial profiles. The second profile used no inventory edits. After that first creation had been preserved, only its position vector and Layton map-discovery file were copied for an optional outpost-access check; that position copy again loaded at spawn, and is not shipped. The restarted profile gained one normal starting caller through ordinary game initialization; this is not described as a byte-identical profile comparison.

The source-only patch generator reproduced the exact runtime candidate, rejected an existing output without changing it, and rejected an unsupported source hash without creating output. No proprietary table or save is included.

## Limits

- Current code build 3331010 / PlayerProfileData_22 / wrapped ADF4. Multiple independent profiles were used for the prevention follow-up; the earlier cleanup test used one profile.
- No map-change, ordinary Huntsman purchase, .270 quest-completion or comprehensive paid-DLC runtime tests.
- The test does not identify the executable grant routine or prove which initialization path reads the reward table.
- Store UI was owner-confirmed after cleanup; the persistence checks use decoded closed-save possession fields. There is no claim that changing a store price removes persisted inventory.
- The original live profile was not replaced by the cleaned test checkpoint. A previously owned original profile or an older backup can still show Owned.
- No current or portable binary offsets are offered. Unsupported inputs are rejected.

Private fixtures and game files are deliberately excluded. These notes describe the observed checks; they do not substitute for testing another build/account.
