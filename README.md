# WeGene 轻应用命令行工具 / WeGene WeApp CLI #

WeGene 的轻应用开发者可以通过本命令行工具生成、测试及打包基因轻应用。

## 安装 ##

`pip install wegene-weapp-cli`

## 使用 ##

### 生成轻应用脚手架工程 ###

命令行运行：

```
weapp-cli init
```

运行该命令后，通过交互界面，开发者可以生成一个轻应用的脚手架工程。工程文件夹内包括必要的代码文件、依赖以及供开发者本地测试使用的模拟测试数据。

```
Project Name [weapp-project]: // 输入你的轻应用工程名，会在当前文件夹下生成该名字的工程文件夹
Language to Use [python27]: // 轻应用使用的语言 [python27/r]
Require Sex [y]: // 是否需要使用性别数据 [y/n]
Require Age [y]: // 是否需要使用年龄数据 [y/n]
Require Ancestry Composition [y]: // 是否需要使用祖源数据 [y/n]
Require Haplogroup [y]: // 是否需要使用单倍群数据 [y/n]
Require Whole Genome Data [y]: // 是否需要使用全部位点数据 [y/n]
RSID List File []: // 在不使用全部位点数据的情况下，需要的部分位点的列表文件路径（相对/绝对）。列表文件中应每行一个 RSID。
```

### 测试轻应用 ###

命令行运行：

```
cd weapp-project
weapp-cli test
```

通过运行该命令，CLI 工具将使用初始化应用时生成的测试数据对开发者开发的脚本进行测试，并抛出测试结果/异常。

### 打包轻应用 ###

命令行运行：

```
cd weapp-project
weapp-cli package
```

通过运行该命令，CLI 工具将会将该轻应用的工程打包为 `.zip` 文件，以便在界面创建应用时上传工程。

### 查看帮助 ###

```
weapp-cli --help
weapp-cli [command] --help
```
