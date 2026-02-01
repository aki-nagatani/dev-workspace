myrulesを厳守して作業してください

全リポジトリのファイルをコミット＆プッシュしてください
コミットメッセージの作成・確認・修正は `commit-message` SKILLを参照してください

直近の作業内容にかかわらず、差分があるファイルはすべてコミットすること
ただし、差分がないプロジェクトへのコミットはスキップしても構わない

FishTrack/MyPokedex/personal-tools/otayori-naviのコミット前に必ず、.githooks/pre-commitを実行し、テストをスキップしないでください
また、カバレッジ要件の無断での緩和も禁止とします
（pre-commitは「git commit」で自動実行されます、コマンドより個別で呼び出す必要はありません）
テストでエラーとなった場合は、原因究明を行ってください

ただし、pre-commit内で設定している、"mdの修正のみの場合はテストスキップ"などの条件に当てはまる場合は、
pre-commitの記述に沿ってテストをスキップしても構いません

テストエラーやカバレッジ不足などで、pre-commitが失敗した場合は、コミットせずに対応を行ってください
失敗の原因を確認し、その原因の解消を始めてください
カバレッジ不足が原因の場合、test-code-generatorのSKILLを呼び出してテストコードを生成し、カバレッジを改善してください

**🚨 絶対禁止: --no-verify によるコミットは厳禁です**
- いかなる理由があっても `git commit --no-verify` を使用してはなりません
- pre-commitが失敗した場合は、必ず原因を解消してからコミットしてください
- カバレッジ不足やテストエラーがある場合は、それらを解決してからコミットしてください
- 一時的な回避策として `--no-verify` を使用することは許可されません

FishTrackとMyPokedexのコミット先は「develop」ブランチです
「main」ブランチには適用しないでください
その他のプロジェクトは、mainリポジトリにコミットしてください

**🚨 otayori-naviのプッシュ後のGitHub Actions確認（必須・絶対にスキップ禁止）**:

otayori-naviのプッシュ時はCI/CDが実行されます。**必ず完了を待って結果を確認してください。**

**実行方法**: `github-actions-check` SKILLを参照して、GitHub Actionsの完了を待って結果を確認してください。
- SKILLの場所: `dev-workspace/.cursor/skills/github-actions-check/SKILL.md`
- リポジトリ: `aki-nagatani/otayori-navi`
- 確認対象: lint、test、deployジョブ

コミット時にコメント用の一時ファイルを作成した場合は削除してください