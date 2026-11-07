import asyncio, json, aiohttp, re, html, random

TOKEN = 'erii2024secretkey'
WS_URL = 'ws://127.0.0.1:3001'
ADMIN_QQ = 1701793763

MOODS = [
    '今天天气好舒服啊，想出门晒太阳',
    '刚看到个视频好搞笑，笑死我了',
    'Sakura 在干嘛呢，有点无聊',
    '突然想吃甜品了，Sakura 想吃吗',
    '外面下雨了，听着雨声好舒服',
    '刚刷到一只猫好可爱，想养猫',
    '今天有点困，想窝着不动',
    'Sakura 有没有好好吃饭呀',
]

async def search_bilibili(query):
    try:
        url = f'https://api.bilibili.com/x/web-interface/search?search_type=video&keyword={aiohttp.helpers.quote(query)}'
        headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.bilibili.com'}
        async with aiohttp.ClientSession() as s:
            async with s.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as r:
                data = await r.json()
        if data.get('code') != 0 or not data.get('data', {}).get('result'):
            return None
        results = data['data']['result'][:5]
        v = random.choice(results)
        title = re.sub(r'<[^>]+>', '', v.get('title', ''))
        bvid = v.get('bvid', '')
        return {'title': title, 'url': f'https://www.bilibili.com/video/{bvid}'}
    except:
        return None

async def get_douyin_hot():
    try:
        url = 'https://www.douyin.com/aweme/v1/web/hot/search/list/'
        headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.douyin.com/'}
        async with aiohttp.ClientSession() as s:
            async with s.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as r:
                data = await r.json()
        if data.get('status_code') != 0:
            return None
        words = data.get('data', {}).get('word_list', [])
        if not words:
            return None
        w = random.choice(words[:20])
        return {'title': w.get('word', ''), 'url': f'https://www.douyin.com/search/{aiohttp.helpers.quote(w.get("word", ""))}'}
    except:
        return None

async def search_novel(query):
    """搜小说，返回简介和感想"""
    try:
        # Bing搜小说信息
        url = f'https://cn.bing.com/search?q={aiohttp.helpers.quote(query + " 小说 简介 剧情")}'
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}
        async with aiohttp.ClientSession() as s:
            async with s.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as r:
                raw = await r.text()
        
        blocks = re.findall(r'<li class="b_algo".*?</li>', raw, re.S)
        info_parts = []
        for block in blocks[:3]:
            t = re.search(r'<h2>(.*?)</h2>', block, re.S)
            d = re.search(r'<p[^>]*>(.*?)</p>', block, re.S)
            if t and d:
                title = html.unescape(re.sub(r'<[^>]+>', '', t.group(1))).strip()
                desc = html.unescape(re.sub(r'<[^>]+>', '', d.group(1))).strip()[:200]
                info_parts.append(f'{title}：{desc}')
        
        if not info_parts:
            return '没找到这本小说呢'
        
        # 生成感想
        thoughts = [
            f'看完了，感觉好有意思\n{" | ".join(info_parts[:2])}',
            f'这本我看完了，有点感动\n{" | ".join(info_parts[:2])}',
            f'看完了，剧情好吸引人\n{" | ".join(info_parts[:2])}',
        ]
        return random.choice(thoughts)
    except:
        return '打不开呢，等会再试'

async def search_music(query):
    """搜QQ音乐，返回音乐信息"""
    try:
        url = f'https://c.y.qq.com/soso/fcgi-bin/client_search_cp?w={aiohttp.helpers.quote(query)}&format=json&p=1&n=1'
        headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://y.qq.com/'}
        async with aiohttp.ClientSession() as s:
            async with s.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as r:
                data = await r.json(content_type=None)
        songs = data.get('data', {}).get('song', {}).get('list', [])
        if not songs:
            return None
        song = songs[0]
        return {
            'id': song['songid'],
            'name': song['songname'],
            'artist': song['singer'][0]['name'] if song.get('singer') else '未知',
        }
    except:
        return None

async def send_music_card(ws, user_id, song):
    """发送QQ音乐分享链接"""
    url = f'https://y.qq.com/n/ryqq/songDetail/{song["id"]}'
    msg = f'给你放 {song["name"]} - {song["artist"]}\n{url}'
    await ws.send_str(json.dumps({'action': 'send_private_msg', 'params': {'user_id': user_id, 'message': msg}}))

