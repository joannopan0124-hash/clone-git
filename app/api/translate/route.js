import { NextResponse } from 'next/server'
import crypto from 'crypto'

function sign(key, msg) {
  return crypto.createHmac('sha256', key).update(msg).digest()
}

export async function POST(request) {
  try {
    const { text, source, target } = await request.json()

    if (!text || !target) {
      return NextResponse.json(
        { success: false, error: '缺少必要参数' },
        { status: 400 }
      )
    }

    if (text.length > 5000) {
      return NextResponse.json(
        { success: false, error: '文本长度超过限制（最多5000字符）' },
        { status: 400 }
      )
    }

    const SecretId = process.env.TENCENT_SECRET_ID
    const SecretKey = process.env.TENCENT_SECRET_KEY

    if (!SecretId || !SecretKey) {
      return NextResponse.json(
        { success: false, error: '服务器配置错误：缺少腾讯云API密钥' },
        { status: 500 }
      )
    }

    const service = 'tmt'
    const host = 'tmt.tencentcloudapi.com'
    const region = 'ap-guangzhou'
    const action = 'TextTranslate'
    const version = '2018-03-21'
    const algorithm = 'TC3-HMAC-SHA256'

    const now = Math.floor(Date.now() / 1000)
    const date = new Date(now * 1000).toISOString().slice(0, 10)

    const payload = JSON.stringify({
      SourceText: text,
      Source: source || 'auto',
      Target: target,
      ProjectId: 0,
    })

    const httpRequestMethod = 'POST'
    const canonicalUri = '/'
    const canonicalQueryString = ''
    const canonicalHeaders = 'content-type:application/json; charset=utf-8\n' + 'host:' + host + '\n'
    const signedHeaders = 'content-type;host'
    const hashedRequestPayload = crypto.createHash('sha256').update(payload).digest('hex')
    const canonicalRequest = httpRequestMethod + '\n' + canonicalUri + '\n' + canonicalQueryString + '\n' + canonicalHeaders + '\n' + signedHeaders + '\n' + hashedRequestPayload

    const credentialScope = date + '/' + service + '/' + 'tc3_request'
    const hashedCanonicalRequest = crypto.createHash('sha256').update(canonicalRequest).digest('hex')
    const stringToSign = algorithm + '\n' + now + '\n' + credentialScope + '\n' + hashedCanonicalRequest

    const secretDate = sign(Buffer.from('TC3' + SecretKey), date)
    const secretService = sign(secretDate, service)
    const secretSigning = sign(secretService, 'tc3_request')
    const signature = crypto.createHmac('sha256', secretSigning).update(stringToSign).digest('hex')

    const authorization = algorithm + ' ' + 'Credential=' + SecretId + '/' + credentialScope + ', ' + 'SignedHeaders=' + signedHeaders + ', ' + 'Signature=' + signature

    const response = await fetch('https://' + host, {
      method: 'POST',
      headers: {
        'Authorization': authorization,
        'Content-Type': 'application/json; charset=utf-8',
        'Host': host,
        'X-TC-Action': action,
        'X-TC-Timestamp': now.toString(),
        'X-TC-Version': version,
        'X-TC-Region': region,
      },
      body: payload,
    })

    const data = await response.json()

    if (data.Response.Error) {
      return NextResponse.json(
        { success: false, error: data.Response.Error.Message },
        { status: 500 }
      )
    }

    return NextResponse.json({
      success: true,
      result: data.Response.TargetText,
      source: data.Response.Source,
      target: data.Response.Target,
    })
  } catch (error) {
    console.error('翻译错误:', error)
    return NextResponse.json(
      { 
        success: false, 
        error: error.message || '翻译服务异常'
      },
      { status: 500 }
    )
  }
}
