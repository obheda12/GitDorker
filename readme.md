![logo](https://github.com/obheda12/GitDorker/raw/master/GitDorker.png)

# GitDorker
---
GitDorker是一个利用GitHub Search API和我从各种来源汇编的GitHub dork的广泛列表来提供给定搜索查询下github上存储的敏感信息的概述的工具。

GitDorker的主要目的是为用户提供一个干净且量身定制的攻击面，以开始在GitHub上收集敏感信息。
GitDorker可以与其他工具（例如GitRob或Trufflehog）一起使用在有趣的存储库上，或对GitDorker发现的用户进行使用，以产生最佳效果。

## 速度限制
---
GitDorker利用GitHub搜索API，每分钟最多只能进行30个请求。
为了防止速率限制，每30个请求后，GitDorker就会内置一个睡眠功能以防止搜索失败。
因此，如果要运行带有GitDorker的alldorks.txt文件，该过程大约需要5分钟才能完成。

## 配置要求
** Python3

** GitHub个人访问令牌

** 安装此存储库的requirements.txt文件中的需求（pip3 install -r requirements.txt）

如果你不确定如何产生一个个人访问令牌，请根据下述指导进行：https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token

## 建议
---
建议为GitDorker提供至少两个GitHub个人访问令牌，以便它可以在dorking过程中在两个GitHub个人访问令牌之间交替出现，并降低速率受限的可能性。
使用来自单独的GitHub帐户的多个令牌将提供最佳结果。

## Dorks
---
在dorks文件夹中是dork的列表。映射github秘密攻击面时，建议使用“alldorks.txt”文件。“alldorks.txt”是我从各种资源中提取的dork集合，总共有239个github敏感信息的个人dork。

## 使用
---
我创建了一个博客文章，其中更详细地介绍了如何使用GitDorker和潜在的用例：https://medium.com/@obheda12/gitdorker-a-new-tool-for-manual-github-dorking-and-easy-bug-bounty-wins-92a0a0a6b8d5

Help Output:
![Help](https://github.com/obheda12/GitDorker/raw/master/GitDorker%20Help.png)

## 屏幕截图
---
下面是一个运行查询“tesla.com”的结果示例，其中包含一个dorks小列表。

下述命令用于针对dorks列表查询“tesla.com”：
```
python3 GitDorker.py -tf TOKENSFILE -q tesla.com -d dorks/DORKFILE -o tesla
```
![Results](https://github.com/obheda12/GitDorker/raw/master/GitDorker%20Usage%20Example%20-%20Tesla.png)

Note：您输入的查询越高级（即合并用户，组织，端点信息等）您获得的结果将越简洁。

## 反馈
---
我乐于接受建议和批评。如果您认为该工具很烂或发现问题/错误，请告诉我并建议我如何对其进行改进  :)

## 感谢
---
创建GitDorker的参考
* [@gwendallecoguic](https://github.com/gwen001) - 特别感谢gwendall和他的脚本，这些脚本为我提供了创建GitDorker的框架。

## 免责声明
---
该项目仅用于教育和道德测试目的。未经事先双方同意，使用此工具攻击目标是非法的。开发人员对此工具不承担任何责任，也不对任何滥用或损坏负责。