# 迁移指南：从合并包到独立 Authoring 包

本文帮助你从原来的 `azure-ai-language-questionanswering` 合并包迁移到新的 **仅 Authoring** 包：`azure-ai-language-questionanswering-authoring`。

## 1. 为什么拆分
原包同时包含：
* 运行时 (Runtime / Query) 能力：对部署后的项目进行问答查询。
* Authoring 管理能力：创建/导入/导出/更新项目、知识源、QnA、同义词等。

很多用户只需要其中一类能力。拆分后：
* `azure-ai-language-questionanswering-authoring` 专注于项目管理（Authoring）。
* （未来）若需要查询，将使用运行时专用包或保留原包作为聚合层（视后续策略）。

## 2. 包名称与类名变化
| 原合并包 | 独立 Authoring 包 |
|----------|------------------|
| `azure.ai.language.questionanswering.authoring` 模块 | `azure.ai.language.questionanswering.authoring` (保持层级，安装包不同) |
| `AuthoringClient` | `QuestionAnsweringAuthoringClient` |
| Async: `AuthoringClient` (aio) | Async: `QuestionAnsweringAuthoringClient` (aio) |

> 注意：安装包名字变了（`-authoring` 后缀），导入路径保持语义一致，只是客户端类名更清晰明确。

## 3. 安装
```bash
pip uninstall azure-ai-language-questionanswering -y  # 如果之前安装过
pip install azure-ai-language-questionanswering-authoring --pre
```

或从源码（仓库根目录）：
```bash
pip install -e ./sdk/cognitivelanguage/azure-ai-language-questionanswering-authoring
```

## 4. 代码改动速查
典型旧代码：
```python
from azure.ai.language.questionanswering.authoring import AuthoringClient
client = AuthoringClient(endpoint, AzureKeyCredential(key))
```

迁移后：
```python
from azure.ai.language.questionanswering.authoring import QuestionAnsweringAuthoringClient
client = QuestionAnsweringAuthoringClient(endpoint, AzureKeyCredential(key))
```

异步：
```python
from azure.ai.language.questionanswering.authoring.aio import QuestionAnsweringAuthoringClient
```

## 5. API 差异
大多数方法名保持一致（`create_project`, `begin_update_sources`, `begin_update_qnas`, `begin_export`, `begin_import_assets`, `begin_deploy_project`, `list_*` 系列）。

目前没有移除 Authoring 功能；仅剔除了与运行时查询（`get_answers`/`query_text` 等）有关的内容。

## 6. 轮询与 LRO
长时间操作（导入、导出、部署、批量更新）仍通过 `begin_*` 前缀返回 poller：
```python
poller = client.begin_export(project_name, file_format="json")
result = poller.result()
```
在 Async 版本中使用 `await poller.result()`。

## 7. 依赖与 Python 版本
* Python: `>=3.9`
* 关键依赖：`azure-core`, `isodate`, `typing-extensions (Py<3.11)`
如果你原环境锁定在 3.8，需要升级后再安装。

## 8. 环境变量
| 变量 | 作用 |
|------|------|
| `AZURE_QUESTIONANSWERING_ENDPOINT` | 资源 Endpoint |
| `AZURE_QUESTIONANSWERING_KEY` | 访问密钥 |
| `AZURE_QUESTIONANSWERING_PROJECT` | 可选：现有项目名（导出/导入样例） |

## 9. 样例与测试
* 新包下的 `samples/authoring` 与 `async_samples` 保留纯 Authoring 示例。
* 测试夹具（fixtures）已裁剪，仅保留 Authoring 所需环境变量。

## 10. 回滚策略
如果需要运行时查询功能，在该独立包 GA 前仍可临时继续使用旧合并包（注意版本差异），或等待运行时独立包提供。

## 11. 已知事项 / 后续计划
* 运行时查询拆分包命名仍在规划。
* 若你使用 AAD（TokenCredential）鉴权，代码方式保持不变，只需替换客户端类名。
* 录制测试与 `assets.json` 暂未启用（仅在需要 live test 基础设施时引入）。

## 12. 遇到问题？
请在仓库提交 Issue，并附上：
* 旧/新包版本
* 调用示例代码
* 完整回溯（如有异常）

---
如需要再额外加入“运行时功能迁移”章节（当运行时包发布后），可追加补充。
