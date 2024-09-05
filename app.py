from flask import Flask, render_template, request, send_file, after_this_request, flash, redirect, url_for
from pytubefix import YouTube
import os
import zipfile
import io
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def is_valid_youtube_url(url):
    youtube_regex = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/.+')
    return youtube_regex.match(url)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        links = request.form['links']
        link_list = links.splitlines()
        format_type = request.form['format']
        downloaded_files = []

        invalid_links = [link for link in link_list if not is_valid_youtube_url(link)]
        
        if invalid_links:
            flash(f'Link inválido: {", ".join(invalid_links)}')
            return redirect(url_for('index'))  # Redireciona para evitar problemas ao recarregar a página

        for link in link_list:
            try:
                yt = YouTube(link)
                file_path = None

                if format_type == 'mp4':
                    video_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
                    file_path = video_stream.download()

                elif format_type == 'mp3':
                    audio_stream = yt.streams.filter(only_audio=True, file_extension='mp4').first()
                    file_path = audio_stream.download()
                    base, ext = os.path.splitext(file_path)
                    new_file = base + '.mp3'
                    os.rename(file_path, new_file)
                    file_path = new_file

                if file_path:
                    downloaded_files.append(file_path)

            except Exception as e:
                flash(f'Erro ao baixar o link {link}: {e}')
                return redirect(url_for('index'))

        memory_file = io.BytesIO()
        with zipfile.ZipFile(memory_file, 'w') as zipf:
            for file in downloaded_files:
                zipf.write(file, os.path.basename(file))

        memory_file.seek(0)

        for file in downloaded_files:
            if os.path.exists(file):
                os.remove(file)

        return send_file(memory_file, as_attachment=True, download_name='mediasdownload.zip')

    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
