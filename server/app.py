#!/usr/bin/env python3
"""
老肥工具箱 - YouTube 下载后端服务
部署到你的云服务器，前端页面通过 API 调用 yt-dlp 下载视频。

使用方式：
  1. pip install -r requirements.txt
  2. 确保已安装 yt-dlp: pip install yt-dlp
  3. python app.py
  4. 前端填入 http://你的服务器IP:5000
"""

import os
import json
import uuid
import subprocess
import threading
import time
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ── 配置 ──
DOWNLOAD_DIR = Path(os.environ.get('DOWNLOAD_DIR', './downloads'))
DOWNLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_AGE = 3600  # 文件保留 1 小时
PORT = int(os.environ.get('PORT', 5000))

# ── 检测 ffmpeg ──
HAS_FFMPEG = False
try:
    subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
    HAS_FFMPEG = True
except Exception:
    pass

# ── 任务状态 ──
tasks = {}  # task_id -> { status, progress, filename, error, created }


def cleanup_old_files():
    """定期清理过期下载文件"""
    while True:
        time.sleep(300)
        now = time.time()
        try:
            for f in DOWNLOAD_DIR.iterdir():
                if f.is_file() and now - f.stat().st_mtime > MAX_FILE_AGE:
                    f.unlink(missing_ok=True)
            # 清理过期任务记录
            expired = [k for k, v in tasks.items() if now - v.get('created', 0) > MAX_FILE_AGE]
            for k in expired:
                tasks.pop(k, None)
        except Exception:
            pass


threading.Thread(target=cleanup_old_files, daemon=True).start()


@app.route('/')
def index():
    return jsonify({
        'service': '老肥工具箱 YouTube 下载服务',
        'status': 'running',
        'ffmpeg': HAS_FFMPEG,
        'endpoints': ['/api/info', '/api/formats', '/api/download', '/api/task/<id>', '/downloads/<file>']
    })


