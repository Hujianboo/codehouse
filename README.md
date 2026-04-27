# codehouse

<p align="center">
  <strong>把 Codex 的 token 使用量盖成一座座城堡。</strong>
</p>

<pre align="center">
<span style="color:#c2410c">       |&gt;&gt;&gt;             |&gt;&gt;&gt;       </span>
<span style="color:#c2410c">       |                |          </span>
<span style="color:#d97706">    [__|__]          [__|__]       </span>
<span style="color:#d97706">    |  <span style="color:#facc15">[]</span> |__________| <span style="color:#facc15">[]</span>  |       </span>
<span style="color:#d97706">    |     |  <span style="color:#facc15">[]</span>  <span style="color:#facc15">[]</span>  |     |       </span>
<span style="color:#d97706">    |_____|__________|_____|       </span>
<span style="color:#92400e">    |#####|   ____   |#####|       </span>
<span style="color:#92400e">   /______|__|    |__|______\      </span>
<span style="color:#16a34a">  /____________________________\    </span>
<span style="color:#16a34a">       /_/              \_\        </span>
</pre>

`codehouse` 是一个 Codex 伴生 TUI。它会读取本机
`~/.codex/sessions/**/*.jsonl` 里的 `token_count` 事件，把当天的 token
使用量转换成一座座完成的城堡，以及一座正在施工的城堡。

当 Codex 写入新的 `token_count` 事件时，`codehouse` 不会直接跳到最终数字，
而是播放一段施工动画：地基、墙体、塔楼、旗帜、窗户、城门，然后变成完整城堡。

`codehouse` 不需要自己的数据库。每次启动都会从本地 Codex session 文件重新计算，
所以关掉再打开也能恢复当前状态。

## 功能亮点

- 默认视图：显示当天总 token，用完成城堡数和下一座城堡进度表示。
- Crew 视图：显示当前 Codex 父会话和它 spawned 出来的 subagents。
- All 视图：显示当天所有 worker/session 的城堡。
- 支持彩色 TUI、纯色模式、一次性快照、指定日期、不同城堡尺寸。
- 只依赖 Python 3 标准库。

## 安装

从 GitHub 一行安装：

```sh
curl -fsSL https://raw.githubusercontent.com/Hujianboo/codehouse/main/install.sh | sh
```

安装脚本会把 `codex_house.py` 下载到：

```sh
~/.local/share/codehouse/codex_house.py
```

并在 `~/.local/bin` 创建两个命令：

```sh
codehouse
codex-house
```

`codehouse` 是主命令。`codex-house` 只是为了兼容旧习惯保留的 alias。

如果 `~/.local/bin` 不在你的 `PATH` 里，安装脚本会询问是否自动写入当前 shell
配置文件，例如 `~/.zshrc`、`~/.bash_profile`、`~/.bashrc` 或 `~/.profile`。

如果你想在非交互安装时直接允许脚本写入 shell 配置，可以这样：

```sh
curl -fsSL https://raw.githubusercontent.com/Hujianboo/codehouse/main/install.sh | CODEHOUSE_UPDATE_PROFILE=1 sh
```

安装指定分支或 tag：

```sh
curl -fsSL https://raw.githubusercontent.com/Hujianboo/codehouse/main/install.sh | CODEHOUSE_REF=v0.1.0 sh
```

## 使用

打开实时 TUI：

```sh
codehouse
```

在 macOS 新 Terminal 窗口中打开：

```sh
codehouse --window
```

打印一次快照并退出：

```sh
codehouse --once
```

查看当前版本和 GitHub 上的最新版本：

```sh
codehouse -version
```

从 GitHub 更新到最新版：

```sh
codehouse -update
```

显示当前父会话和 subagents 的 crew 城堡：

```sh
codehouse -crew
codehouse -crew --once
```

显示当天所有 worker/session 城堡：

```sh
codehouse -all
codehouse -all --once
```

## 常用参数

```sh
codehouse --castle-tokens 500000
codehouse --scale large
codehouse --date 2026-04-27
codehouse --refresh 0.5
codehouse --seconds-per-castle 4
codehouse --pace slow
codehouse --no-color
codehouse --no-solid
codehouse -version
codehouse -update
```

完整帮助：

```sh
codehouse --help
```

## 视图说明

默认视图：

```sh
codehouse
```

显示指定日期的总 token 使用量，以及“已完成城堡 + 正在施工城堡”的进度。

Crew 视图：

```sh
codehouse -crew
```

显示当前 Codex crew。父会话显示为 `Main`；如果 Codex 在 session metadata 里记录了
subagent 的 nickname / role，`codehouse` 会把它展示出来。

All 视图：

```sh
codehouse -all
```

显示当天所有 worker/session 的城堡，包括不同时间启动的父会话。适合看全天活动，
而不是只看最新的父会话和 subagent 家族。

## 兼容命令

这些旧名字仍然可用：

```sh
codex-house
codehouse --crew
codehouse --agents
codehouse --all-agents
codehouse --all-castles
```

## 更新机制

`codehouse` 的安装脚本本身也是更新脚本。你可以随时重新运行：

```sh
curl -fsSL https://raw.githubusercontent.com/Hujianboo/codehouse/main/install.sh | sh
```

也可以直接运行：

```sh
codehouse -update
```

`codehouse -version` 会显示两个版本：

```text
codehouse local:  0.1.0
codehouse remote: 0.1.0
```

如果远程版本更新，它会提示：

```text
update available: run `codehouse -update`
```

版本号来自仓库根目录的 `VERSION` 文件。发布新版本时，更新 `VERSION` 后推送到
GitHub 即可。
