import os
from flask import Flask, render_template, request, send_from_directory, abort, Response
import re

app = Flask(__name__)

# 影片文件夾路徑
ANIME_FOLDER = 'D:/server/anime'

@app.route('/')
def index():
    folders = sorted(os.listdir(ANIME_FOLDER))
    anime_data = []
    for folder in folders:
        folder_path = os.path.join(ANIME_FOLDER, folder)
        cover_image = f'/anime/{folder}/cover.jpg'
        if not os.path.exists(os.path.join(folder_path, 'cover.jpg')):
            cover_image = '/static/placeholder.jpg'  # 如果沒有自訂封面就顯示預設封面
        anime_data.append({'name': folder, 'cover': cover_image})
    
    return render_template('index.html', anime_data=anime_data)

# 封面圖路由
@app.route('/anime/<folder>/cover.jpg')
def serve_cover(folder):
    return send_from_directory(os.path.join(ANIME_FOLDER, folder), 'cover.jpg')

# 集數list頁面
@app.route('/anime/<folder>')
def show_episodes(folder):
    folder_path = os.path.join(ANIME_FOLDER, folder)
    # 只顯示MP4影片檔案
    episodes = [f for f in os.listdir(folder_path) if f.endswith('.mp4')]
    
    # 實現了只依照影片名稱裡面的數字進行排序避免了1,10,11,12,2,3,4的問題
    episodes.sort(key=lambda x: list(map(int, re.findall(r'\d+', x))))
    
    return render_template('episodes.html', folder=folder, episodes=episodes)

# 觀看影片
@app.route('/anime/<folder>/<episode>')
def watch_episode(folder, episode):
    folder_path = os.path.join(ANIME_FOLDER, folder)
    episode_path = os.path.join(folder_path, episode)
    
    if os.path.exists(episode_path):
        def generate():
            with open(episode_path, 'rb') as f:
                while True:
                    chunk = f.read(4096)  # 怕iPhone用戶的瀏覽器爆炸
                    if not chunk:
                        break
                    yield chunk

        response = Response(generate(), content_type='video/mp4')
        response.headers['Accept-Ranges'] = 'bytes'
        return response
    else:
        return abort(404)

# 提供影片文件的動態路徑 不然flask讀不到
@app.route('/anime/<folder>/video/<episode>')
def serve_video(folder, episode):
    folder_path = os.path.join(ANIME_FOLDER, folder)
    return send_from_directory(folder_path, episode)

# 搜尋ㄉ功能
@app.route('/search')
def search():
    query = request.args.get('q', '')
    results = []
    if query:
        for folder in os.listdir(ANIME_FOLDER):
            if query.lower() in folder.lower():
                results.append(folder)
    return render_template('search_results.html', query=query, results=results)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)