"""
本地 Whisper ASR 服务
OpenAI 兼容接口: POST /v1/audio/transcriptions
"""
from flask import Flask, request, jsonify
from faster_whisper import WhisperModel
import tempfile, os

app = Flask(__name__)

# 用 small 模型，速度快
model = WhisperModel("tiny", device="cpu", compute_type="int8")

@app.route('/v1/audio/transcriptions', methods=['POST'])
def transcribe():
    if 'file' not in request.files:
        return jsonify({'error': 'no file'}), 400
    f = request.files['file']
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
        f.save(tmp.name)
        tmp_path = tmp.name
    try:
        segments, info = model.transcribe(tmp_path, language='zh')
        text = ''.join(seg.text for seg in segments)
        return jsonify({'text': text})
    finally:
        os.unlink(tmp_path)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=9881)
