# 东方财富妙想 Skills 安装指南

配套 UZI-Skill 的可选增强：安装东财妙想 skill 集合，并配置 `MX_APIKEY`。  
UZI 主链路只需 key（见仓库根目录 `.env.example`）；本指南覆盖 **OpenClaw / ClawHub 侧 skill 包** 的安装与校验。

## 前提条件

- Node.js ≥ 22
- 有效的 `MX_APIKEY`（免费获取：https://dl.dfcfs.com/m/itc4）
- HTTP 请求 Header 须携带 `apikey` 认证

```bash
# 检查 Node.js
if ! command -v node &> /dev/null; then
  echo "错误：未安装 Node.js。请先安装 Node.js 22 或以上版本。"
  exit 1
fi
```

## 安装步骤

### 1. 清理旧版本

删除下列目录下以 `mx-skills` 开头的旧技能，避免版本冲突：

```bash
rm -rf ~/.openclaw/skills/mx-skills*
rm -rf ~/.openclaw/workspace/skills/mx-skills*
rm -rf ~/.openclaw/workspace/agent/skills/mx-skills*
rm -rf ~/mx-skills*
rm -rf ~/mx-data*
rm -rf ~/mx-search*
rm -rf ~/mx-xuangu*
rm -rf ~/mx-zixuan*
rm -rf ~/mx-moni*
echo "✅ 已清理旧版本的妙想技能目录。"
```

### 2. 确定安装目录

使用「官方技能（ClawHub 预装）安装路径」或「当前 ClawHub skills 全局共享目录」。后续 zip 均解压到该目录。

### 3. 下载并解压妙想 Skill

解压后目录结构示例：

```
~/skills/
├── mx-data/      # 金融数据
├── mx-search/    # 资讯搜索
├── mx-xuangu/    # 智能选股
├── mx-zixuan/    # 自选股管理
└── mx-moni/      # 模拟组合
```

| Skill | 下载 |
|---|---|
| 金融数据 | https://marketing.dfcfw.com/res/download/A620260331IHX67H.zip |
| 资讯搜索 | https://marketing.dfcfw.com/res/download/A620260331K5WDTK.zip |
| 智能选股 | https://marketing.dfcfw.com/res/download/A620260331NXBVEY.zip |
| 自选股管理 | https://marketing.dfcfw.com/res/download/A6202603314TMGR1.zip |
| 模拟组合 | https://marketing.dfcfw.com/res/download/A620260402S10QIM.zip |

### 4. 设置 API 密钥

在妙想 Skills 页面获取 apikey，会话级设置（默认不改 shell 启动文件）：

```bash
if [ -z "$MX_APIKEY" ]; then
  echo "⚠️ 未检测到环境变量 MX_APIKEY。"
  read -p "请输入您的 API Key: " input_key
  if [ -n "$input_key" ]; then
    export MX_APIKEY="$input_key"
    echo "✅ API Key 已临时设置（当前会话有效）。"
  else
    echo "❌ 输入为空，安装终止。"
    exit 1
  fi
else
  echo "✅ 检测到环境变量 MX_APIKEY，正在使用..."
fi
```

UZI-Skill 也可把 key 写入仓库根目录 `.env`（见 `.env.example`）。

### 5. 验证

```bash
test -f ~/mx-data/SKILL.md && echo "mx-data OK" || echo "mx-data MISSING"
test -f ~/mx-search/SKILL.md && echo "mx-search OK" || echo "mx-search MISSING"
test -f ~/mx-xuangu/SKILL.md && echo "mx-xuangu OK" || echo "mx-xuangu MISSING"
test -f ~/mx-zixuan/SKILL.md && echo "mx-zixuan OK" || echo "mx-zixuan MISSING"
test -f ~/mx-moni/SKILL.md && echo "mx-moni OK" || echo "mx-moni MISSING"
echo "MX_APIKEY=${MX_APIKEY:+is set}"
```

> 路径以你在第 2 步选定的 skills 根目录为准；若解压到 ClawHub 共享目录，请把 `~/mx-*` 换成实际路径。
