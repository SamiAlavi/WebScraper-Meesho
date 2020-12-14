# -*- coding: utf-8 -*-

from os import listdir

files = [i for i in listdir()if i.endswith('.csv') ]
for file in files:
  with open(file,'r',encoding='utf8') as f:
    lines = f.read()
    lines = lines.split('\n')
    for line in lines:
      cols = line.split(';')
      desc = cols[-1].split('~')
      cols = cols[:-1]
      print(cols)
      print(desc)
      print()
