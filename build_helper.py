import os
from flask import Flask, render_template_string

app = Flask(__name__)
TUNNEL_URL = "https://chronicles-home-vocabulary-soldiers.trycloudflare.com"

HTML_PAGE = f"""
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CyberStudio VPN Pro - APK Builder</title>
    <style>
        body {{ background: #03070f; color: #fff; font-family: sans-serif; text-align: center; padding: 40px 20px; }}
        .card {{ background: #111827; border: 1px solid #1f2937; border-radius: 12px; padding: 30px; max-width: 400px; margin: 0 auto; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }}
        h1 {{ color: #6366f1; font-size: 22px; margin-bottom: 10px; }}
        p {{ color: #9ca3af; font-size: 14px; margin-bottom: 25px; }}
        .btn {{ display: block; background: #6366f1; color: white; text-decoration: none; padding: 14px; border-radius: 8px; font-weight: bold; margin-bottom: 12px; }}
        .btn-alt {{ background: #374151; }}
    </style>
</head>
<body>
    <div class="card">
        <h1>CyberStudio VPN Pro</h1>
        <p>Ваша панель управления и сборка APK.</p>
        <a href="{TUNNEL_URL}" target="_blank" class="btn">Открыть VPN в браузере</a>
        <a href="https://www.pwabuilder.com/?url={TUNNEL_URL}" target="_blank" class="btn btn-alt">Снять ограничения и собрать APK</a>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

if __name__ == '__main__':
    print("Сервер запущен! Откройте в браузере: http://localhost:8080")
    app.run(host='0.0.0.0', port=8080)
