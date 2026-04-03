# 🔧 老肥工具箱 (FeiTools)

> 实用小工具合集，纯前端实现，开箱即用。

## 工具列表

| 工具 | 说明 |
|------|------|
| ⏱ 时间戳转换 | 时间戳与日期互转，支持秒/毫秒切换 |
| 📋 JSON 格式化 | 格式化、压缩、层级彩色高亮，文件导入导出 |
| 📱 二维码工具 | 生成/解析二维码，自定义样式配色 |
| ▶️ YouTube 下载 | 解析视频链接，下载视频/音频/封面，支持自建服务器 |
| ✨ Lora 提示词 | 中文描述自动翻译生成 Stable Diffusion 英文提示词 |
| 🎨 Pixiv 搜图 | 搜索 Pixiv 插画，标签筛选，瀑布流浏览 |

## 使用方式

直接用浏览器打开 `index.html` 即可，无需安装任何依赖。

YouTube 下载的自建服务器部署见 `server/` 目录。

## 项目结构

```
index.html              # 首页
tools/
  timestamp.html        # 时间戳转换
  json-formatter.html   # JSON 格式化
  qrcode.html           # 二维码工具
  youtube-dl.html       # YouTube 解析下载
  prompt-generator.html # Lora 提示词生成
  pixiv-search.html     # Pixiv 搜图
server/
  app.py                # YouTube 下载后端服务
  requirements.txt      # Python 依赖
```

## 免责声明

1. 本项目仅供个人学习和研究使用，请勿用于任何商业用途。
2. 本项目中的 YouTube 下载功能仅供用户下载自己拥有版权或已获得授权的内容。用户应自行遵守所在地区的法律法规及 YouTube 服务条款，因使用本工具产生的任何法律责任由用户自行承担。
3. 本项目中的 Pixiv 搜图功能通过公开 API 代理访问，不存储任何图片数据。所有图片版权归原作者所有，请尊重创作者权益。
4. 本项目不对任何第三方 API 或服务的可用性、准确性、安全性做任何保证。
5. 使用本项目即表示您已阅读并同意以上声明。因使用本项目造成的任何直接或间接损失，作者不承担任何责任。

## 开源协议

本项目基于 [MIT License](LICENSE) 开源。

```
MIT License

Copyright (c) 2025 liuqiaochi

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## 致谢

- [qrcode-generator](https://github.com/kazuhikoarase/qrcode-generator) - 二维码生成
- [jsQR](https://github.com/cozmo/jsQR) - 二维码解析
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - YouTube 视频下载
- [Cobalt](https://github.com/imputnet/cobalt) - 视频解析 API
