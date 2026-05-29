# Recommendation Engine

GitHub の issue と commit 履歴から、チームメンバーのスキルを推定して会話やレビューに活かすための分析パッケージです。

このリポジトリでは、`github.md` に記載された履歴を正規化したうえで、メンバー別のスキルシグナル、要約、チャット用コンテキストを生成します。

## 使い方

```bash
python -m recommend_engine repository
python -m recommend_engine profile --member joeyprg45
python -m recommend_engine context --member joeyprg45 --question "この人の強みは？"
```

## 構成

- `src/recommend_engine/models.py`: データモデル
- `src/recommend_engine/demo_data.py`: 履歴データの定義
- `src/recommend_engine/analysis.py`: スキル推定ロジック
- `src/recommend_engine/chat_context.py`: Chat 用の文脈生成
- `src/recommend_engine/cli.py`: コマンドライン入口
