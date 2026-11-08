import asyncio
import json
import random
import re
import subprocess
import base64
import websockets

WS_URL = 'ws://127.0.0.1:3001'
ACCESS_TOKEN = 'erii2024secretkey'
TARGET_QQ = '1701793763'

# 概率分配
URL_GROUPS = [
    ('B站', [
        'https://www.bilibili.com',
        'https://www.bilibili.com/anime/',
        'https://www.bilibili.com/variant/3',
        'https://www.bilibili.com/variant/64',
        'https://www.bilibili.com/variant/56',
    ], 0.30),
    ('小黑盒', [
        'https://xiaoheihe.cn/app/bbs/home',
    ], 0.25),
    ('小说', [
        'https://www.qidian.com',
        'https://www.jjwxc.net',
        'https://fanqienovel.com',
        'https://www.ciweimao.com',
    ], 0.15),
    ('其他', [
        'https://www.douban.com/group/topic/',
        'https://music.163.com',
        'https://www.zhihu.com/topic/19552732',
        'https://weibo.com/u/5516721467',
        'https://www.douyin.com',
        'https://www.4399.com',
    ], 0.20),
    ('休息', [], 0.10),
]

# 晚安模式状态
sleep_mode = False

def pick_url():
    global sleep_mode
    if sleep_mode:
        return None  # 晚安模式下不主动截图
    r = random.random()
    cumulative = 0
    for group_name, urls, prob in URL_GROUPS:
        cumulative += prob
        if r < cumulative:
            if group_name == '休息':
                return None
            return random.choice(urls)
    return URL_GROUPS[0][1][0]

MESSAGES = [
    'Sakura 你看这个！',
    '我刷到个好玩的',
    '给你看看这个',
    '这个有意思',
    '你看看这个',
]

async def send_screenshot(ws, url, text=None):
    output = '/tmp/proactive_screenshot.png'
    print(f'截图: {url}')
    
    result = subprocess.run(['node', '/opt/QQagent/scripts/web_browse.cjs', url, output], 
                          capture_output=True, text=True, timeout=60)
    print(result.stdout)
    if result.returncode != 0:
        print(f'截图失败: {result.stderr}')
        return
    
    # 提取标题
    title = ''
    if '---内容开始---' in result.stdout and '---内容结束---' in result.stdout:
        title = result.stdout.split('---内容开始---')[1].split('---内容结束---')[0].strip()
    
    if not text:
        text = random.choice(MESSAGES)
    if title:
        text = text + '\n\n' + title
    
    # 发文字
    msg_data = {
        'action': 'send_private_msg',
        'params': {
            'user_id': int(TARGET_QQ),
            'message': [{'type': 'text', 'data': {'text': text}}]
        }
    }
    await ws.send(json.dumps(msg_data))
    print(f'已发送: {text}')
    
    await asyncio.sleep(2)
    
    # 发图片
    with open(output, 'rb') as f:
        img_b64 = base64.b64encode(f.read()).decode()
    
    img_msg = {
        'action': 'send_private_msg',
        'params': {
            'user_id': int(TARGET_QQ),
            'message': [{'type': 'image', 'data': {'file': f'base64://{img_b64}'}}]
        }
    }
    await ws.send(json.dumps(img_msg))
    print('图片已发送')
    
    # 发完后自动删除临时文件
    import os
    if os.path.exists(output):
        os.remove(output)
        print('临时文件已删除')

async def listen_and_screenshot(ws):
    print('开始监听消息...')
    async for message in ws:
        try:
            data = json.loads(message)
            if data.get('post_type') == 'message' and data.get('message_type') == 'private':
                user_id = str(data.get('user_id', ''))
                raw_message = data.get('raw_message', '').strip()
                if user_id == TARGET_QQ:
                    global sleep_mode
                    # 晚安模式
                    if '晚安' in raw_message:
                        sleep_mode = True
                        print('进入晚安模式，暂停主动功能')
                    # 恢复模式
                    elif raw_message and raw_message not in ['晚安']:
                        if sleep_mode:
                            sleep_mode = False
                            print('退出晚安模式，恢复主动功能')
                    # 截图指令
                    if '截图' in raw_message or '看看网页' in raw_message or '刷一下' in raw_message:
                        print(f'收到指令: {raw_message}')
                        url = pick_url()
                        if url:
                            asyncio.create_task(send_screenshot(ws, url))
        except Exception as e:
            print(f'处理消息错误: {e}')

async def proactive_loop(ws):
    print('开始主动截图循环...')
    while True:
        wait_time = random.randint(600, 900)  # 10-15分钟
        print(f'等待 {wait_time//60} 分钟...')
        await asyncio.sleep(wait_time)
        
        url = pick_url()
        if url:
            print(f'主动截图: {url}')
            try:
                await send_screenshot(ws, url)
            except Exception as e:
                print(f'主动截图失败: {e}')

async def main():
    while True:
        try:
            print(f'连接到 {WS_URL}...')
            async with websockets.connect(WS_URL, additional_headers={'Authorization': f'Bearer {ACCESS_TOKEN}'}) as ws:
                print('已连接!')
                
                await asyncio.gather(
                    listen_and_screenshot(ws),
                    proactive_loop(ws)
                )
        except Exception as e:
            print(f'连接失败: {e}')
            await asyncio.sleep(5)

if __name__ == '__main__':
    asyncio.run(main())
