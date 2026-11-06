import os, sqlite3, random, string, base64, io
from datetime import datetime, timedelta
from flask import Flask, render_template_string, jsonify, request, send_file
import qrcode

app = Flask(__name__)

BASE_DIR = os.environ.get('ANDROID_PRIVATE', os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'vpn.db')
CONFIGS_DIR = os.path.join(BASE_DIR, 'configs')
os.makedirs(CONFIGS_DIR, exist_ok=True)

_HERE = os.path.dirname(os.path.abspath(__file__))
_tpl_path = os.path.join(_HERE, 'template.html')
HTML_TEMPLATE = open(_tpl_path, encoding='utf-8').read() if os.path.exists(_tpl_path) else "<h1>template.html не найден</h1>"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_name TEXT NOT NULL, server TEXT NOT NULL, protocol TEXT NOT NULL,
        access_key TEXT NOT NULL, config_file TEXT,
        traffic_used REAL DEFAULT 0.0, traffic_limit REAL DEFAULT 50.0,
        ping_ms INTEGER DEFAULT 12, speed_mbps REAL DEFAULT 340.0,
        status TEXT DEFAULT 'DISCONNECTED', expires_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit(); conn.close()

init_db()


def get_real_traffic():
    try:
        if os.path.exists('/proc/net/dev'):
            with open('/proc/net/dev') as f:
                for line in f:
                    if any(x in line for x in ('wlan0','eth0','rmnet')):
                        p = line.split()
                        return round((int(p[1]) + int(p[9])) / (1024**3), 3)
    except Exception:
        pass
    return 0.38


def _gen_wg_keys():
    try:
        from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
        from cryptography.hazmat.primitives import serialization
        priv = X25519PrivateKey.generate()
        pb = priv.private_bytes(serialization.Encoding.Raw, serialization.PrivateFormat.Raw, serialization.NoEncryption())
        pub = priv.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        return base64.b64encode(pb).decode(), base64.b64encode(pub).decode()
    except Exception:
        return base64.b64encode(os.urandom(32)).decode(), base64.b64encode(os.urandom(32)).decode()


def generate_vpn_config(username, protocol, server):
    rs = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
    if protocol == 'WireGuard':
        priv, pub = _gen_wg_keys()
        ip = f"10.10.0.{random.randint(2,250)}"
        content = f"[Interface]\nPrivateKey = {priv}\nAddress = {ip}/32\nDNS = 1.1.1.1, 8.8.8.8\n\n[Peer]\nPublicKey = {pub}\nEndpoint = {server}.vpn.net:51820\nAllowedIPs = 0.0.0.0/0\nPersistentKeepalive = 25\n"
        fn = f"{username}_{server}.conf"
        open(os.path.join(CONFIGS_DIR, fn), 'w').write(content)
        return f"wireguard://config-{username}", fn
    elif protocol == 'VLESS':
        return f"vless://{rs}@{server}.vpn.net:443?encryption=none&security=reality&type=tcp&sni=cloudflare.com#VPN-{username}", None
    elif protocol == 'Trojan':
        return f"trojan://{rs}@{server}.vpn.net:8443?security=tls&sni=cloudflare.com#VPN-{username}", None
    elif protocol == 'OpenVPN':
        content = f"client\ndev tun\nproto udp\nremote {server}.vpn.net 1194\nresolv-retry infinite\nnobind\npersist-key\npersist-tun\nremote-cert-tls server\ncipher AES-256-GCM\nauth SHA256\n"
        fn = f"{username}_{server}.ovpn"
        open(os.path.join(CONFIGS_DIR, fn), 'w').write(content)
        return f"openvpn://config-{username}", fn
    else:
        raw = f"chacha20-poly1305:{rs}@{server}.vpn.net:8388"
        return f"ss://{base64.b64encode(raw.encode()).decode()}#VPN-{username}", None


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/keys', methods=['GET'])
def get_keys():
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("DELETE FROM keys WHERE expires_at < CURRENT_TIMESTAMP"); conn.commit()
    c.execute("SELECT id,user_name,server,protocol,access_key,config_file,traffic_used,traffic_limit,ping_ms,speed_mbps,status,expires_at FROM keys ORDER BY id DESC")
    rows = c.fetchall(); conn.close()
    keys = [{'id':r[0],'user_name':r[1],'server':r[2],'protocol':r[3],'access_key':r[4],'config_file':r[5],'traffic_used':r[6],'traffic_limit':r[7],'ping_ms':r[8],'speed_mbps':r[9],'status':r[10],'expires_at':r[11].split()[0] if r[11] else 'Бессрочно'} for r in rows]
    return jsonify({'keys': keys, 'system_traffic': get_real_traffic()})


@app.route('/api/keys', methods=['POST'])
def create_key():
    d = request.json or {}
    u, s, p = d.get('username','Client'), d.get('server','kazakhstan'), d.get('protocol','WireGuard')
    days = int(d.get('duration', 30))
    key, cf = generate_vpn_config(u, p, s)
    tu = round(random.uniform(0.01,0.3), 2)
    exp = (datetime.now()+timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
    metrics = {'kazakhstan':(random.randint(3,7),round(random.uniform(420,500),1)),'uzbekistan':(random.randint(8,14),round(random.uniform(350,420),1)),'russia':(random.randint(10,16),round(random.uniform(480,560),1)),'singapore':(random.randint(10,15),round(random.uniform(620,750),1)),'tokyo':(random.randint(13,18),round(random.uniform(500,600),1)),'frankfurt':(random.randint(16,22),round(random.uniform(700,850),1)),'amsterdam':(random.randint(18,25),round(random.uniform(750,900),1)),'london':(random.randint(20,28),round(random.uniform(680,780),1)),'istanbul':(random.randint(22,30),round(random.uniform(400,500),1)),'dubai':(random.randint(25,35),round(random.uniform(550,650),1)),'usa':(random.randint(35,48),round(random.uniform(800,950),1))}
    ping, speed = metrics.get(s, (12, 450.0))
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute("INSERT INTO keys (user_name,server,protocol,access_key,config_file,traffic_used,traffic_limit,ping_ms,speed_mbps,expires_at) VALUES (?,?,?,?,?,?,50.0,?,?,?)", (u,s,p,key,cf,tu,ping,speed,exp))
    conn.commit(); conn.close()
    return jsonify({"status":"success","key":key})


@app.route('/api/keys/<int:kid>', methods=['DELETE'])
def delete_key(kid):
    conn = sqlite3.connect(DB_PATH); c = conn.cursor()
    c.execute('DELETE FROM keys WHERE id=?', (kid,)); conn.commit(); conn.close()
    return jsonify({"status":"success"})


@app.route('/api/download/<filename>')
def download_config(filename):
    path = os.path.join(CONFIGS_DIR, filename)
    return send_file(path, as_attachment=True) if os.path.exists(path) else ("Файл не найден", 404)


@app.route('/api/qr')
def generate_qr():
    img = qrcode.make(request.args.get('text',''))
    buf = io.BytesIO(); img.save(buf, format='PNG'); buf.seek(0)
    return send_file(buf, mimetype='image/png')


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='127.0.0.1', port=port, debug=False)
