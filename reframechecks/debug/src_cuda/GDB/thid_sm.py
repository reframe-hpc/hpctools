# call with: source ./thisfile.py
# if interactive, uncomment: 
#uncomment: python
import re
import sys
print(sys.version)
# --------------------
#  (105,0,0) (120,0,0) (105,0,0) (127,0,0) 8 0x000000000102c650 ./density.cu 24
#                                 ^^^
# +set logging off
# --------------------
txt=gdb.execute('info cuda threads', to_string=True)
# regex = r'(?>\(\S+\)\s+){3}\((\d+),\d+,\d+\).*\n\+set logging off'
# '(?>' : ko with python2
regex = r'(\(\S+\)\s+){3}\((\d+),\d+,\d+\)'
res = re.findall(regex, txt[-256:])
# print("res=", res, type(res))
res_i = int(res[0][1])
gdb.execute('set $threadmax_block = %s' % res_i)
#uncomment: end
