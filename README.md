# WeGene 轻应用命令行工具 / WeGene WeApp CLI #

WeGene 的轻应用开发者可以通过本命令行工具生成、测试及打包基因轻应用。

## 安装 ##

```
pip install wegene-weapp-cli
```

## 版本 ##

由于 Python 2 的支持生命周期即将结束，自 `wegene-weapp-cli==0.9.9` 版本开始，`weapp-cli` 将只支持在 Python 3.6 或更高版本运行。同时，从该版本开始，本工具将支持使用 Python 3.6 或更高版本开发轻应用。需要注意的是，这只代表 `weapp-cli` 工具将不能在 Python 2 环境下运行，而我们依然会支持使用 Python 2.7 开发的轻应用一段时间以便平滑过渡。

如果您仍然在使用 Python 2.7，并且只需要开发 Python 2.7 下的轻应用，可以选择安装 `wegene-weapp-cli==0.2.1`。

## 更新扩展数据 ##

WeGene 目前为用户提供千万位点的扩展数据，并且轻应用中同样可以使用这部分位点。由于该部分数据较大，无法与安装包一同提供下载。为了保证您在生成测试数据时可以使用扩展数据，您可以在安装完本工具后执行以下命令下载额外的扩展数据以供未来使用：

```
weapp-cli download-extra
```

下载后，在您初始化应用时，如果位点列表包含扩展数据位点，该部分位点对应的数据也会被添加到模拟的测试数据集中。

## 使用 ##

### 生成轻应用脚手架工程 ###

命令行运行：

```
weapp-cli init
```

运行该命令后，通过交互界面，开发者可以生成一个轻应用的脚手架工程。工程文件夹内包括必要的代码文件、依赖以及供开发者本地测试使用的模拟测试数据。

```
Project Name [weapp-project]: // 输入你的轻应用工程名，会在当前文件夹下生成该名字的工程文件夹
Language to Use [python27]: // 轻应用使用的语言 [python27/python3/r]
Require Sex [y]: // 是否需要使用性别数据 [y/n]
Require Age [y]: // 是否需要使用年龄数据 [y/n]
Require Ancestry Composition [y]: // 是否需要使用祖源数据 [y/n]
Require Haplogroup [y]: // 是否需要使用单倍群数据 [y/n]
Require Haplotype [y]: // 是否需要使用基因单倍型数据 [y/n]
Require Whole Genome Data [y]: // 是否需要使用全部位点数据 [y/n]
RSID List File []: // 在不使用全部位点数据的情况下，需要的部分位点的列表文件路径（相对/绝对）。列表文件中应每行一个 RSID。
Output In Markdown Format [y]: // 是否以 Markdown 形式输出结果，如果是，在测试时会解析 Markdown 语法并生成模拟线上样式的 HTML 文件供参考。
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