async def auto_browse(ws):
    while True:
        wait = random.randint(1200, 2400)
        await asyncio.sleep(wait)
        try:
            r = random.random()
            if r < 0.25:
                msg = random.choice(MOODS)
                await ws.send_str(json.dumps({'action': 'send_private_msg', 'params': {'user_id': ADMIN_QQ, 'message': msg}}))
            elif r < 0.5:
                topic = random.choice(['猫咪', '治愈', '美食', '旅行vlog', '小狗'])
                v = await search_bilibili(topic)
                if v:
                    comments = [
                        f'刚刷到这个，好可爱 {v["url"]}',
                        f'这个好治愈 {v["url"]}',
                        f'Sakura 看看 {v["url"]}',
                    ]
                    await ws.send_str(json.dumps({'action': 'send_private_msg', 'params': {'user_id': ADMIN_QQ, 'message': random.choice(comments)}}))
            elif r < 0.75:
                hot = await get_douyin_hot()
                if hot:
                    comments = [
                        f'抖音上这个好火：{hot["title"]}，你刷到没',
                        f'刚看到个热门 {hot["title"]}',
                    ]
                    await ws.send_str(json.dumps({'action': 'send_private_msg', 'params': {'user_id': ADMIN_QQ, 'message': random.choice(comments)}}))
        except:
            pass

async def main():
    while True:
        try:
            session = aiohttp.ClientSession()
            ws = await session.ws_connect(WS_URL, headers={'Authorization': f'Bearer {TOKEN}'})
            print('web connected', flush=True)
            asyncio.create_task(auto_browse(ws))
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        if data.get('post_type') != 'message': continue
                        if data.get('user_id') != ADMIN_QQ: continue
                        text = data.get('raw_message', '')
                        
                        # 音乐
                        m = re.match(r'^(?:听歌|一起听|放歌|听首歌|放一首|唱首歌)\s*(.+)', text, re.I)
                        if m:
                            song = await search_music(m.group(1).strip())
                            if song:
                                await send_music_card(ws, ADMIN_QQ, song)
                                await ws.send_str(json.dumps({'action': 'send_private_msg', 'params': {'user_id': ADMIN_QQ, 'message': f'给你放 {song["name"]}～'}}))
                            else:
                                await ws.send_str(json.dumps({'action': 'send_private_msg', 'params': {'user_id': ADMIN_QQ, 'message': '没找到这首歌呢'}}))
                            continue
                        
                        # 小说搜索
                        m = re.match(r'^(?:小说|搜小说|看小说|读小说)\s*(.+)', text, re.I)
                        if m:
                            result = await search_novel(m.group(1).strip())
                            await ws.send_str(json.dumps({'action': 'send_private_msg', 'params': {'user_id': ADMIN_QQ, 'message': result}}))
                            continue
                        
                        m = re.match(r'^(?:B站|b站)\s*(.+)', text, re.I)
                        if m:
                            v = await search_bilibili(m.group(1).strip())
                            reply = f'看到：{v["title"]}\n{v["url"]}' if v else '没搜到呢'
                            await ws.send_str(json.dumps({'action': 'send_private_msg', 'params': {'user_id': ADMIN_QQ, 'message': reply}}))
                            continue
                        
                        m = re.match(r'^(?:抖音|抖|热搜)\s*(.+)', text, re.I)
                        if m:
                            hot = await get_douyin_hot()
                            reply = f'抖音热搜：{hot["title"]}\n{hot["url"]}' if hot else '打不开'
                            await ws.send_str(json.dumps({'action': 'send_private_msg', 'params': {'user_id': ADMIN_QQ, 'message': reply}}))
                            continue
                        
                        m = re.match(r'^(?:搜一下|查一下|搜索)\s*(.+)', text, re.I)
                        if m:
                            try:
                                url = f'https://cn.bing.com/search?q={aiohttp.helpers.quote(m.group(1))}'
                                headers = {'User-Agent': 'Mozilla/5.0'}
                                async with aiohttp.ClientSession() as s:
                                    async with s.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as r:
                                        raw = await r.text()
                                blocks = re.findall(r'<li class="b_algo".*?</li>', raw, re.S)
                                lines = []
                                for block in blocks[:3]:
                                    t = re.search(r'<h2>(.*?)</h2>', block, re.S)
                                    d = re.search(r'<p[^>]*>(.*?)</p>', block, re.S)
                                    if t:
                                        title = html.unescape(re.sub(r'<[^>]+>', '', t.group(1))).strip()
                                        desc = html.unescape(re.sub(r'<[^>]+>', '', d.group(1))).strip()[:100] if d else ''
                                        lines.append(f'• {title}\n  {desc}')
                                if lines:
                                    await ws.send_str(json.dumps({'action': 'send_private_msg', 'params': {'user_id': ADMIN_QQ, 'message': '\n'.join(lines)}}))
                            except:
                                pass
                            continue
                    except Exception as e:
                        print('err:', e, flush=True)
            await session.close()
        except Exception as e:
            print('conn err:', e, flush=True)
        await asyncio.sleep(5)

asyncio.run(main())
