#!/usr/bin/env python3
"""
Coverity Connect接続テストスクリプト
Windows環境での接続確認用
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from urllib.parse import urlparse

# .envファイルを読み込む
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✓ .envファイルを読み込みました: {env_path}")
except ImportError:
    print("⚠ python-dotenvがインストールされていません")
    print("  pip install python-dotenv を実行してください")

# ログ設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# プロジェクトのパスを追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))
sys.path.insert(0, str(project_root / 'src' / 'coverity_mcp_server'))

async def test_connection():
    """Coverity Connectへの接続をテスト"""
    
    print("=" * 60)
    print("Coverity Connect 接続テスト")
    print("=" * 60)
    
    # 1. 環境変数の確認
    print("\n[1] 環境変数の確認:")
    print("-" * 40)
    
    coverity_host = os.getenv('COVERITY_HOST', '')
    username = os.getenv('COVAUTHUSER', '')
    password = os.getenv('COVAUTHKEY', '')
    proxy_host = os.getenv('PROXY_HOST', 'bypsproxy.daikin.co.jp')
    proxy_port = os.getenv('PROXY_PORT', '3128')
    
    print(f"COVERITY_HOST: {coverity_host}")
    print(f"COVAUTHUSER: {username}")
    print(f"COVAUTHKEY: {'*' * 8 if password else 'NOT SET'}")
    print(f"Proxy: {proxy_host}:{proxy_port}")
    
    if not all([coverity_host, username, password]):
        print("\n❌ エラー: 必要な環境変数が設定されていません")
        print("\n以下のコマンドで設定してください:")
        print("set COVERITY_HOST=https://sast.kbit-repo.net")
        print("set COVAUTHUSER=your_username")
        print("set COVAUTHKEY=your_auth_key")
        return False
    
    # 2. プロキシ設定
    print("\n[2] プロキシ設定:")
    print("-" * 40)
    
    proxy_url = f"http://{proxy_host}:{proxy_port}"
    os.environ['HTTP_PROXY'] = proxy_url
    os.environ['HTTPS_PROXY'] = proxy_url
    os.environ['http_proxy'] = proxy_url
    os.environ['https_proxy'] = proxy_url
    
    print(f"HTTP_PROXY: {proxy_url}")
    print(f"HTTPS_PROXY: {proxy_url}")
    
    # 3. URL解析
    print("\n[3] URL解析:")
    print("-" * 40)
    
    try:
        if not coverity_host.startswith(('http://', 'https://')):
            coverity_host = f"https://{coverity_host}"
        
        parsed = urlparse(coverity_host)
        host = parsed.hostname or parsed.netloc.split(':')[0]
        port = parsed.port or (443 if parsed.scheme == 'https' else 8080)
        use_ssl = parsed.scheme == 'https'
        
        print(f"Host: {host}")
        print(f"Port: {port}")
        print(f"SSL: {use_ssl}")
        
    except Exception as e:
        print(f"❌ URL解析エラー: {e}")
        return False
    
    # 4. クライアント作成と接続テスト
    print("\n[4] Coverityクライアント接続テスト:")
    print("-" * 40)
    
    client = None
    try:
        # coverity_clientモジュールをインポート
        try:
            from coverity_mcp_server.coverity_client import CoverityClient
            print("✓ coverity_mcp_server.coverity_clientからインポート成功")
        except ImportError as e1:
            print(f"⚠ coverity_mcp_serverからのインポート失敗: {e1}")
            try:
                from src.coverity_mcp_server.coverity_client import CoverityClient
                print("✓ src.coverity_mcp_server.coverity_clientからインポート成功")
            except ImportError as e2:
                print(f"⚠ src.coverity_mcp_serverからのインポート失敗: {e2}")
                try:
                    from coverity_client import CoverityClient
                    print("✓ coverity_clientから直接インポート成功")
                except ImportError as e3:
                    print(f"❌ すべてのインポート試行が失敗しました")
                    print(f"  Error 1: {e1}")
                    print(f"  Error 2: {e2}")
                    print(f"  Error 3: {e3}")
                    print("\n現在のPythonパス:")
                    for p in sys.path[:5]:
                        print(f"  - {p}")
                    return False
        
        client = CoverityClient(
            host=host,
            port=port,
            use_ssl=use_ssl,
            username=username,
            password=password
        )
        
        print("✓ クライアント作成成功")
        
        # プロジェクト一覧を取得してテスト
        print("\n[5] API接続テスト (プロジェクト一覧取得):")
        print("-" * 40)
        
        projects = await client.get_projects()
        
        if projects:
            print(f"✓ 接続成功! {len(projects)}個のプロジェクトを取得")
            print("\nプロジェクト一覧:")
            for i, project in enumerate(projects[:5], 1):  # 最初の5個を表示
                name = project.get('projectName', project.get('projectKey', 'Unknown'))
                desc = project.get('description', '')
                print(f"  {i}. {name}")
                if desc:
                    print(f"     説明: {desc[:50]}...")
            
            if len(projects) > 5:
                print(f"  ... 他 {len(projects) - 5}個のプロジェクト")
            
            # ダミーデータかどうかを確認
            first_project = projects[0]
            if 'dummy' in str(first_project).lower() or 'test' in str(first_project).lower():
                print("\n⚠ 警告: ダミーデータが返されています")
                print("  実際のCoverityサーバーに接続できていない可能性があります")
            
            # ユーザー情報も取得してテスト
            print("\n[6] ユーザー情報取得テスト:")
            print("-" * 40)
            
            users = await client.get_users(limit=5)
            if users:
                print(f"✓ {len(users)}人のユーザーを取得")
                for user in users[:3]:
                    user_name = user.get('name', 'Unknown')
                    user_email = user.get('email', '')
                    print(f"  - {user_name}")
                    if user_email:
                        print(f"    Email: {user_email}")
                
                # ダミーデータかどうかを確認
                if users and 'dummy' in str(users[0]).lower():
                    print("\n⚠ 警告: ユーザーデータもダミーデータです")
            
            return True
        else:
            print("⚠ プロジェクトが見つかりませんでした")
            return False
        
    except Exception as e:
        print(f"❌ 接続エラー: {e}")
        logger.error("詳細なエラー情報:", exc_info=True)
        
        print("\n確認事項:")
        print("1. Coverityサーバーへのネットワーク接続")
        print("2. プロキシ設定（社内ネットワークの場合）")
        print("3. 認証情報の正確性")
        print("4. Coverityサーバーのアドレスとポート")
        
        # エラーの詳細を表示
        import traceback
        print("\n詳細なスタックトレース:")
        traceback.print_exc()
        
        return False
    
    finally:
        if client:
            await client.close()
            print("\n✓ クライアント接続をクローズしました")

async def main():
    """メイン処理"""
    success = await test_connection()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ テスト完了: 接続成功!")
    else:
        print("❌ テスト失敗: 接続できませんでした")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    # Windows環境でのイベントループポリシー設定
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\nテストを中断しました")
        sys.exit(1)
    except Exception as e:
        print(f"\n予期しないエラー: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)