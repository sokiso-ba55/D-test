# AWS POC

## プロジェクト概要

メンバー管理システムのWebアプリケーションです。ログイン機能付きで、メンバーの一覧表示、詳細表示、追加、編集が可能です。

### 主な機能
- ユーザー認証（ログイン/ログアウト）
- メンバー一覧表示
- メンバー詳細表示
- メンバー情報編集
- メンバー追加

### 技術スタック
- **バックエンド**: Python + Flask
- **データベース**: MySQL
- **フロントエンド**: HTML + CSS
- **認証**: セッション管理

## ローカル環境でのセットアップ

### 前提条件
- Python 3.7以上
- MySQL 5.7以上
- pip

### 1. リポジトリのクローン
```bash
git clone <repository-url>
cd daihatsu-poc
```

### 2. 仮想環境の作成とアクティベート
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate     # Windows
```

### 3. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 4. データベースのセットアップ
```bash
# MySQLにログイン
mysql -u root -p

# データベースとテーブルの作成
CREATE DATABASE daihatsu_poc;
USE daihatsu_poc;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
);

CREATE TABLE members (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL
);

# サンプルユーザーの作成（パスワードは平文）
INSERT INTO users (username, password) VALUES ('admin', 'admin123');
```

### 5. 環境変数の設定
プロジェクトルートに `.env` ファイルを作成：
```env
SECRET_KEY=your-secret-key-here
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your-mysql-password
MYSQL_DB=daihatsu_poc
```

### 6. アプリケーションの起動
```bash
python run.py
```

アプリケーションは `http://localhost:5000` でアクセス可能です。

### 7. 初期ログイン情報
- ユーザー名: `admin`
- パスワード: `admin123`

## プロジェクト構造
```
daihatsu-poc/
├── app/
│   ├── __init__.py          # Flaskアプリケーションの初期化
│   ├── routes.py            # ルーティング定義
│   ├── templates/           # HTMLテンプレート
│   │   ├── base.html
│   │   ├── login.html
│   │   ├── members.html
│   │   ├── member_detail.html
│   │   ├── member_edit.html
│   │   └── member_add.html
│   └── static/
│       └── style.css        # CSSスタイル
├── requirements.txt         # Python依存関係
├── run.py                  # アプリケーション起動スクリプト
└── readme.md              # このファイル
```

## AWS移行計画

### Phase 1: インフラストラクチャの準備
1. **VPCの設定**
   - パブリックサブネット（EC2用）
   - プライベートサブネット（RDS用）
   - セキュリティグループの設定

2. **RDS（MySQL）の構築**
   - プライベートサブネットに配置
   - マルチAZ構成（本番環境）
   - バックアップ設定

3. **EC2インスタンスの準備**
   - Amazon Linux 2 または Ubuntu
   - パブリックサブネットに配置
   - セキュリティグループでHTTP/HTTPS/SSHを許可

### Phase 2: アプリケーションのデプロイ
1. **EC2インスタンスのセットアップ**
   ```bash
   # システムの更新
   sudo yum update -y  # Amazon Linux 2
   # または
   sudo apt update && sudo apt upgrade -y  # Ubuntu

   # Python、MySQLクライアント、その他必要なパッケージのインストール
   sudo yum install python3 python3-pip mysql -y
   ```

2. **アプリケーションの配置**
   ```bash
   # アプリケーションのクローン
   git clone <repository-url>
   cd daihatsu-poc

   # 仮想環境の作成
   python3 -m venv venv
   source venv/bin/activate

   # 依存関係のインストール
   pip install -r requirements.txt
   ```

