# rakuten-travel-api

## 〜修正する手順〜

* ローカルで修正
* githubにアップする
* ローカルのターミナルで"ssh reo@45.77.23.158"
* "cd src/rakuten-travel-api/" ソースのあるコードに移動
* "git pull" してgitから最新のコードを取得する
* "sudo python3 manage.py collectstatic"
* "sudo lsof -i:8000" でPIDの数字を
* "sudo kill -9 (PIDの数字)"で消す。
* "gunicorn --bind 127.0.0.1:8000 mysite.wsgi:application &"
* 上記文 "&"をつけることでバックグラウンドで走る。

エラーが出た場合、DEBUG = Trueにして原因を追求する。
## 〜permissionエラーの場合〜
* "/usr/share/nginx/html/media"を変えたい場合、
* 1つ前 "cd /usr/share/nginx/html/"に移動して
* "sudo chmod -R 777 media" でmedia のアクセス権限を全ユーザーに持たせる。
* "ll" で確認。光っていたらok
