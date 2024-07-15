import struct

with open(r'D:\桌面\diyibanzhu-update\utils\i标签\手动输入.txt', 'r', encoding='utf-8')as f:
    data = f.read().split('\n')

output = ''
for i in range(0, 100):
    if len(hex(i)[2:]) == 1:
        index = '0' + hex(i)[2:]
    else:
        index = hex(i)[2:]
    output += "\\ue8%2s\t%s\n" % (index, data[i])

with open(r'D:\桌面\diyibanzhu-update\utils\i标签\字体反爬库.txt', 'w', encoding='utf-8')as f:
    f.write(output)