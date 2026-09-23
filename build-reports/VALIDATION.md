# 本地验证记录

日期：2026-09-22

## 已完成

### 1. 词典算法与运行时数据

- Python 3.13.14
- `python -m unittest discover -s tests -v`
- 8 项测试全部通过
- 覆盖：批准示例、仅残余分支追加第二码、一级对照、唯一词组、长度前缀碰撞、方案静态设置、词典格式和关键行数

### 2. 可重复构建

使用源码包内四份数据快照，从零生成：

- `hengma.dict.yaml`
- `hengma_fuzzy.dict.yaml`
- `hengma_phrases.dict.yaml`

三份结果与 `data/` 内运行时文件逐字节一致。

### 3. PowerShell 语法

- PowerShell 7.6.6 AST Parser
- 6 个 `.ps1` 文件（后新增 `rebuild-data.ps1` 后共 6 个）均无解析错误
- 该检查只验证语法，不替代 Windows 管理员/UAC、文件复制和 `regsvr32` 行为测试

### 4. Windows C++ 目标编译

工具：llvm-mingw 20260922，Clang 23.1.2。

- x64：所有 `.cpp` 翻译单元通过语法编译
- x86：所有 `.cpp` 翻译单元通过语法编译
- x64：完整链接为 PE32+ DLL
- x86：完整链接为 PE32 DLL
- 导入表不含 `rime.dll`；运行时按安装目录绝对路径显式加载
- 两个测试 DLL 均导出：
  - `DllCanUnloadNow`
  - `DllGetClassObject`
  - `DllRegisterServer`
  - `DllUnregisterServer`

交叉测试 DLL依赖 llvm-mingw 运行库，仅用于工程验证，未纳入交付包，也不作为可安装版本。

## 尚未完成

- Visual Studio 2022/MSVC 的 CMake 构建；
- Windows 10/11 上的 COM/TSF 注册；
- Notepad、Office、浏览器、Electron、32 位应用的输入测试；
- 首次 librime 词典部署耗时和异常路径；
- 代码签名、安装包签名、SmartScreen 信誉；
- 长时间稳定性、辅助功能和安全测试。

所以当前结论是“源码和双架构链接已验证”，不是“Windows 输入法已完成运行验收”。
