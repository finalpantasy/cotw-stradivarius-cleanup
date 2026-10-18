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

## Limits

- One disposable profile, current code build 3331010 / PlayerProfileData_22 / wrapped ADF4.
- No map-change, ordinary Huntsman purchase, .270 quest-completion or comprehensive paid-DLC runtime tests.
- The test does not identify the executable grant routine or prove which initialization path reads the reward table.
- Store UI was owner-confirmed after cleanup; the persistence checks use decoded closed-save possession fields. There is no claim that changing a store price removes persisted inventory.
- The original live profile was not replaced by the cleaned test checkpoint. A previously owned original profile or an older backup can still show Owned.
- No current or portable binary offsets are offered. Unsupported inputs are rejected.

Private fixtures and game files are deliberately excluded. These notes describe the observed checks; they do not substitute for testing another build/account.
