"""QQ空间说说发布脚本 - 需要cookie"""
import requests, time, random, json, re

QQ = '3867035056'

# 读cookie
def load_cookies():
    try:
        with open('/opt/QQagent/qzone_cookies.txt') as f:
            return f.read().strip()
    except:
        return ''

def post_shuo(content):
    cookies_str = load_cookies()
    if not cookies_str:
        return '没有cookie，发不了'
    
    # 解析cookie
    cookies = {}
    for part in cookies_str.split(';'):
        part = part.strip()
        if '=' in part:
            k, v = part.split('=', 1)
            cookies[k.strip()] = v.strip()
    
    skey = cookies.get('skey', '')
    p_skey = cookies.get('p_skey', '')
    if not skey or not p_skey:
        return 'cookie不完整'
    
    # 构造g_tk
    def gtk(hskey):
        h = 5381
        for c in hskey:
            h += (h << 5) + ord(c)
        return h & 0x7fffffff
    
    gtk = gtk(skey)
    
    url = f'https://user.qzone.qq.com/publish'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': f'https://user.qzone.qq.com/{QQ}',
        'Cookie': cookies_str,
    }
    
    data = {
        'conn': '1',
        'synced': '1',
        'content': content,
        'pic': '',
        'url': '',
        'location': '',
        'feedfiltered': '',
        'picwanjang': '',
        'flushnum': f'{random.randint(1000,9999)}',
        'appid': '311',
        'shopInfo': '',
        'refresh': '0',
        'client_type': '1',
        'hostUin': QQ,
        'uin': QQ,
        'g_tk': gtk,
    }
    
    try:
        r = requests.post(url, headers=headers, data=data, timeout=10)
        result = r.json()
        if result.get('code') == 0:
            return '说说发成功了'
        else:
            return f'发失败：{result.get("message", result)}'
    except Exception as e:
        return f'出错：{e}'

# 测试
if __name__ == '__main__':
    print(post_shuo('今天天气真好'))
