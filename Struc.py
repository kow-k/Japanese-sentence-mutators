# coding: utf-8

# Copyright (C) 2016-2018 Kow Kuroda
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re

def structure(cab):
    cablst=re.split(r'\n',cab)
    cid=0
    result=[]
    chunkpattern=re.compile('^\* (.*?) (.*?)(.) (.*?)\/(.*?)(?:\s|$)')
    for l in cablst:
        m=chunkpattern.match(l)
        if m != None :
            cid=int(m.group(1))
            chunk={'link':int(m.group(2)),
                   'head':int(m.group(4)),
                   'func':int(m.group(5)),
                   'deptype':m.group(3)}
            chunk['deps']=[]
            chunk['morphs']=[]
            chunk['surface']=''
            result.append(chunk)
        elif l != "EOS":
            line=re.split(r'\t',l)
            chunk['surface']+=line[0]
            result[cid]['morphs'].append(l)
    for i in range(len(result)):
        if result[i]['link']!= -1:
            result[result[i]['link']]['deps'].append(i)
    return result

def structure2str(structure):
    result=''
    for chunk in structure:
        for m in chunk['morphs']:
            line=re.split('\t',m)
            result+=line[0]
    return result
