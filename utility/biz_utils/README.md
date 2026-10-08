打开当前路径
open .

权限
chmod 755 adb

git配置
git config --global user.name [your name]
git config --global user.email [company email]

克隆仓库
git clone git@gitlab.alibaba-inc.com:lingxiADC/adc-sc.git

切换分支
cd adc-sc && git checkout feature/dev_0219_2024

AirtestIDE adb覆盖
cp adb /Applications/AirtestIDE.app/Contents/MacOS/airtest/core/android/static/adb/mac/adb 

安装homebrew
/bin/bash -c "$(curl -fsSL https://gitee.com/ineo6/homebrew-install/raw/master/install.sh)"

安装python
brew install python@3.9
python3 --version
pip3 --version

软连接
brew unlink python@3.9 && brew link python@3.9 

安装模块
pip3 install -U airtest oss2 pocoui paddleocr paddlepaddle pillow numpy opencv-python future six pycryptodome swig

投屏
scrcpy -s localhost:9999 -b 120M --always-on-top

write_name=f"{single_counter()}"

app_will_get_runloop_count  设定重试次数

# 新建项目
```shell
cd ~/adc-sc
game=2416_common
mkdir -p ${game}/${game}_index.air
mkdir -p ${game}/${game}_fabu.air
touch ${game}/${game}_index.air/${game}_index.py
touch ${game}/${game}_fabu.air/${game}_fabu.py
```

# vscode添加包路径
设置 -> Analysis: Extra Paths
```
"python.analysis.extraPaths": [
  "/Users/vip/adc-sc/utility/adc_request.air",
  "/Users/vip/adc-sc/utility/adc_tools.air",
  "/Users/vip/adc-sc/utility/api.air",
  "/Users/vip/adc-sc/utility/application.air",
  "/Users/vip/adc-sc/utility/biz_foundation.air",
  "/Users/vip/adc-sc/utility/biz_utils.air",
  "/Users/vip/adc-sc/utility/dwarf.air",
  "/Users/vip/adc-sc/utility/files.air",
  "/Users/vip/adc-sc/utility/game_property.air",
  "/Users/vip/adc-sc/utility/image.air",
  "/Users/vip/adc-sc/utility/lingxi_platform.air",
  "/Users/vip/adc-sc/utility/lxplatform_start.air",
  "/Users/vip/adc-sc/utility/lxplatform.air",
  "/Users/vip/adc-sc/utility/mask.air",
  "/Users/vip/adc-sc/utility/monitor.air",
  "/Users/vip/adc-sc/utility/ocr.air",
  "/Users/vip/adc-sc/utility/oppo_platform.air",
  "/Users/vip/adc-sc/utility/phase.air",
  "/Users/vip/adc-sc/utility/resource",
  "/Users/vip/adc-sc/utility/security.air",
  "/Users/vip/adc-sc/utility/status_check.air",
  "/Users/vip/adc-sc/utility/swipe.air",
  "/Users/vip/adc-sc/utility/tool_kit.air",
  "/Users/vip/adc-sc/utility/upload.air",
  "/Users/vip/adc-sc/utility/xiaomi_platform.air"
]
```