"""Prepare an output-only, exact-fixture Stradivarius cleanup experiment.

No live writes. Rejects equipped/loadout/vehicle references rather than trying
to delete dynamic-array elements. Current-build disposable fixture only.
"""
from pathlib import Path
import argparse, hashlib, json, struct, zlib
from inspect_profile_inventory import Profile

ROOT=Path(__file__).parent.resolve()
TARGET=2208468366  # 83a28d8e: exact equipment_data RTPC node + controlled transfer.

def prepare(source,output):
    source=Path(source).resolve(strict=True);source.relative_to(ROOT)
    output=Path(output).resolve();output.relative_to(ROOT)
    if output.exists() or output==source:raise ValueError('New workspace output required')
    profile=Profile(source);before=profile.report()
    owned,owned_at=profile.u32array(profile.fields['EquipmentOwned'])
    amount,amount_at=profile.u32array(profile.fields['EquipmentAmount'])
    backpack,backpack_at=profile.u32array(profile.fields['EquipmentBackPack'])
    owner=[i for i,v in enumerate(owned) if v==TARGET]
    carried=[i for i,v in enumerate(backpack) if v==TARGET]
    if len(owner)!=1 or amount[owner[0]]!=1 or len(carried)!=1:raise ValueError('Expected exactly one owned and carried rifle')
    if any(TARGET in values for values in before['inventory_slots']):raise ValueError('Unequip target in game before cleanup')
    for row in before['loadouts']:
        if any(any(v['value']==TARGET for v in row[name]) for name in ['LoadoutEquipment','LoadoutAllEquipment','LoadoutMissingItems']) or any(TARGET in values for values in row['slots']):raise ValueError('Remove target from saved loadouts in game first')
    if any(v['value']==TARGET for v in before['other_arrays']['VehicleEquipmentStorage']):raise ValueError('Remove target from vehicle first')
    # Fixed arrays stay length 1024. Never shift a paired ownership/quantity slot.
    changes=[('EquipmentOwned',owner[0],owned_at[owner[0]],TARGET),('EquipmentAmount',owner[0],amount_at[owner[0]],1),('EquipmentBackPack',carried[0],backpack_at[carried[0]],TARGET)]
    plain=bytearray(profile.plain);allowed=set()
    for name,index,relative,old in changes:
        at=profile.base+relative
        if struct.unpack_from('<I',plain,at)[0]!=old:raise ValueError('Unexpected typed source value')
        struct.pack_into('<I',plain,at,0);allowed.update(range(at,at+4))
    diff=[i for i,(a,b) in enumerate(zip(profile.plain,plain)) if a!=b]
    if len(plain)!=len(profile.plain) or any(i not in allowed for i in diff):raise ValueError('Change outside three allowlisted uint32 entries')
    if struct.unpack_from('<Q',profile.raw,8)[0]!=len(plain) or struct.unpack_from('<Q',profile.raw,24)[0]!=len(plain):raise ValueError('Unexpected wrapper lengths')
    wrapped=profile.raw[:32]+zlib.compress(plain)
    output.parent.mkdir(parents=True,exist_ok=True);output.write_bytes(wrapped)
    after_profile=Profile(output);after=after_profile.report()
    expected=json.loads(json.dumps(before));expected['equipment_rows']=[r for r in expected['equipment_rows'] if r['owned']!=TARGET]
    expected['other_arrays']['EquipmentBackPack']=[r for r in expected['other_arrays']['EquipmentBackPack'] if r['value']!=TARGET]
    for key in ['equipment_rows','other_arrays','inventory_slots','loadouts']:
        if expected[key]!=after[key]:raise ValueError('Output semantic diff differs from allowlist')
    if after_profile.raw[:32]!=profile.raw[:32] or after_profile.plain!=plain:raise ValueError('Wrapper/roundtrip mismatch')
    if hashlib.sha256(source.read_bytes()).hexdigest()!=before['sha256']:raise ValueError('Source changed')
    result=dict(status='EXPERIMENTAL COPY ONLY - runtime unverified',source=str(source),source_sha256=before['sha256'],output=str(output),output_sha256=after['sha256'],target_hex='83a28d8e',target_decimal=TARGET,identity_evidence=['Supplied equipment_data.bin RTPC node name equipment_weapon_ba_rifle_270_03','Only new backpack ID after user-confirmed Stradivarius transfer'],changes=[dict(field=n,index=i,before=v,after=0) for n,i,p,v in changes],changed_decompressed_bytes=len(diff),uncompressed_length_unchanged=True,all_other_payload_bytes_unchanged=True,original_source_unchanged=True,preserved=['WeaponData and statistics','EquipmentUnlocked','GivenDLCItems and all other grant records','All other equipment and quantities','Quests, cash, XP, level','All other save files'],limitations=['Existing target weapon history/cosmetic records intentionally retained','Fixed-array zero-slot tolerance and runtime re-grant behavior require disposable verification','No generalized compatibility or ownership provenance claimed'],live_deployment=False)
    output.with_name(output.name+'.manifest.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('source');parser.add_argument('output');args=parser.parse_args()
    print(json.dumps(prepare(args.source,args.output),indent=2))
