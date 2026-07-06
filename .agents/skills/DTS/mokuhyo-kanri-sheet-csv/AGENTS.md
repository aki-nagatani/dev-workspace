# mokuhyo-kanri-sheet-csv

**人事考課_管理シート.md** と **同名 `.csv`** の併設・同期。手順の正本は **`SKILL.md`**。

- **正本**: `.md`。**ミラー**: `Work/社内業務/人事考課/人事考課_管理シート.csv`（UTF-8 BOM・1 行 = 1 枝番）
- **発火**: **`mokuhyo-excel-to-markdown`** / **`mokuhyo-draft`** / **`mokuhyo-proofread`** / **`mokuhyo-hojo-setteiji-comment`** が `.md` を変更した**同一セッション**
- **更新**: **`export_hr_kanri_sheet_to_csv.py`** で全量再生成（**既定**）。枝番の増減・並べ替え時は**必須**
- **CSV に含めない**: `<改善案>`（校閲メタは MD のみ）
- **逆同期**（CSV→MD）は本 SKILL の範囲外

Always respond in Japanese when applying this skill.
