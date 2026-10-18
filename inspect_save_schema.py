"""Self-authored bounded read-only ADF schema inspector for retained save copies.

Does not import public editor code, write a save, or infer a teleport offset.
"""
from pathlib import Path
import argparse
import hashlib
import json
import re
import struct
import zlib

def inspect(path, include_types=False):
    path=Path(path).resolve(strict=True)
    workspace=Path(__file__).parent.resolve()
    path.relative_to(workspace)
    raw=path.read_bytes()
    if raw[:4]!=b'SAVE' or len(raw)>8*1024*1024:raise ValueError('Unsupported wrapper or size')
    inflater=zlib.decompressobj()
    plain=inflater.decompress(raw[32:],16*1024*1024)
    if not inflater.eof or inflater.unconsumed_tail or inflater.unused_data:raise ValueError('Unsupported compressed stream')
    prefix=0 if plain[:4]==b' FDA' else 5 if plain[5:9]==b' FDA' else None
    if prefix is None:raise ValueError('No supported ADF prefix')
    data=plain[prefix:]
    def get(fmt,offset):
        if offset<0 or offset+struct.calcsize(fmt)>len(data):raise ValueError('Read outside ADF')
        return struct.unpack_from(fmt,data,offset)
    header=get('<10I',4)
    version,ic,io,tc,to,sc,so,nc,no,total=header
    if version not in (3,4) or ic>20 or tc>5000 or nc>5000 or total>len(data):raise ValueError('Unsupported ADF bounds')
    lengths=get('<'+'B'*nc,no)
    names=[];cursor=no+nc
    for size in lengths:
        if cursor+size+1>len(data) or data[cursor+size]!=0:raise ValueError('Invalid name table')
        names.append(data[cursor:cursor+size].decode('utf-8'));cursor+=size+1
    types={};cursor=to
    for _ in range(tc):
        kind,size,align,th,ni,flags,element,length=get('<IIIIQIII',cursor);cursor+=36
        count=0
        if kind!=0:
            count=get('<I',cursor)[0];cursor+=4
        item=dict(name=names[ni],kind=kind,size=size,element_type=element,length=length,auxiliary_count=count,members=[])
        if count>5000:raise ValueError('Type extras too large')
        if kind==1:
            for __ in range(count):
                mi,mt,ms,packed,dt,dv=get('<QIIIIQ',cursor);cursor+=32
                item['members'].append(dict(name=names[mi],type_hash=mt,size=ms,offset=packed&0xffffff,bit_offset=packed>>24))
        elif kind==8:
            cursor+=count*12
            if cursor>len(data):raise ValueError('Enum outside ADF')
        elif count and kind not in (2,3):raise ValueError(f'Unsupported type extras: kind={kind}, name={item["name"]}, count={count}, table_cursor={cursor}')
        types[th]=item
    instances=[]
    for index in range(ic):
        nh,th,offset,size,ni=get('<IIIIQ',io+24*index)
        if offset+size>len(data):raise ValueError('Instance outside ADF')
        instances.append(dict(name=names[ni],type_hash=th,type=types.get(th,{}).get('name'),size=size,offset=offset))
    relevant=[]
    referenced={}
    def follow(type_hash,depth=0):
        if depth>12 or type_hash in referenced or type_hash not in types:return
        item=types[type_hash];referenced[type_hash]=item
        if item['element_type']:follow(item['element_type'],depth+1)
        for member in item['members']:follow(member['type_hash'],depth+1)
    for th,item in types.items():
        if any(re.search('(?i)pos|location|transform|reserve|rotation|spawn',m['name']) for m in item['members']):
            relevant.append(dict(type_hash=th,**item))
            for member in item['members']:
                if re.search('(?i)pos|location|transform|reserve|rotation|spawn',member['name']):follow(member['type_hash'])
    position_candidates=[]
    for instance in instances:
        root=types.get(instance['type_hash'],{})
        if root.get('name')!='PlayerInformationData_7':continue
        fields={m['name']:m for m in root['members']}
        if not all(n in fields for n in ('LastPlayerPositions','LastPlayerPositions_Memory')):continue
        base=instance['offset'];size=instance['size']
        def instance_get(fmt,relative):
            if relative<0 or relative+struct.calcsize(fmt)>size:raise ValueError('Position read outside instance')
            return get(fmt,base+relative)
        memory_type=types[fields['LastPlayerPositions_Memory']['type_hash']]
        memory_fields={m['name']:m for m in memory_type['members']}
        memory_offset=fields['LastPlayerPositions_Memory']['offset']
        chain_array_offset=memory_offset+memory_fields['ChainMemory']['offset']
        pointer,array_flags,count,padding_word=instance_get('<4I',chain_array_offset)
        if count>128 or pointer+count*24>size:raise ValueError(f'Unsupported position-chain memory: pointer={pointer}, flags={array_flags}, count={count}, padding_word={padding_word}, instance_size={size}')
        chain_array_type=types[memory_fields['ChainMemory']['type_hash']]
        chain_type=types[chain_array_type['element_type']]
        chain_fields={m['name']:m for m in chain_type['members']}
        if chain_type['size']!=24 or chain_fields['Key']['offset']!=0 or chain_fields['Value']['offset']!=12:raise ValueError('Unsupported position-chain layout')
        logical_offset=fields['LastPlayerPositions']['offset']
        logical_size=instance_get('<H',logical_offset+24)[0]
        entries=[]
        for index in range(count):
            entry=pointer+index*24
            key=instance_get('<Q',entry)[0]
            next_index=instance_get('<H',entry+8)[0]
            coordinates=instance_get('<3f',entry+12)
            entries.append(dict(memory_slot=index,key=key,next_index=next_index,xyz=coordinates,vector_offset_within_instance=entry+12))
        position_candidates.append(dict(instance_type=root['name'],logical_map_size=logical_size,memory_count=count,array_flags=array_flags,padding_word=padding_word,entries=entries,interpretation='Memory slots; active chains and reserve-key meanings not yet validated.'))
    result=dict(source=str(path),sha256=hashlib.sha256(raw).hexdigest(),wrapper_build=get_raw_u32(raw,4),prefix_bytes=prefix,adf_version=version,instances=instances,position_related_types=relevant,position_referenced_types=referenced,position_memory_candidates=position_candidates,names=[n for n in names if re.search('(?i)pos|location|transform|reserve|rotation|spawn',n)],limitation='Read-only schema and candidate position values; no save mutation or validated teleport established.')
    if include_types:result.update(types=types,all_names=names)
    return result

def get_raw_u32(raw,offset):return struct.unpack_from('<I',raw,offset)[0]

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('input');parser.add_argument('--output');parser.add_argument('--all-types',action='store_true');args=parser.parse_args()
    result=inspect(args.input,args.all_types);encoded=json.dumps(result,indent=2)
    if args.output:
        destination=Path(args.output).resolve();destination.relative_to(Path(__file__).parent.resolve())
        if destination.exists():raise ValueError('Refusing to replace prior evidence')
        destination.write_text(encoded,encoding='utf-8')
    else:print(encoded)
