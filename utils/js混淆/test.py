import execjs

# 如果没安装node，则会默认调用windows的JScript，会导致报错语法错误
# 安装node，并使用默认配置环境变量后，需要重启IDE
# print(execjs.get().name)
# https://www.cnblogs.com/xkdn/p/17186941.html


js_code = open(r"test.js", "r", encoding="utf-8").read() 
# npm root -g   查看全局 node_modules 的路径
ctx = execjs.compile(js_code)#, cwd=r"C:\Users\iyzyi\AppData\Roaming\npm\node_modules")

res = ctx.call("hello")
print(res)