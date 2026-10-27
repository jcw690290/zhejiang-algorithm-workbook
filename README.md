# 浙江选考算法专题练习册

> 本项目为个人整理的非官方练习册，已在 GitHub 公开以便查阅、做题与反馈。原仓库贡献者对原解析、题图和真题转载范围的进一步确认尚未收到；公开只表示项目所有者的意愿，不等于已获得第三方材料的转载授权。如权利人提出异议，将按 [NOTICE.md](NOTICE.md) 缩小或移除相应内容。

面向浙江信息技术选考的单文件静态练习册。覆盖 2023 年 1 月至 2026 年 6 月的 8 次非学考考试，每次第 10、11、12、15 题，共 32 题、17 个交叉专题。

## 使用

下载本仓库（Code → Download ZIP），解压后双击 `index.html`。无需安装 Node.js 即可阅读和做题。

- 主页提供从专题开始、从年份开始、配置 AI、全部真题和待复习入口。
- 选择题核对答案，非选择题记录草稿；答案、仓库原解析与新增教学解析分别展示。
- 17 题附逐步执行示例；题图内嵌，可离线使用，可打印筛选后的题目。
- 可选的自备 API 助教：OpenRouter、DeepSeek 预设及自定义兼容接口。密钥和对话不写入本地存储；刷新即清空。
- 做题记录、复习标记和草稿保存在当前浏览器。不同设备和不同网页来源之间不会自动同步。

AI 需要联网并使用自己的密钥，受服务商计费、额度与跨域策略约束。配置方法见 [AI使用说明.md](AI使用说明.md)。切换供应商会清除旧密钥，任何密钥都不应提交到 Git 仓库。

## 安卓 APK

不想解压文件夹、希望在手机上直接做题，可以安装打包好的 APK：

[**下载 zhejiang-algorithm-workbook-1.0.apk**](https://github.com/jcw690290/zhejiang-algorithm-workbook/releases/download/v1.0/zhejiang-algorithm-workbook-1.0.apk)

- 版本 1.0，约 601 KB，Android 5.0（API 21）及以上。
- 全部 32 道题、题干配图和两层解析都打包在应用内，**不联网也能做题**。
- 首次安装需允许「安装未知来源应用」；浏览器提示「此类文件可能有害」属于未上架应用商店的常规提示。
- 校验：SHA-256 `1a84ed1abffe15809cfeec45dddd093c37885c8074b0b7dc6ff64d9644ba4e7b`，MD5 `9210bd6c13c82b918ea0f435951be168`，APK Signature Scheme v1/v2/v3 均已签名。
- 应用内页面由 `https://appassets.local/` 这个虚拟源提供资产，所以内置 AI 助教发请求时 Origin 不是 `null`，与网页版行为一致；仍受服务商跨域策略约束。

发布页见 [Releases](https://github.com/jcw690290/zhejiang-algorithm-workbook/releases/tag/v1.0)。

## 开发与构建

需要 Node.js 22.12 或更高版本。

```sh
npm install
npm run build
```

生成根目录的 `index.html`，它包含全部题目数据、图片、样式和脚本。

| 文件 | 用途 |
| --- | --- |
| `template.html` | 主页、题目阅读、筛选、作答与打印界面 |
| `ai-panel.html`、`ai.js` | 可选 AI 配置及对话 |
| `data.json` | 32 题的题干、来源、分类、答案、两类解析和内嵌图片；构建的内容来源 |
| `traces.json` | 逐步执行演示数据 |
| `notes.md` | 本次新增教学解析的编辑底稿；修改后需同步到 `data.json` 才会参与构建 |
| `build.mjs` | 将 Markdown 和各组件打包成单文件 |
| `verify_algorithms.py` | 算法核对，重建演示数据与核对报告 |
| `test-ai.mjs`、`test-home.mjs` | 浏览器功能测试，API 采用模拟响应 |

## 验证

```sh
npx playwright install chromium
npm test
python verify_algorithms.py
```

浏览器测试共 28 项检查，包含主页导航、年份筛选、供应商预设、请求参数、会话隔离、取消与超时、密钥不落盘、移动布局等。算法脚本包含 37 项独立核对。浏览器测试没有真实调用收费模型，不能证明服务商实时可用或一定支持浏览器跨域。

如果希望测试本机已安装的 Edge，可设置环境变量 `TEST_BROWSER_CHANNEL=msedge`。测试截图写入忽略提交的 `artifacts/`。

## 来源、许可与校勘

题目和仓库原解析来自 [sjxun/zhejiang-it-algorithm-exam](https://gitee.com/sjxun/zhejiang-it-algorithm-exam)，采用版本 `0f866ebfad0f4b2c4c9c7519a19c7c1bb4f65f09`。本项目不是官方试题发布平台，也不代表原作者对新增解析或 AI 回答的认可。

保留上游 [Mulan PSL v2 全文](LICENSE)及[来源与权利范围说明](NOTICE.md)。页面实现与本项目新增的软件代码按该许可证提供；题干、截图、配图、引用解析等第三方材料保留原权利，不能仅凭本项目的软件许可证推定其另行授权。

专题参考用户提供的对应表，并补齐 6 道未映射题目；两处题干不符的表格分类已修正。仓库原文与新增教学说明分开展示，发现的笔误和边界问题在页面中注明。

## 安卓应用

APK 已经发布（见上文「安卓 APK」）。工程源码不在本仓库内：它只做三件事——用一个只含 `INTERNET` 权限的 `WebView` 承载练习册，把所有请求拦截回 `assets/index.html`，以及把非 `appassets.local` 的链接交给系统浏览器。v1.0 APK 内置的是发布时的页面快照。仓库中的 `index.html` 后续更新（包括本次教学解析修订）不会自动进入已发布的 APK；使用新版解析请下载仓库最新版 HTML，安卓安装包需要重新打包发布后才会更新。

尚未制作 PWA。APK 不改变 AI 的联网需求：不填密钥时应用完全离线可用，填了才联网，且仍受服务商计费、额度与跨域策略约束。