@app.route('/api/info', methods=['POST'])
def video_info():
    """获取视频信息"""
    data = request.get_json() or {}
    url = data.get('url', '').strip()
    if not url:
        return jsonify({'error': '缺少 url 参数'}), 400

    try:
        result = subprocess.run(
            ['yt-dlp', '--dump-json', '--no-download', url],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return jsonify({'error': result.stderr.strip() or '获取信息失败'}), 500

        info = json.loads(result.stdout)
        return jsonify({
            'id': info.get('id'),
            'title': info.get('title'),
            'duration': info.get('duration'),
            'uploader': info.get('uploader'),
            'view_count': info.get('view_count'),
            'thumbnail': info.get('thumbnail'),
            'description': (info.get('description') or '')[:300],
        })
    except subprocess.TimeoutExpired:
        return jsonify({'error': '请求超时'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/formats', methods=['POST'])
def video_formats():
    """获取所有可用格式"""
    data = request.get_json() or {}
    url = data.get('url', '').strip()
    if not url:
        return jsonify({'error': '缺少 url 参数'}), 400

    try:
        result = subprocess.run(
            ['yt-dlp', '-J', '--no-download', url],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode != 0:
            return jsonify({'error': result.stderr.strip() or '获取格式失败'}), 500

        info = json.loads(result.stdout)
        formats = []
        for f in info.get('formats', []):
            formats.append({
                'format_id': f.get('format_id'),
                'ext': f.get('ext'),
                'resolution': f.get('resolution', 'audio only'),
                'fps': f.get('fps'),
                'vcodec': f.get('vcodec', 'none'),
                'acodec': f.get('acodec', 'none'),
                'filesize': f.get('filesize') or f.get('filesize_approx'),
                'note': f.get('format_note', ''),
            })
        return jsonify({'title': info.get('title'), 'formats': formats})
    except subprocess.TimeoutExpired:
        return jsonify({'error': '请求超时'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download', methods=['POST'])
def start_download():
    """启动下载任务（异步）"""
    data = request.get_json() or {}
    url = data.get('url', '').strip()
    mode = data.get('mode', 'best')  # best | 1080 | 720 | 480 | audio_mp3 | audio_best
    if not url:
        return jsonify({'error': '缺少 url 参数'}), 400

    task_id = str(uuid.uuid4())[:8]
    tasks[task_id] = {'status': 'downloading', 'progress': '0%', 'filename': None, 'error': None, 'created': time.time()}

    def do_download():
        output_log = []
        try:
            output_tpl = str(DOWNLOAD_DIR / f'{task_id}_%(title).80s.%(ext)s')

            # 构建 yt-dlp 命令
            cmd = ['yt-dlp', '--no-playlist', '-o', output_tpl, '--newline']

            if mode == 'audio_mp3':
                if HAS_FFMPEG:
                    cmd += ['-x', '--audio-format', 'mp3', '--audio-quality', '0']
                else:
                    # 没有 ffmpeg，直接下载最佳音频流（不转码）
                    cmd += ['-f', 'bestaudio[ext=m4a]/bestaudio']
            elif mode == 'audio_best':
                if HAS_FFMPEG:
                    cmd += ['-x', '--audio-format', 'best']
                else:
                    cmd += ['-f', 'bestaudio[ext=m4a]/bestaudio']
            elif mode in ('1080', '720', '480'):
                height = mode
                if HAS_FFMPEG:
                    # 有 ffmpeg：下载分离的视频+音频流，合并为 mp4
                    cmd += [
                        '-f', f'bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<={height}]+bestaudio/best[height<={height}]',
                        '--merge-output-format', 'mp4',
                    ]
                else:
                    # 没有 ffmpeg：只能下载已经包含音视频的单文件
                    cmd += ['-f', f'best[height<={height}][ext=mp4]/best[height<={height}]']
            else:
                # best 模式
                if HAS_FFMPEG:
                    cmd += [
                        '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best',
                        '--merge-output-format', 'mp4',
                    ]
                else:
                    # 没有 ffmpeg：下载包含音视频的单文件 mp4
                    cmd += ['-f', 'best[ext=mp4]/best']

            cmd.append(url)

            tasks[task_id]['cmd'] = ' '.join(cmd)

            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in proc.stdout:
                line = line.strip()
                output_log.append(line)
                # 只保留最后 50 行日志
                if len(output_log) > 50:
                    output_log.pop(0)
                # 解析进度
                if '[download]' in line and '%' in line:
                    try:
                        pct = line.split('%')[0].split()[-1]
                        tasks[task_id]['progress'] = pct + '%'
                    except Exception:
                        pass

            proc.wait()
            if proc.returncode != 0:
                tasks[task_id]['status'] = 'error'
                # 提取有用的错误信息
                err_lines = [l for l in output_log if 'ERROR' in l or 'error' in l.lower()]
                err_msg = err_lines[-1] if err_lines else '\n'.join(output_log[-5:])
                tasks[task_id]['error'] = f'yt-dlp 失败: {err_msg}'
                return

            # 找到下载的文件
            files = sorted(DOWNLOAD_DIR.glob(f'{task_id}_*'), key=lambda f: f.stat().st_mtime, reverse=True)
            if files:
                tasks[task_id]['status'] = 'done'
                tasks[task_id]['filename'] = files[0].name
                tasks[task_id]['filesize'] = files[0].stat().st_size
                tasks[task_id]['progress'] = '100%'
            else:
                tasks[task_id]['status'] = 'error'
                tasks[task_id]['error'] = '下载完成但未找到文件，日志: ' + '\n'.join(output_log[-3:])

        except Exception as e:
            tasks[task_id]['status'] = 'error'
            tasks[task_id]['error'] = str(e)

    threading.Thread(target=do_download, daemon=True).start()
    return jsonify({'task_id': task_id, 'status': 'downloading'})


@app.route('/api/task/<task_id>')
def task_status(task_id):
    """查询任务状态"""
    task = tasks.get(task_id)
    if not task:
        return jsonify({'error': '任务不存在'}), 404

    resp = {
        'task_id': task_id,
        'status': task['status'],
        'progress': task['progress'],
    }
    if task['status'] == 'done':
        resp['filename'] = task['filename']
        resp['filesize'] = task.get('filesize', 0)
        resp['download_url'] = f'/downloads/{task["filename"]}'
    elif task['status'] == 'error':
        resp['error'] = task['error']
    return jsonify(resp)


@app.route('/downloads/<path:filename>')
def serve_file(filename):
    """提供文件下载"""
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)


if __name__ == '__main__':
    print(f'🚀 老肥工具箱下载服务启动在 http://0.0.0.0:{PORT}')
    print(f'📁 下载目录: {DOWNLOAD_DIR.resolve()}')
    print(f'⏰ 文件保留时间: {MAX_FILE_AGE}s')
    if HAS_FFMPEG:
        print(f'✅ ffmpeg 已检测到，支持视频合并和音频转码')
    else:
        print(f'⚠️  未检测到 ffmpeg！视频将以单文件格式下载（画质可能受限），音频无法转为 mp3')
        print(f'   安装方法: apt install ffmpeg (Ubuntu) / yum install ffmpeg (CentOS) / brew install ffmpeg (macOS)')
    app.run(host='0.0.0.0', port=PORT, debug=False)
