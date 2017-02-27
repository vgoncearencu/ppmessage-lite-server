
<!-- Customer             |  Service -->
<!-- :-------------------------:|:-------------------------: -->
<!-- ![](doc/ppcom.gif)  | ![](doc/ppkefu.gif) -->

<img src="doc/ppkefu-ppcom.gif" height=400px></img>


# PPMessage Lite Server

With [PPMessage](https://ppmessage.com), you can chat with customer via Web or mobile App.

PPMessage Lite Server targets to help [PPMessage](https://ppmessage.com) developer to deploy a test server on local machine. It could run on Linux, macOS and even **Windows** operating systems, and compatible with the [SaaS serivce](https://ppmessage.com) on interface level. It means Web or Mobile App integrated with `PPMessage Lite Server` can smoothly work with PPMessage Online SaaS service with minor changes (different key).


## EASY START

> Clone

```bash
git clone https://github.com/PPMESSAGE/ppmessage-lite-server.git
cd ppmessage
```

> Under Debian/Ubuntu


```bash
bash ppmessage/scripts/set-up-ppmessage-on-linux.sh
```

> Under macOS


```bash
bash ppmessage/scripts/set-up-ppmessage-on-mac.sh
```

> Under Windows


Check [this](doc/en-us/install-ppmessage-on-windows.md)



```bash
./config.py --email=your_login_email_address --password=your_login_password
```

```bash
./lite.py
```

> Access


```bash
Open your browser and visit `http://127.0.0.1:8945` with `your_login_email_address` and `your_login_password` to login.

```

> Reconfig PPMessage, just remove the file `ppmessage/bootstrap/config.json` and run `config.py` again.


> Not working yet? Please fire an issue on Github, thanks. Enjoy!

## DOCUMENTS

> Read following document to use and develop. Check More details on [PPMessage Site](https://ppmessage.com).

* [Complete english manual](https://ppmessage.gitbooks.io/ppbook-en/content/)


## LICENSE 

> Please read license carefully, you can use PPMessage Lite Server freely under the license.

PPMessage Lite Server target to be used as testing and developing. So that only one service user and one domain (including one web site and one app) only, if needs more than one domain deployment you needs contact the author to get commercial permission.

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


## OTHER LANGUAGES

[In Chinese 中文版](doc/zh-cn/README.md)


## OTHER PROJECTS

* [PPMessage Lite Server](https://github.com/PPMESSAGE/ppmessage-lite-server)

* [PPCom iOS SDK](https://github.com/PPMESSAGE/ppcom-ios-sdk)

* [PPCom Android SDK](https://github.com/PPMESSAGE/ppcom-android-sdk)
