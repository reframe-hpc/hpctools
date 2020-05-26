# call with: source ./thisfile.py
# if interactive, uncomment: 
#uncomment: python
import re
txt=gdb.execute('info cuda devices', to_string=True)
regex = r'\s+sm_\d+\s+(\d+)\s+'
res = re.findall(regex, txt)
gdb.execute('set $sm_max = %s' % res[0])
# print $sm_max
#uncomment: end
