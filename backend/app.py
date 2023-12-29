from datetime import timedelta

import mimetypes
# 在导入flask之前修复MIME类型，参考 https://stackoverflow.com/a/70741738/21178367
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')

from flask import *
import os


from core.detector import Detector
import core.setup

ALLOWED_EXTENSIONS = set(['png', 'jpg'])
app = Flask(__name__)
app.secret_key = 'secret!'

# 解决缓存刷新问题
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)
# 设置服务端文件路径
app.config['UPLOAD_FOLDER'] = 'server_files/upload'
app.config['OUTPUT_FOLDER'] = 'server_files/output'

# 添加header解决跨域
@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With'
    return response


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# 主页面，使用Vue构建
@app.route('/')
def index_page():
    return app.send_static_file('index.html')

# 修复页面图标，参考 https://stackoverflow.com/a/48863231/21178367
@app.route('/favicon.ico')
def index_page_icon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# 主页中使用的静态资源文件
@app.route('/<path:file>')
def index_page_file(file):
    return app.send_static_file(file)


# 用于上传并处理图像的接口
@app.route('/upload', methods=['GET', 'POST'])
def upload_image():
    file = request.files['file']

    if file and allowed_file(file.filename):
        print(f'Saving {app.config["UPLOAD_FOLDER"]}/{file.filename}...')
        file.save(f'{app.config["UPLOAD_FOLDER"]}/{file.filename}')

        image_info = core.setup.detect(current_app.model,
                                            app.config['UPLOAD_FOLDER'],
                                            app.config['OUTPUT_FOLDER'],
                                            file.filename)

        return jsonify({'status': 1,
                        'upload_url': f'{app.config["UPLOAD_FOLDER"]}/{file.filename}',
                        'output_url': f'{app.config["OUTPUT_FOLDER"]}/{file.filename}',
                        'image_info': image_info })

    return jsonify({'status': 0})


# 用于下载原图和结果图的接口
@app.route('/server_files/<path:file>', methods=['GET'])
def download_image(file):
    if request.method == 'GET':
        if not file is None:
            image_data = open(f'server_files/{file}', "rb").read()
            response = make_response(image_data)
            response.headers['Content-Type'] = 'image/png'
            return response


if __name__ == '__main__':
    with app.app_context():
        current_app.model = Detector()
    
    # 初始化上传文件夹
    if not os.path.exists(app.config["UPLOAD_FOLDER"]):
        print('Creating upload folder...')
        os.makedirs(app.config["UPLOAD_FOLDER"])
    
    # 初始化输出文件夹
    if not os.path.exists(app.config["OUTPUT_FOLDER"]):
        print('Creating output folder...')
        os.makedirs(app.config["OUTPUT_FOLDER"])

    app.run(host='127.0.0.1', port=5003, debug=True)
