# Sources

- [Rookie Warden - Zero-to-Hero Edition posts](https://www.nexusmods.com/thehuntercallofthewild/mods/1138?tab=posts): reported distinction between store overhaul and direct legacy storage grants.
- [Official December 2017 announcement](https://store.steampowered.com/news/posts/?appids=518790&enddate=1513947146): Stradivarius community reward context.
- [Pinned Mod Builder name map](https://github.com/RyMaxim/cotw-mod-builder/blob/3ac2b0c8ea61c822f47bcdd6ad54f3ab7a65adeb/modbuilder/name_map.yaml): variant naming.
- [Pinned DECA ADF format implementation](https://github.com/RyMaxim/cotw-mod-builder/blob/3ac2b0c8ea61c822f47bcdd6ad54f3ab7a65adeb/deca/ff_adf.py): public type/instance layout reference.
- [Pinned public save parser](https://github.com/js-codewolke/COTW-Save-File-Editor/blob/659b2c1b4c7db0f18134dcf2582c710885b302c7/adf_parser.py) and [GUI backend](https://github.com/js-codewolke/COTW-Save-File-Editor/blob/659b2c1b4c7db0f18134dcf2582c710885b302c7/gui_backend.py): comparison material. That editor's mutation routines were not used; instance-relative offsets and dynamic-array shortening require particular care.

The weapon ID and exact tested schema were additionally verified against locally supplied mod data, embedded save schemas and controlled runtime observations. No proprietary data fixture is distributed. Public references establish context/format, while [TEST_NOTES.md](TEST_NOTES.md) states what the local experiment actually established.
