import os

path = r'D:\桌面\diyibanzhu\变形字体库v2'
os.chdir(path)

with open(r'变形字体库v2.txt', 'r', encoding='utf-8')as f:
    data = f.read()
dic = {}
for line in data.split('\n'):
    word, id = line.split(' ')
    dic[str(id)] = word

for path, dir, files in os.walk(path):
    for file in files:
        if file[-4:] == '.png':
            if file not in dic.keys():
                print(file)