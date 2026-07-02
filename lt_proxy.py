"""
localtunnel 客户端 - 通过 HTTP 代理连接
实现 localtunnel 协议：建立到服务器的连接，双向转发到本地服务
"""
import socket
import threading
import requests
import time
import sys
import json

PROXY_HOST = '127.0.0.1'
PROXY_PORT = 18080
LT_SERVER = '193.34.76.44'  # localtunnel.me 的 IP
LT_API = 'https://localtunnel.me'

# 代理用于 API 请求
PROXIES = {'http': f'http://{PROXY_HOST}:{PROXY_PORT}', 'https': f'http://{PROXY_HOST}:{PROXY_PORT}'}


def log(msg):
    line = f'[{time.strftime("%H:%M:%S")}] {msg}'
    print(line, flush=True)


def get_tunnel_info(subdomain):
    """获取 localtunnel tunnel 信息"""
    url = f'{LT_API}/{subdomain}'
    r = requests.get(url, proxies=PROXIES, timeout=20)
    return r.json()


def connect_via_proxy(target_host, target_port):
    """通过 HTTP 代理 CONNECT 建立到目标的 TCP 连接"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(30)
    sock.connect((PROXY_HOST, PROXY_PORT))
    # 发送 CONNECT 请求
    connect_req = f'CONNECT {target_host}:{target_port} HTTP/1.1\r\nHost: {target_host}:{target_port}\r\n\r\n'
    sock.sendall(connect_req.encode())
    # 读取响应
    buf = b''
    while b'\r\n\r\n' not in buf:
        data = sock.recv(4096)
        if not data:
            raise ConnectionError('代理连接断开')
        buf += data
    header = buf.split(b'\r\n\r\n')[0].decode(errors='ignore')
    if ' 200 ' not in header.split('\r\n')[0]:
        raise ConnectionError(f'代理 CONNECT 失败: {header.split(chr(13))[0]}')
    return sock


def pipe(src, dst):
    """双向转发数据"""
    try:
        while True:
            data = src.recv(65536)
            if not data:
                break
            dst.sendall(data)
    except Exception:
        pass
    finally:
        try: src.close()
        except: pass
        try: dst.close()
        except: pass


def serve_tunnel(remote_port, local_port, name):
    """建立一条隧道连接并转发到本地服务"""
    while True:
        try:
            log(f'{name}: 连接到 {LT_SERVER}:{remote_port} 经代理...')
            remote_sock = connect_via_proxy(LT_SERVER, remote_port)
            remote_sock.settimeout(None)
            log(f'{name}: 服务器连接已建立')

            # 连接本地服务
            local_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            local_sock.connect(('127.0.0.1', local_port))
            local_sock.settimeout(None)
            log(f'{name}: 本地服务 {local_port} 已连接')

            # 双向转发
            t1 = threading.Thread(target=pipe, args=(remote_sock, local_sock), daemon=True)
            t2 = threading.Thread(target=pipe, args=(local_sock, remote_sock), daemon=True)
            t1.start()
            t2.start()
            t1.join()
            t2.join()
            log(f'{name}: 连接结束，重连...')
        except Exception as e:
            log(f'{name}: 错误 {e}，2秒后重连')
            time.sleep(2)


def start_tunnel(local_port, name, subdomain):
    """启动一个 localtunnel 隧道"""
    info = get_tunnel_info(subdomain)
    log(f'{name}: 获取到 tunnel 信息: {json.dumps(info)}')
    remote_port = info['port']
    max_conn = info.get('max_conn_count', 2)
    url = info['url']
    log(f'{name}: 公网 URL = {url}')
    log(f'{name}: remote_port={remote_port}, max_conn={max_conn}')

    # 启动多条连接
    for i in range(max_conn):
        t = threading.Thread(target=serve_tunnel, args=(remote_port, local_port, f'{name}-{i}'), daemon=True)
        t.start()
        time.sleep(0.5)

    return url


if __name__ == '__main__':
    local_port = int(sys.argv[1]) if len(sys.argv) > 1 else 5173
    name = sys.argv[2] if len(sys.argv) > 2 else 'TUNNEL'
    subdomain = sys.argv[3] if len(sys.argv) > 3 else 'doctrfe'

    url = start_tunnel(local_port, name, subdomain)
    print(f'\n{"="*60}')
    print(f'  公网 URL: {url}')
    print(f'  本地端口: {local_port}')
    print(f'{"="*60}\n')

    # 保持运行
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        log('退出')
