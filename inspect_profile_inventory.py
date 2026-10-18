"""Bounded read-only inventory decoder for workspace copies of current profiles."""
from pathlib import Path
import argparse, hashlib, json, struct, zlib
from inspect_save_schema import inspect

class Profile:
    def __init__(self,path):
        self.path=Path(path).resolve(strict=True)
        self.schema=inspect(self.path,True)
        if self.schema['wrapper_build']!=3331010 or self.schema['adf_version']!=4 or len(self.schema['instances'])!=1:raise ValueError('Unsupported current build/schema')
        self.instance=self.schema['instances'][0]
        if self.instance['type']!='PlayerProfileData_22':raise ValueError('Wrong profile type')
        self.raw=self.path.read_bytes();self.plain=zlib.decompress(self.raw[32:])
        self.base=self.schema['prefix_bytes']+self.instance['offset']
        self.data=self.plain[self.base:self.base+self.instance['size']]
        self.types=self.schema['types'];self.root=self.types[self.instance['type_hash']]
        self.fields={m['name']:m for m in self.root['members']}
    def get(self,fmt,offset):
        if offset<0 or offset+struct.calcsize(fmt)>len(self.data):raise ValueError('Outside current instance')
        return struct.unpack_from(fmt,self.data,offset)
    def array(self,type_hash,offset):
        typ=self.types[type_hash]
        if typ['kind']==4:count=typ['length'];start=offset
        elif typ['kind']==3:
            start,flags,count,pad=self.get('<4I',offset)
            if pad:raise ValueError('Unexpected pointer padding')
        else:raise ValueError('Expected fixed or dynamic array')
        element=typ['element_type'];width=4 if element==123620943 else self.types[element]['size']
        if count>4096 or start+count*width>len(self.data):raise ValueError('Array outside instance')
        return element,width,[start+i*width for i in range(count)]
    def u32array(self,field,base=0):
        element,width,positions=self.array(field['type_hash'],base+field['offset'])
        if element!=123620943 or width!=4:raise ValueError('Expected uint32 array')
        return [self.get('<I',p)[0] for p in positions],positions
    def slot_arrays(self,field,base=0):
        element,width,positions=self.array(field['type_hash'],base+field['offset'])
        typ=self.types[element]
        if typ['name']!='PPSlot_1' or width!=16 or len(typ['members'])!=1:raise ValueError('Unsupported slot type')
        return [self.u32array(typ['members'][0],p)[0] for p in positions]
    def report(self):
        names=['EquipmentUnlocked','EquipmentOwned','EquipmentAmount','EquipmentBackPack','VehicleEquipmentStorage','GivenDLCItems','UnlockedHuntClubEquipment']
        arrays={name:self.u32array(self.fields[name])[0] for name in names}
        owned=arrays['EquipmentOwned']
        if any(len(arrays[name])!=len(owned) for name in ['EquipmentAmount','EquipmentBackPack']):raise ValueError('Paired array length differs')
        rows=[dict(index=i,owned=value,owned_hex=f'{value:08x}',amount=arrays['EquipmentAmount'][i]) for i,value in enumerate(owned) if value or arrays['EquipmentAmount'][i]]
        li=self.fields['LoadoutInfo'];lt=self.types[li['type_hash']];lf={m['name']:m for m in lt['members']}
        element,width,positions=self.array(lf['LoadoutData']['type_hash'],li['offset']+lf['LoadoutData']['offset'])
        loadout_type=self.types[element];loadout_fields={m['name']:m for m in loadout_type['members']}
        if loadout_type['name']!='LoadoutData_1' or len(positions)>32:raise ValueError('Unsupported loadouts')
        loadouts=[]
        for index,base in enumerate(positions):
            row=dict(index=index)
            for name in ['LoadoutEquipment','LoadoutAllEquipment','LoadoutMissingItems']:
                row[name]=[dict(index=i,value=v) for i,v in enumerate(self.u32array(loadout_fields[name],base)[0]) if v]
            row['slots']=self.slot_arrays(loadout_fields['LoadoutEquipmentSlot'],base)
            loadouts.append(row)
        return dict(source=str(self.path),sha256=hashlib.sha256(self.raw).hexdigest(),wrapper_build=3331010,profile_type='PlayerProfileData_22',equipment_rows=rows,other_arrays={name:[dict(index=i,value=v) for i,v in enumerate(values) if v] for name,values in arrays.items() if name not in ['EquipmentOwned','EquipmentAmount']},inventory_slots=self.slot_arrays(self.fields['InventorySlot']),loadouts=loadouts,limitation='Owned/amount pairing requires validation; backpack is a separate ID list, not paired by index. No item identity inferred from numeric values alone.')

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('input');parser.add_argument('--output');args=parser.parse_args()
    report=Profile(args.input).report();text=json.dumps(report,indent=2)
    if args.output:
        output=Path(args.output).resolve();output.relative_to(Path(__file__).parent.resolve())
        if output.exists():raise ValueError('Refusing existing report')
        output.write_text(text,encoding='utf-8')
    else:print(text)
