# sprite-gen

生成 12 张布偶猫 sprite 给 claude-pet 用。调用 Gemini 2.5 Image（俗称 Nano Banana），基于参考照片做角色一致的多 pose 生成。

## 一次性准备

```bash
cd projects/claude-pet/sprite-gen
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# 然后编辑 .env，把 GEMINI_API_KEY 填进去
```

把 10+ 张你布偶的照片丢到 `refs/`（jpg / png / webp / heic 都行）。不同角度、姿势、光线越多越好。

## 生成

```bash
python generate.py             # 生成全部 12 张
python generate.py walk_01     # 只生成一张
python generate.py walk_01 walk_02 walk_03 walk_04   # 一组
python generate.py --list      # 看支持的状态名
```

输出在 `out/`。

## 12 张清单

`walk_01..04` · `idle_01..02` · `sleep_01..02` · `sit` · `alert` · `happy` · `sad`

详细 pose 描述在 [prompts/states.yaml](prompts/states.yaml)，风格通用 prompt 在 [prompts/base.md](prompts/base.md)。

## 迭代

如果某张不像你的猫 / 姿势不对：
1. 改对应状态在 `states.yaml` 里的 pose 描述
2. 重跑 `python generate.py <state_name>` 覆盖

成本预估：每张 ~$0.04，12 张约 $0.5，加迭代 30 张总共约 $1-2。
