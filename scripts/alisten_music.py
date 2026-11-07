"""
Alisten 一起听 - QQagent 兼容版
移植自 nonebot-plugin-alisten
用法：
  听歌 稻香       → 点歌
  播放列表        → 看当前列表
  切歌           → 投票切歌
  当前在听       → 看正在播的
"""
import asyncio, json, aiohttp, re, random

TOKEN = 'erii2024secretkey'
WS_URL = 'ws://127.0.0.1:3001'
ADMIN_QQ = 1701793763

# alisten 服务器地址（公共测试服）
ALISTEN_SERVER = 'https://alisten.uy.sun'
HOUSE_ID = 'erii-room'
HOUSE_PASSWORD = 'erii2024'

async def alisten_request(method, path, data=None):
    """调用 alisten API"""
    url = f'{ALISTEN_SERVER}{path}'
    headers = {'Content-Type': 'application/json'}
    try:
        async with aiohttp.ClientSession() as s:
            if method == 'GET':
                async with s.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as r:
                    return await r.json()
            else:
                async with s.post(url, headers=headers, json=data, timeout=aiohttp.ClientTimeout(total=10)) as r:
                    return await r.json()
    except Exception as e:
        return {'error': str(e)}

async def ensure_house():
    """确保房间存在"""
    # 先搜索房间
    resp = await alisten_request('GET', '/house/search')
    houses = resp if isinstance(resp, list) else []
    for h in houses:
        if h.get('id') == HOUSE_ID:
            return True
    return False

async def pick_music(name, source='qq'):
    """点歌"""
    data = {
        'houseId': HOUSE_ID,
        'password': HOUSE_PASSWORD,
        'user': {'name': '绘梨衣', 'email': 'erii@qq.com'},
        'name': name,
        'source': source,
    }
    return await alisten_request('POST', '/music/pick', data)

async def get_playlist():
    """获取播放列表"""
    data = {'houseId': HOUSE_ID, 'password': HOUSE_PASSWORD}
    return await alisten_request('POST', '/music/playlist', data)

async def get_current():
    """获取当前播放"""
    data = {'houseId': HOUSE_ID, 'password': HOUSE_PASSWORD}
    return await alisten_request('POST', '/music/sync', data)

async def vote_skip():
    """投票切歌"""
    data = {
        'houseId': HOUSE_ID,
        'password': HOUSE_PASSWORD,
        'user': {'name': '绘梨衣', 'email': 'erii@qq.com'},
    }
    return await alisten_request('POST', '/music/skip/vote', data)

async def send_music_card(ws, user_id, song_id, platform='qq'):
    """发送音乐卡片到QQ"""
    msg = [{'type': 'music', 'data': {'type': platform, 'id': str(song_id)}}]
    await ws.send_str(json.dumps({'action': 'send_private_msg', 'params': {'user_id': user_id, 'message': msg}}))

async def main():
    # 先确保房间
    await ensure_house()
    print('alisten room ready', flush=True)

    while True:
        try:
            session = aiohttp.ClientSession()
            ws = await session.ws_connect(WS_URL, headers={'Authorization': f'Bearer {TOKEN}'})
            print('alisten connected', flush=True)

            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    try:
                        data = json.loads(msg.data)
                        if data.get('post_type') != 'message': continue
                        if data.get('user_id') != ADMIN_QQ: continue
                        text = data.get('raw_message', '')

                        # 点歌
                        m = re.match(r'^(?:听歌|一起听|点歌|放歌|放一首|唱首歌)\s*(.+)', text, re.I)
                        if m:
                            song_name = m.group(1).strip()
                            result = await pick_music(song_name)
                            if 'error' in result:
                                await ws.send_str(json.dumps({'action': 'send_private_msg', 'params': {'user_id': ADMIN_QQ, 'message': f'点歌失败了: {result["error"]}'}}))
                            else:
                                name = result.get('name', song_name)
                                sid = result.get('id', '')
                                await send_music_card(ws, ADMIN_QQ, sid)
                                await ws.send_str(json.dumps({'action': 'send_private_msg', 'params': {'user_id': ADMIN_QQ, 'message': f'给你点了 {name}'}}))
                            continue

                        # 播放列表
                        if re.match(r'^(?:播放列表|列表|歌单)', text):
                            result = await get_playlist()
                            playlist = result.get('playlist', [])
                            if not playlist:
                                await ws.send_str(json.dumps({'action': 'send_private_msg', 'params': {'user_id': ADMIN_QQ, 'message': '列表是空的，点首歌吧'}}))
                            else:
                                lines = [f'{i+1}. {p["name"]} ({p.get("source","")}) ❤{p.get("likes",0)}' for i, p in enumerate(playlist[:10])]
                                await ws.send_str(json.dumps({'action': 'send_private_msg', 'params': {'user_id': ADMIN_QQ, 'message': '\n'.join(lines)}}))
                            continue

                        # 当前在听
                        if re.match(r'^(?:当前在听|正在听|现在听|当前音乐)', text):
                            result = await get_current()
                            if 'error' in result:
                                await ws.send_str(json.dumps({'action': 'send_private_msg', 'params': {'user_id': ADMIN_QQ, 'message': '没在放歌'}}))
                            else:
                                await ws.send_str(json.dumps({'action': 'send_private_msg', 'params': {'user_id': ADMIN_QQ, 'message': f'正在听 {result.get("name","")}'}}))
                            continue

                        # 切歌
                        if re.match(r'^(?:切歌|下一首|跳过)', text):
                            result = await vote_skip()
                            if 'error' in result:
                                await ws.send_str(json.dumps({'action': 'send_private_msg', 'params': {'user_id': ADMIN_QQ, 'message': '切歌失败'}}))
                            else:
                                votes = result.get('current_votes', 0)
                                required = result.get('required_votes', 0)
                                await ws.send_str(json.dumps({'action': 'send_private_msg', 'params': {'user_id': ADMIN_QQ, 'message': f'切歌投票 {votes}/{required}'}}))
                            continue

                    except Exception as e:
                        print('err:', e, flush=True)
            await session.close()
        except Exception as e:
            print('conn err:', e, flush=True)
        await asyncio.sleep(5)

asyncio.run(main())
