# call with: source ./thisfile.py
# if interactive, uncomment:
#uncomment: python
import re
txt=gdb.execute('info args', to_string=True)
regex = r'\s+clist = std::vector of length (\d+),'
res = re.findall(regex, txt)
gdb.execute('set $clist_len = %s' % res[0])
#uncomment: end
