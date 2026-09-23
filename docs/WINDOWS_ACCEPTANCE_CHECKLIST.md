# Windows 验收清单

## 构建

- [ ] `scripts/run-tests.ps1` 全部通过
- [ ] VS2022 Release x64 编译无错误
- [ ] VS2022 Release x86 编译无错误
- [ ] DLL 只依赖系统组件和同目录 `rime.dll`
- [ ] 生成并保存 SHA-256

## 安装/注册

- [ ] 全新安装成功
- [ ] 重复安装成功
- [ ] 覆盖升级成功
- [ ] 普通用户触发 UAC 后成功
- [ ] Win+Space 可见“应物输入法”
- [ ] 注销/登录后仍可见
- [ ] 卸载后两个 COM 注册视图均清理
- [ ] 用户缓存默认保留，`-PurgeUserData` 可清理

## 输入

- [ ] 单字全拼、结构码、部首码
- [ ] 2、3、4、5、6—12 字词组
- [ ] 一级、二级歧义后缀
- [ ] Space/Enter/1—9 上屏
- [ ] Up/Down/PageUp/PageDown
- [ ] Backspace/Delete/Esc
- [ ] 切换窗口和切换输入法无残留
- [ ] Ctrl/Alt/Win 快捷键不被误吞

## 应用矩阵

- [ ] Windows Notepad
- [ ] Word 64 位
- [ ] 至少一个 32 位应用
- [ ] Edge/Chrome
- [ ] Notion 或 VS Code（Electron）
- [ ] Windows Terminal
- [ ] RDP 场景

## 视觉和稳定性

- [ ] 100%、125%、150%、200% DPI
- [ ] 多显示器与负坐标屏幕
- [ ] 浅色/深色/高对比度
- [ ] 连续 12 小时输入无崩溃
- [ ] 首次词典编译有可接受等待时间

## 发布

- [ ] 代码签名和时间戳
- [ ] 安装包签名
- [ ] SBOM
- [ ] 第三方许可证复核
- [ ] 隐私说明
- [ ] 回滚方案
