#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
プロジェクトファイル整理スクリプト
古いMDファイルをアーカイブし、最新状況に更新
"""
import os
import shutil
from datetime import datetime

def organize_files():
    """ファイルを整理"""
    
    print("=" * 70)
    print("プロジェクトファイル整理開始")
    print("=" * 70)
    print()
    
    # アーカイブディレクトリを作成
    archive_dir = "docs/archive"
    os.makedirs(archive_dir, exist_ok=True)
    print(f"✅ アーカイブディレクトリ作成: {archive_dir}")
    print()
    
    # アーカイブするファイル
    files_to_archive = [
        "WORK_SUMMARY_20251119.md",
        "WORK_SUMMARY_20251122.md"
    ]
    
    # 削除推奨ファイル（実際には削除せず、リストのみ作成）
    files_to_delete = [
        "DATA_COLLECTION_ROADMAP.md",
        "FAILED_PREDICTORS.md", 
        "NEXT_STEPS.md",
        "OPTION_A_GUIDE.md",
        "PLAYWRIGHT_MIGRATION.md"
    ]
    
    # アーカイブ処理
    print("📦 ファイルをアーカイブ中...")
    for filename in files_to_archive:
        if os.path.exists(filename):
            dest = os.path.join(archive_dir, filename)
            shutil.move(filename, dest)
            print(f"  ✅ {filename} -> {archive_dir}/")
        else:
            print(f"  ⚠️  {filename} が見つかりません")
    print()
    
    # 削除推奨リストを作成
    print("🗑️  削除推奨ファイルのリスト作成中...")
    delete_list_path = "docs/FILES_TO_DELETE.txt"
    with open(delete_list_path, 'w', encoding='utf-8') as f:
        f.write("# 削除推奨ファイルリスト\n")
        f.write(f"# 作成日: {datetime.now().strftime('%Y/%m/%d %H:%M:%S')}\n")
        f.write("# 以下のファイルは古い情報のため、削除を推奨します\n\n")
        
        for filename in files_to_delete:
            if os.path.exists(filename):
                f.write(f"{filename}\n")
                print(f"  📝 {filename} を削除推奨リストに追加")
            else:
                print(f"  ⚠️  {filename} が見つかりません")
    
    print(f"\n✅ 削除推奨リスト作成: {delete_list_path}")
    print()
    
    # 整理結果のサマリー
    print("=" * 70)
    print("整理完了サマリー")
    print("=" * 70)
    print(f"📦 アーカイブ済み: {len([f for f in files_to_archive if os.path.exists(os.path.join(archive_dir, f))])}件")
    print(f"🗑️  削除推奨: {len([f for f in files_to_delete if os.path.exists(f)])}件")
    print()
    print("次のステップ:")
    print("1. docs/FILES_TO_DELETE.txt を確認")
    print("2. 削除推奨ファイルを手動で削除")
    print("3. 最新版のドキュメントを確認")
    print("=" * 70)

if __name__ == "__main__":
    organize_files()
