![PPMessage Demo](/ppmessage/doc/ppkefu-ppcom.gif)

[In English](/README.md)

# PPMessage Lite Server - 皮皮消息，即插即用，纯Python实现。

PPMessage Lite Server 是配合 PPMessage 在线服务[https://ppmessage.com] 提供的一个精简版的开源沟通平台，PPMessage Lite Server 能够在服务器接口级别与 PPMessage SaaS 服务兼容，其目标为开发者提供一个可以本地部署的测试开发平台。

PPMessage Lite Server 建议部署到 macOS 上，其次 Debian Linux，再其次选择 Windows。

PPConfig 用来辅助生成运行所需的配置信息，配置信息保存在 ppmessge/bootstrap/config.json，如果想重新配置，只需要把这个文件删除，再运行 main.py。


## 快速上手

### 下载代码

```bash
git clone https://github.com/PPMESSAGE/ppmessage
cd ppmessage
```

### 安装依赖

> Debian/Ubuntu

```bash
bash ppmessage/scripts/set-up-ppmessage-on-linux.sh
```

> 为啥没有 CentOS 的安装脚本？ 没啥为什么，就是懒... ^_^

> macOS


```bash
bash ppmessage/scripts/set-up-mac-on-linux.sh
```


### 执行


```bash
./main.py
```
> 删除文件 ppmessage/bootstrap/config.json，再运行 main.py 就可以重新配置。

> 就是这些，不工作？请将日志贴到 Github issue 中，谢谢！

 
> 完全参考手册，请关注 PPMessage 在 GitBook 上的持续更新

* [中文手册](https://ppmessage.gitbooks.io/ppbook/content/)


> 应网友之强烈要求，要有个 QQ 群 348015072


![](/ppmessage/doc/348015072.png)


## 版权 

> 使用前请仔细阅读版权声明。

本项目的源代码是按照 Apache License Version 2 开源的，其版权归属于原作者，并且只允许在单网站或者单应用和单客服上使用 PPMessage 及其衍生项目，如果想利用 PPMessage 的全部或者部分代码提供多租户（多站点）服务，请联系作者获取商业许可。

[Apache License Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)

Copyright (c) 2010-2017, PPMESSAGE team and contributors - https://www.ppmessage.com and https://github.com/PPMESSAGE/ppmessage

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.



## 其他项目

* [PPCom iOS SDK](https://github.com/PPMESSAGE/ppcom-ios-sdk)

* [PPCom Android SDK](https://github.com/PPMESSAGE/ppcom-android-sdk)
