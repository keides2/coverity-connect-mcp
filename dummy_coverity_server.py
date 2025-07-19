# このファイルは examples/development/mock_server.py に移動しました
# 
# 新しい場所:
# examples/development/mock_server.py
#
# 起動方法:
# python examples/development/mock_server.py
# または
# .\scripts\start_mock_server.bat
#
# このファイルは下位互換のため残していますが、
# 新しい場所のファイルを使用することを推奨します。

print("⚠️  このファイルは移動されました")
print("新しい場所: examples/development/mock_server.py")
print("起動方法: python examples/development/mock_server.py")
print()

# 新しいファイルを実行
import subprocess
import sys
import os

# プロジェクトルートを取得
project_root = os.path.dirname(os.path.abspath(__file__))
new_server_path = os.path.join(project_root, "examples", "development", "mock_server.py")

if os.path.exists(new_server_path):
    print(f"🚀 新しいサーバーを起動します: {new_server_path}")
    subprocess.run([sys.executable, new_server_path])
else:
    print(f"❌ 新しいファイルが見つかりません: {new_server_path}")
    print("プロジェクト構造を確認してください。")
