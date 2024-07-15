# diyibanzhu

第一版主爬虫

## 使用方法

### 安装依赖

```
pip install -r requirements.txt
```

### 安装Node.js

全流程均选默认即可，具体步骤略。

安装完成后，需要配置相关环境：

1. 查看 node 模块全局路径：`npm -g root`
2. 在环境变量中添加 NODE_PATH 变量，值为上述 node 模块全局路径
3. 安装 jsdom：`npm -g install jsdom`

然后进入`utils\js混淆`目录下，尝试运行`node \test.js`和`python3 test.py`，如果不报错则说明执行JS的环境没问题了。

### 安装Chromium内核浏览器

比如Edge、Chrome，用于绕过Cloudflare的真人检测。

### 更改config.py

browser_path请修改为你电脑上Chromium内核浏览器的路径。

其他具体信息可看注释。

### 运行diyibanzhu.py

```python
# 下载一本小说
url = 'https://diyibanzhu.domain/{id_pre}/{id}/'
dd = DiyibanzhuDownloader(url)
dd.run()

# 下载全站小说
download_all_books()
```

## 反爬策略简析

### Cloudflare真人检测

以前我使用[curl_cffi](https://github.com/yifeikong/curl_cffi)来规避CF（原理是模拟Chrome的TLS指纹），但现在好像失效了。

所以我自己实现了一个能够绕过这个检测的方案，可见[iyzyi/cloudflare_bypass: Bypass Cloudflare human verification](https://github.com/iyzyi/cloudflare_bypass)

### 输入1234

需要输入1234后才能看到网页内容。

抓包，如果遇到这个检测页面就重放此包，并在cookies中保存PHPSESSID，后续就不会遇到这个页面了。

### JS混淆

采用`sojson.v5`对正文内容进行加密。

逆向难度较大，可以从网页内容中提取出密文和密钥，通过PyExecJS来执行`_ii_rr`函数，实现解密。

具体信息可见`utils\js混淆`。

### 字体重新渲染

网页中的i标签中的汉字，不是真正的汉字，而是通过`font.ttf`来实现自定义的字体渲染，把一个字显示成另一个字。

![](http://image.iyzyi.com/img/202405272228405.png)

通过上图软件手动建立映射关系。

具体信息可见`utils\i标签`。

### 图片文字

存在大量以图片形式显示的文字。

这个原理很简单，把所有图片都下载下来，然后手动或者OCR建立映射关系即可。

主要是图片很多，超级繁琐，我用c#简单写了个方便构建映射的UI。

![image-20240527223604280](http://image.iyzyi.com/img/202405272249357.png)

具体信息可见`utils\img标签`。

### 正文内容只给一部分

另一部分需要post一个数据包才能给出。那就post。

### AES 加密

从网页中提取密文、密钥和IV，解密即可。