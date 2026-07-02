// 启动 localtunnel 隧道，patch TunnelCluster 让 net.connect 走 HTTP 代理 CONNECT
const fs = require('fs');
const net = require('net');
const path = require('path');

// Patch net.connect 让连外网的走代理 CONNECT
const PROXY_HOST = '127.0.0.1';
const PROXY_PORT = 18080;
const NO_PROXY_HOSTS = ['localhost', '127.0.0.1', '::1'];

function connectViaProxy(targetHost, targetPort, directOpts) {
  // 本地地址直连
  if (NO_PROXY_HOSTS.includes(targetHost)) {
    return net.connect(directOpts);
  }
  // 外网地址：先连代理，发 CONNECT，成功后透传
  const proxySock = net.connect({ host: PROXY_HOST, port: PROXY_PORT });
  let connected = false;
  proxySock.on('connect', () => {
    proxySock.write(`CONNECT ${targetHost}:${targetPort} HTTP/1.1\r\nHost: ${targetHost}:${targetPort}\r\n\r\n`);
  });
  let buf = Buffer.alloc(0);
  proxySock.on('data', (chunk) => {
    if (connected) return;
    buf = Buffer.concat([buf, chunk]);
    const headerEnd = buf.indexOf('\r\n\r\n');
    if (headerEnd === -1) return;
    const header = buf.slice(0, headerEnd).toString();
    if (!/^HTTP\/1\.[01] 200/.test(header)) {
      proxySock.emit('error', new Error(`Proxy CONNECT failed: ${header.split('\r\n')[0]}`));
      proxySock.destroy();
      return;
    }
    connected = true;
    // 透传剩余数据
    const rest = buf.slice(headerEnd + 4);
    if (rest.length) proxySock.emit('proxy-ready', rest);
    proxySock.emit('proxy-ready');
    // 把后续 data 监听交给原调用方：重新转发
  });
  // 重新实现 data 事件：建立后透传
  const origOn = proxySock.on.bind(proxySock);
  proxySock.on = function (ev, cb) {
    if (ev === 'data' && connected) {
      // 已经建立，直接监听
      return origOn(ev, cb);
    }
    if (ev === 'data') {
      // 在建立前注册的 data 监听，需要过滤掉 CONNECT 响应
      return origOn(ev, (chunk) => {
        if (connected) cb(chunk);
      });
    }
    return origOn(ev, cb);
  };
  return proxySock;
}

const origConnect = net.connect;
net.connect = function (...args) {
  let opts = args[0];
  if (typeof opts === 'object' && opts.host && opts.port) {
    return connectViaProxy(opts.host, opts.port, opts);
  }
  return origConnect.apply(this, args);
};

// axios 也走代理
const axios = require('axios');
const { HttpsProxyAgent } = require('https-proxy-agent');
const proxyAgent = new HttpsProxyAgent(`http://${PROXY_HOST}:${PROXY_PORT}`);
axios.defaults.httpsAgent = proxyAgent;
axios.defaults.httpAgent = proxyAgent;
axios.defaults.proxy = false;

const localtunnel = require('localtunnel');

function log(msg) {
  const line = new Date().toISOString() + ' ' + msg;
  fs.appendFileSync('/workspace/tunnel.log', line + '\n');
  process.stdout.write(line + '\n');
}

function startTunnel(port, name, subdomain) {
  return localtunnel({ port: port, subdomain: subdomain })
    .then(tunnel => {
      log(`${name}_URL=${tunnel.url}`);
      log(`${name}_PORT=${port}`);
      tunnel.on('close', () => log(`${name} tunnel closed`));
      tunnel.on('error', (e) => log(`${name} tunnel error: ${e.message}`));
      return tunnel;
    })
    .catch(e => {
      log(`${name} tunnel FAILED: ${e.message}`);
      throw e;
    });
}

(async () => {
  fs.writeFileSync('/workspace/tunnel.log', '');
  log('Starting tunnels via proxy CONNECT...');
  try {
    const timeout = setTimeout(() => {
      log('TIMEOUT: tunnels did not start in 40s');
      process.exit(2);
    }, 40000);

    await startTunnel(5173, 'FRONTEND', 'doctrfe');
    log('Frontend tunnel started, starting backend...');
    await startTunnel(5000, 'BACKEND', 'doctrbe');
    log('Both tunnels started successfully');
    clearTimeout(timeout);
    setInterval(() => {}, 60000);
  } catch(e) {
    log('FATAL: ' + e.message);
    process.exit(1);
  }
})();
