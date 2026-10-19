"""Prepare a rifle-only new-character grant patch on a copy of Rookie Warden.

Python standard library only. Never overwrites input, deploys files, edits saves,
starts the game, or changes Steam settings. The property has no established public
name; its effect was identified by isolated fresh-character tests, not guessed.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

SOURCE_SHA256 = '00a489abf8c65f196e3959cd0a487d85c74bd182c8543383b72b7a64dd2886e6'
OUTPUT_SHA256 = '733ae0959b6c4f254c80328d7408530e6332cb808933f00df75ac4e3b6813edd'
ITEM_ID = 0x83A28D8E
ITEM_NAME = b'equipment_weapon_ba_rifle_270_03'
PROPERTY_ID = 0x3C814744


def prepare(source, output):
    source = Path(source).resolve(strict=True)
    output = Path(output).resolve()
    manifest_path = output.with_name(output.name + '.manifest.json')
    if output == source or manifest_path == source or output.exists() or manifest_path.exists():
        raise ValueError('Choose new output and manifest paths; existing files are never overwritten')
    if source.stat().st_size != 484432:
        raise ValueError('Unsupported equipment table size; original Rookie Warden v1.0.2 is required')
    raw = source.read_bytes()
    if hashlib.sha256(raw).hexdigest() != SOURCE_SHA256:
        raise ValueError('Unsupported equipment table hash; use an untouched copy of Rookie Warden v1.0.2')

    def read(fmt, at):
        if at < 0 or at + struct.calcsize(fmt) > len(raw):
            raise ValueError('RTPC bounds exceeded')
        return struct.unpack_from(fmt, raw, at)

    if raw[:4] != b'RTPC' or read('<I', 4)[0] != 2:
        raise ValueError('Expected RTPC v2')
    seen = set()
    matches = []

    def visit(at, depth=0):
        if at in seen or depth > 64:
            raise ValueError('RTPC cycle or excessive depth')
        seen.add(at)
        name, table, count, children = read('<IIHH', at)
        if name == ITEM_ID:
            props = {}
            for i in range(count):
                entry = table + 9 * i
                key, value, kind = read('<IIB', entry)
                if key in props and key != 0:
                    raise ValueError('Duplicate item property')
                props[key] = (value, kind, entry + 4)
            pointer, kind, _ = props[0xD31AB684]
            if kind != 3 or pointer >= len(raw):
                raise ValueError('Missing item name')
            end = raw.find(b'\0', pointer)
            if end < pointer or raw[pointer:end] != ITEM_NAME:
                raise ValueError('Item node/name mismatch')
            if props[0x33DF3B2F][:2] != (7000, 1) or props[0xB304F782][:2] != (6, 1):
                raise ValueError('Unexpected original price or lock mode')
            value, kind, field_at = props[PROPERTY_ID]
            if (value, kind) != (1, 1):
                raise ValueError('Unexpected original grant-related flag')
            matches.append(field_at)
        child_table = (table + count * 9 + 3) & ~3
        for i in range(children):
            visit(child_table + i * 12, depth + 1)

    visit(8)
    if len(matches) != 1:
        raise ValueError('Expected exactly one target item')
    field_at = matches[0]
    patched = bytearray(raw)
    struct.pack_into('<I', patched, field_at, 0)
    differences = [i for i, (a, b) in enumerate(zip(raw, patched)) if a != b]
    if differences != [field_at] or hashlib.sha256(patched).hexdigest() != OUTPUT_SHA256:
        raise ValueError('Unexpected output; only one validated flag byte may change')
    if source.read_bytes() != raw:
        raise ValueError('Source changed during preparation')
    manifest = dict(
        status='Prepared copy; deployment is separate',
        source_sha256=SOURCE_SHA256, output_sha256=OUTPUT_SHA256,
        target=ITEM_NAME.decode(), target_id=f'{ITEM_ID:08x}',
        property_id=f'{PROPERTY_ID:08x}', before=1, after=0,
        property_name='Public name unknown; isolated tests identify its grant-related effect',
        changed_bytes=1, all_other_bytes_unchanged=True,
        price_retained=7000, lock_mode_retained=6,
        reward_table_changed=False, save_files_changed=False,
        executable_changed=False, installed_files_changed=False,
        caveats=['Fresh characters only; existing ownership persists',
                 'Exact supplied Rookie Warden v1.0.2 table only',
                 'See TEST_NOTES.md for runtime coverage and limits'])
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('xb') as stream:
        stream.write(patched)
    with manifest_path.open('x', encoding='utf-8') as stream:
        json.dump(manifest, stream, indent=2)
        stream.write('\n')
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', help='Untouched Rookie Warden v1.0.2 equipment_data.bin copy')
    parser.add_argument('output', help='New output path; never an existing installed file')
    args = parser.parse_args()
    print(json.dumps(prepare(args.source, args.output), indent=2))
