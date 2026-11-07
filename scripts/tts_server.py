#!/usr/bin/env python3
import asyncio, io, edge_tts
from flask import Flask, request, Response

app = Flask(__name__)

# Voice configs with rate, pitch, volume tuning
VOICES = {
    'erii': {
        'voice': 'zh-CN-XiaoxiaoNeural',
        'rate': '-5%',
        'pitch': '+2Hz',
        'volume': '+0%',
    },
    'xiaoyi': {
        'voice': 'zh-CN-XiaoyiNeural',
        'rate': '-10%',
        'pitch': '+5Hz',
        'volume': '+0%',
    },
}

@app.route('/v1/audio/speech', methods=['POST'])
def tts():
    data = request.get_json(force=True)
    text = data.get('input', '')
    voice_id = data.get('voice', 'erii')
    fmt = data.get('response_format', 'mp3')
    if not text:
        return Response('input is required', status=400)
    cfg = VOICES.get(voice_id, VOICES['erii'])
    async def synth():
        c = edge_tts.Communicate(
            text,
            cfg['voice'],
            rate=cfg['rate'],
            pitch=cfg['pitch'],
            volume=cfg['volume'],
        )
        buf = io.BytesIO()
        async for chunk in c.stream():
            if chunk['type'] == 'audio':
                buf.write(chunk['data'])
        return buf.getvalue()
    try:
        audio = asyncio.run(synth())
    except Exception as e:
        return Response(str(e), status=500)
    mime = 'audio/mpeg' if fmt == 'mp3' else f'audio/{fmt}'
    return Response(audio, mimetype=mime)

@app.route('/v1/models', methods=['GET'])
def models():
    return {'object': 'list', 'data': [{'id': 'tts-1', 'object': 'model', 'created': 0, 'owned_by': 'edge-tts'}]}

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9880, debug=False)
