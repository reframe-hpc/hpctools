# call with: source ./mygps.py
# if interactive, uncomment: 
#uncomment: python
# import sys
# print(sys.version)
k=gdb.execute('cuda kernel', to_string=True)
g=gdb.execute('cuda grid', to_string=True)
b=gdb.execute('cuda block', to_string=True)
t=gdb.execute('cuda thread', to_string=True)
d=gdb.execute('cuda device', to_string=True)
s=gdb.execute('cuda sm', to_string=True)
w=gdb.execute('cuda warp', to_string=True)
l=gdb.execute('cuda lane', to_string=True)
print("{} {} {} {} {} {} {} {}\n".format(k.strip(), g.strip(), b.strip(), \
t.strip(), d.strip(), s.strip(), w.strip(), l.strip() ))
# print("{}{}".format(k[:-1], g))
#uncomment: end
