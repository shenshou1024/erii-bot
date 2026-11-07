import asyncio
import json
import websockets

WS_URL = 'ws://127.0.0.1:3001'
ACCESS_TOKEN = 'erii2024secretkey'

async def handle_event(ws, event):
    post_type = event.get('post_type', '')
    
    # 好友申请
    if post_type == 'request' and event.get('request_type') == 'friend':
        user_id = event.get('user_id', '')
        comment = event.get('comment', '')
        print(f'收到好友申请: {user_id}, 备注: {comment}')
        
        # 自动通过
        api_request = {
            'action': 'set_friend_add_request',
            'params': {
                'flag': event.get('flag', ''),
                'approve': True,
                'remark': ''
            }
        }
        await ws.send(json.dumps(api_request))
        print(f'已通过好友申请: {user_id}')
    
    # 进群申请
    elif post_type == 'request' and event.get('request_type') == 'group':
        user_id = event.get('user_id', '')
        group_id = event.get('group_id', '')
        sub_type = event.get('sub_type', '')
        print(f'收到进群申请: {user_id} -> {group_id}, 类型: {sub_type}')
        
        # 自动同意
        api_request = {
            'action': 'set_group_add_request',
            'params': {
                'flag': event.get('flag', ''),
                'sub_type': sub_type,
                'approve': True,
                'reason': ''
            }
        }
        await ws.send(json.dumps(api_request))
        print(f'已同意进群: {user_id} -> {group_id}')

async def main():
    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'}
    
    while True:
        try:
            print('连接 OneBot WS...')
            async with websockets.connect(WS_URL, additional_headers=headers) as ws:
                print('连接成功，监听事件...')
                async for message in ws:
                    try:
                        event = json.loads(message)
                        await handle_event(ws, event)
                    except Exception as e:
                        print(f'处理事件错误: {e}')
        except Exception as e:
            print(f'连接错误: {e}, 5秒后重连...')
            await asyncio.sleep(5)

if __name__ == '__main__':
    asyncio.run(main())
