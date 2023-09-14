# Telegraph Image QT
- version: 1.0.0

![](icon/logo.png)

### 简介
- 本项目是基于[Telegraph-Image](https://github.com/cf-pages/Telegraph-Image)部署到[Cloundflare](https://dash.cloudflare.com/)后二次开发的一个QT客户端。
- 主要是想方便上传图片到Telegraph，并粘贴链接到剪贴板中，方便写笔记。

### 环境支持
- Python 3.6+
- PyQt5
- requests
- sqlite3
- re

### 安装
确保已安装上述的Python环境和库。然后，你可以直接从源代码运行应用。

#### Python环境和库安装
如果你尚未安装Python或所需的库，你可以按照以下步骤进行安装：

1. 下载并安装Python 3.6 或更高版本： [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. 在命令行中输入以下命令来一次性安装所有依赖库：

```bash
pip install PyQt5 requests
```

### 运行
在安装完所有必要的库之后，你可以通过执行以下操作来运行程序:
1. 打开命令行窗口（例如，Windows中的cmd或PowerShell）。
2. 切换到包含 `main.py` 的目录。
3. 输入 `python main.py` 后回车运行。

注意：
首次运行时需要设置API URL，以便程序向其发送图片上传请求。此URL保存在本地sqlite数据库中，供后续使用。

API URL格式要求:
- 正确例子：https://telegraph-image-6666.page.dev
- 错误例子：https://telegraph-image-6666.page.dev/  (请不要在最后加上`/`)

### 功能
1. 选择并上传图片文件(.png/.jpg/.gif/.jpeg)。
2. 从剪贴板复制的图片也可直接上传。
3. 提交图片后，将返回图像链接，并自动复制到剪贴板。
4. 支持不同的链接格式，包括URL，Markdown，HTML和UBB。
5. 可随时清除已上传的图片。

### 截图

![](https://telegraph-image-9gk.pages.dev/file/77dd1840fae31c48465cd.png)

界面比较简陋，但是功能还是挺全的。