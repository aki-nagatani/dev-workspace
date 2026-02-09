#!/bin/bash
# 本番RDSのテーブル一覧を取得
# 実行: EC2上で、おたよりナビ・MyPokedex・FishTrack のいずれかのアプリコンテナから実行
#
# 例（MyPokedex EC2）:
#   aws ssm start-session --target i-023a1623e48cabf1d --region ap-northeast-1
#   cd /home/ec2-user/MyPokedex && docker exec mypokedex-app-1 python -c '
# from mypokedex import createApp
# from mypokedex.extensions import db
# from sqlalchemy import text
# app = createApp()
# with app.app_context():
#     for row in db.session.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = chr(39)||chr(112)||chr(117)||chr(98)||chr(108)||chr(105)||chr(99) ORDER BY tablename")):
#         print(row[0])
# '
#
# 例（おたよりナビ EC2、OTAYORI_NAVI_EC2_HOST を確認して接続）:
#   cd /home/ec2-user/otayori-navi && docker compose exec -T app python -c "
# from otayori_navi.config import load_config
# from sqlalchemy import create_engine, text
# cfg = load_config('/app/config.yaml')
# engine = create_engine(cfg.db.url)
# with engine.connect() as conn:
#     for row in conn.execute(text(\"SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename\")):
#         print(row[0])
# "
echo "Usage: Connect to EC2 via Session Manager, then run the Python command in comments above."