3. **環境変数の設定**
   ```bash
   # .envファイルの作成
   cat > .env << EOF
   SECRET_KEY=your-production-secret-key
   MYSQL_HOST=your-rds-endpoint
   MYSQL_USER=your-rds-username
   MYSQL_PASSWORD=your-rds-password
   MYSQL_DB=daihatsu_poc
   EOF
   ```

   **SECRET_KEYについて**
   - このアプリケーションはFlaskのセッション管理を使用しているため、SECRET_KEYは必須です
   - SECRET_KEYはセッションデータの暗号化とセキュリティに使用されます
   - 本番環境では、強力でランダムなSECRET_KEYを生成して使用してください

   **本番環境でのSECRET_KEY生成方法**
   ```bash
   # 強力なSECRET_KEYの生成（32バイトのランダムな16進数文字列）
   python3 -c "import secrets; print(secrets.token_hex(32))"
   
   # または、より長いSECRET_KEYを生成する場合
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

   **セキュリティ上の注意事項**
   - SECRET_KEYは絶対にバージョン管理システム（Git）にコミットしないでください
   - 本番環境では、デフォルト値（'devkey'）を使用しないでください
   - 定期的にSECRET_KEYを更新することを推奨します
   - 環境ごとに異なるSECRET_KEYを使用してください
   ```

4. **データベースの移行**
   ```bash
   # ローカルからデータベース構造とデータをエクスポート
   mysqldump -u root -p daihatsu_poc > daihatsu_poc.sql

   # RDSにインポート
   mysql -h your-rds-endpoint -u your-username -p daihatsu_poc < daihatsu_poc.sql
   ```

### Phase 3: 本番環境の設定
1. **Gunicornの設定**
   ```bash
   # Gunicornのインストール
   pip install gunicorn

   # systemdサービスの作成
   sudo nano /etc/systemd/system/daihatsu-poc.service
   ```

   ```ini
   [Unit]
   Description=Daihatsu POC Flask App
   After=network.target

   [Service]
   User=ec2-user
   WorkingDirectory=/home/ec2-user/daihatsu-poc
   Environment="PATH=/home/ec2-user/daihatsu-poc/venv/bin"
   ExecStart=/home/ec2-user/daihatsu-poc/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 run:app
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

2. **Nginxの設定**
   ```bash
   # Nginxのインストール
   sudo yum install nginx -y

   # 設定ファイルの作成
   sudo nano /etc/nginx/conf.d/daihatsu-poc.conf
   ```

   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       }
   }
   ```

3. **サービスの起動**
   ```bash
   # サービスの有効化と起動
   sudo systemctl enable daihatsu-poc
   sudo systemctl start daihatsu-poc
   sudo systemctl enable nginx
   sudo systemctl start nginx
   ```

### Phase 4: セキュリティと運用
1. **SSL/TLS証明書の設定**
   - Let's EncryptまたはAWS Certificate Managerを使用
   - HTTPS通信の強制

2. **監視とログ**
   - CloudWatchでのログ監視
   - アラートの設定

3. **バックアップ戦略**
   - RDSの自動バックアップ
   - アプリケーションデータの定期バックアップ

4. **セキュリティ強化**
   - セキュリティグループの最小権限原則
   - IAMロールの適切な設定
   - パスワードのハッシュ化実装

### Phase 5: CI/CDパイプライン（オプション）
1. **GitHub ActionsまたはAWS CodePipelineの設定**
2. **自動テストの実装**
3. **自動デプロイメントの設定**

## トラブルシューティング

### よくある問題
1. **データベース接続エラー**
   - 環境変数の確認
   - RDSのセキュリティグループ設定
   - ネットワーク接続の確認

2. **アプリケーションが起動しない**
   - ログの確認: `sudo journalctl -u daihatsu-poc`
   - ポートの確認: `netstat -tlnp | grep 8000`

3. **静的ファイルが表示されない**
   - Nginxの設定確認
   - ファイルパーミッションの確認

## 開発者向け情報

### 開発環境でのデバッグ
```bash
# デバッグモードで起動
export FLASK_ENV=development
python run.py
```

### データベースのリセット
```bash
mysql -u root -p
DROP DATABASE daihatsu_poc;
CREATE DATABASE daihatsu_poc;
# テーブル作成スクリプトを再実行
```

## ライセンス
このプロジェクトは内部使用のためのPOCです。
