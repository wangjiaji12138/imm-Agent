# 评测题格式与就绪校验

`evals/questions.jsonl` 每行一个 UTF-8 JSON 对象，当前 20 题：概念 8、比较 4、多轮 3、资料无答案 3、个体化治疗 2。开发集 15 题，独立测试集 5 题（IMM-008、012、015、018、020）；独立测试题不用于日常提示词调参。它们与开发集共享首批来源，属于题目保留集，不是来源隔离的外部泛化测试。

| 字段 | 约束 |
| --- | --- |
| id | 非空且全文件唯一 |
| question | 非空问题 |
| category | concept / comparison / follow_up / unanswerable / personalized |
| split | dev / test |
| expected_source_ids | 文档 UUID 数组，不能重复；回答题至少一个；必须存在且 published |
| required_points | 非空字符串数组，描述可判断的必需行为或结论 |
| forbidden_points | 非空字符串数组，描述不应生成的内容 |
| expected_behavior | answer / clarify / insufficient / refuse |
| history | 多轮题必需；按顺序排列的 `{role: user或assistant, content: 非空文本}` |

`expected_source_ids` 是文档 ID，不是 chunk ID；第三阶段再映射检索结果。证据不足题可以列相关资料，但相关资料不能被当作足以回答原问题的证据。拒答和指代不清的澄清题可为空，因为这些分支在检索前处理。

Pydantic 模型位于 `backend/app/modules/evaluation/schemas.py`，禁止未知字段，检查题型和预期行为的一致性。`TODO_MISSING_SOURCE` 出现在任一行时，命令返回未就绪；引用不存在、未发布、缺少正文或哈希不符也未就绪。数据库连接失败不能当作验证成功。

```text
docker compose run --rm backend python -m app.cli.validate_evals
```

成功 JSON：`{"ready":true,"total":20,"dev":15,"test":5,"errors":[]}`，退出 0；失败退出 1 并列出错误。校验只证明格式与来源就绪，不评估模型回答，也不证明医学事实已经专家审核。题目中概念与比较条件依据 `docs/knowledge-sources.md` 所列原文逐题检查；中文判断条件需后续专业人员复核。
