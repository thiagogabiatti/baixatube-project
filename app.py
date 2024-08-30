from flask import Flask, render_template, request, send_file, after_this_request
from pytubefix import YouTube
import os
import zipfile

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        links = request.form['links'] #return string with links from textarea
        link_list = links.splitlines()
        format_type = request.form['format']
        downloaded_files = [] # list to store paths from downloaded files

        for link in link_list:
            yt = YouTube(link)
            file_path = None

            if format_type == 'mp4':
                # Download video as MP4
                video_stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
                file_path = video_stream.download()

            elif format_type == 'mp3':
                # Download audio as MP3
                audio_stream = yt.streams.filter(only_audio=True, file_extension='mp4').first()
                file_path = audio_stream.download()
                # Rename file to .mp3
                base, ext = os.path.splitext(file_path)
                new_file = base + '.mp3'
                os.rename(file_path, new_file)
                file_path = new_file

            if file_path:
                downloaded_files.append(file_path)

        # zip all files
        zip_filename = 'mediasdownload.zip'
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for file in downloaded_files:
                zipf.write(file, os.path.basename(file))

        @after_this_request
        def remove_files(response):
            try:
                # remove individual files
                for file in downloaded_files:
                    if os.path.exists(file):
                        os.remove(file)
                # remove zip file
                if os.path.exists(zip_filename): 
                    os.remove(zip_filename)
            except Exception as e:
                print(f"Error removing file: {e}")
            return response


        return send_file(zip_filename, as_attachment=True)


    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)