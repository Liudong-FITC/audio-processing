import json
import time
from urllib.request import urlopen, Request
from urllib.error import URLError
from urllib.parse import urlencode
import websocket
import datetime
from wsgiref.handlers import format_date_time
import hashlib
import base64
import hmac
import ssl
from time import mktime
import _thread as thread
from datetime import datetime


"""
    recognize_speech(input_path, False, 1):
    输入：语音的地址，使用科大讯飞的动态修正时需不需要显示细节。0~3分别表示百度标准版、百度极速版、科大讯飞标准版、科大讯飞动态修正
    输出：识别的文本
    recognize_speech_all(input_path, False)
    输入：语音的地址，使用科大讯飞的动态修正时需不需要显示细节。
    输出：没有输出，但是会print四个ASR模型的转写结果
"""


# 定义函数，输入为音频文件路径，输出为识别的文本内容
def recognize_speech_baidu_stand(input_path):
    API_KEY = 'lUWetObGojKELYf5KGpYLIHQ'  # 替换为你的API_KEY
    SECRET_KEY = 'jiMy4fTsW8pdoyTNQWaHHyQgW6aZVNGp'  # 替换为你的SECRET_KEY

    # 文件格式
    FORMAT = input_path[-3:]  # 文件后缀只支持 pcm/wav/amr 格式

    CUID = '123456PYTHON'
    RATE = 16000  # 固定值
    DEV_PID = 1537  # 表示识别普通话，使用输入法模型
    ASR_URL = 'http://vop.baidu.com/server_api'

    # 获取token
    def fetch_token():
        params = {'grant_type': 'client_credentials', 'client_id': API_KEY, 'client_secret': SECRET_KEY}
        post_data = urlencode(params).encode('utf-8')
        req = Request('http://aip.baidubce.com/oauth/2.0/token', post_data)
        try:
            f = urlopen(req)
            result_str = f.read().decode('utf-8')
        except URLError as err:
            result_str = err.read().decode('utf-8')
        result = json.loads(result_str)
        if 'access_token' in result and 'scope' in result:
            return result['access_token']
        else:
            raise Exception('Failed to get token or scope')

    # 主函数逻辑
    token = fetch_token()

    with open(input_path, 'rb') as speech_file:
        speech_data = speech_file.read()
    if len(speech_data) == 0:
        raise Exception('File is empty')

    params = {'cuid': CUID, 'token': token, 'dev_pid': DEV_PID}
    params_query = urlencode(params)
    headers = {'Content-Type': 'audio/' + FORMAT + '; rate=' + str(RATE), 'Content-Length': len(speech_data)}
    url = ASR_URL + "?" + params_query

    try:
        begin = time.perf_counter()
        f = urlopen(Request(url, speech_data, headers))
        result_str = f.read().decode('utf-8')
        # print("Request time cost:", time.perf_counter() - begin)
    except URLError as err:
        print('asr http response http code:', err.code)
        result_str = err.read().decode('utf-8')

    # 解析结果
    result_data = json.loads(result_str)
    result_list = result_data.get("result", [])
    if result_list:
        result_text = result_list[0]
        # print("Text content:", result_text)
        return result_text
    else:
        print("No text content recognized!")
        return None


def recognize_speech_baidu_fast(input_path):
    API_KEY = 'lUWetObGojKELYf5KGpYLIHQ'  # 替换为你的API_KEY
    SECRET_KEY = 'jiMy4fTsW8pdoyTNQWaHHyQgW6aZVNGp'  # 替换为你的SECRET_KEY

    # 文件格式
    FORMAT = input_path[-3:]  # 文件后缀支持 wav/amr/m4a 格式

    CUID = '123456PYTHON'
    RATE = 16000  # 采样率，极速版支持16000和8000
    DEV_PID = 80001  # 极速版模型ID
    ASR_URL = 'http://vop.baidu.com/pro_api'
    SCOPE = 'brain_enhanced_asr'  # 有此scope表示有asr能力，没有请在网页里开通极速版

    class DemoError(Exception):
        pass

    """  TOKEN start """
    TOKEN_URL = 'http://aip.baidubce.com/oauth/2.0/token'

    def fetch_token():
        params = {'grant_type': 'client_credentials', 'client_id': API_KEY, 'client_secret': SECRET_KEY}
        post_data = urlencode(params).encode('utf-8')
        req = Request(TOKEN_URL, post_data)
        try:
            f = urlopen(req)
            result_str = f.read().decode('utf-8')
        except URLError as err:
            result_str = err.read().decode('utf-8')
        result = json.loads(result_str)
        if 'access_token' in result and 'scope' in result:
            if SCOPE and (not SCOPE in result['scope'].split(' ')):
                raise DemoError('scope is not correct')
            return result['access_token']
        else:
            raise DemoError('MAYBE API_KEY or SECRET_KEY not correct: access_token or scope not found in token response')

    """  TOKEN end """
    token = fetch_token()

    with open(input_path, 'rb') as speech_file:
        speech_data = speech_file.read()
    if len(speech_data) == 0:
        raise DemoError('file %s length read 0 bytes' % input_path)

    params = {'cuid': CUID, 'token': token, 'dev_pid': DEV_PID}
    params_query = urlencode(params)

    headers = {
        'Content-Type': 'audio/' + FORMAT + '; rate=' + str(RATE),
        'Content-Length': len(speech_data)
    }

    url = ASR_URL + "?" + params_query

    req = Request(url, speech_data, headers)
    try:
        f = urlopen(req)
        result_str = f.read().decode('utf-8')
    except URLError as err:
        result_str = err.read().decode('utf-8')

    # 解析结果
    result_data = json.loads(result_str)
    result_list = result_data.get("result", [])
    if result_list:
        result_text = result_list[0]
        return result_text
    else:
        print("No text content recognized!")
        return None


STATUS_FIRST_FRAME = 0  # 第一帧的标识
STATUS_CONTINUE_FRAME = 1  # 中间帧标识
STATUS_LAST_FRAME = 2  # 最后一帧的标识

class Ws_Param(object):
    def __init__(self, APPID, APIKey, APISecret, AudioFile):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.AudioFile = AudioFile
        self.CommonArgs = {"app_id": self.APPID}
        self.BusinessArgs = {"domain": "iat", "language": "zh_cn", "accent": "mandarin", "vinfo": 1, "vad_eos": 10000}

    def create_url(self):
        url = 'wss://ws-api.xfyun.cn/v2/iat'
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        signature_origin = "host: ws-api.xfyun.cn\ndate: {}\nGET /v2/iat HTTP/1.1".format(date)
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'), digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
        authorization_origin = 'api_key="{}", algorithm="{}", headers="{}", signature="{}"'.format(self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        url = url + '?' + urlencode(v)
        return url

# 科大讯飞标准版
def recognize_speech_kdxf_stand(input_path, showDetail=True):

    result_text = ""  # 初始化结果文本


    def on_message(ws, message):
        nonlocal result_text
        try:
            code = json.loads(message)["code"]
            sid = json.loads(message)["sid"]
            if code != 0:
                errMsg = json.loads(message)["message"]
                if showDetail:
                    print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
            else:
                data = json.loads(message)["data"]["result"]["ws"]
                result = "".join(w["w"] for i in data for w in i["cw"])
                if showDetail:
                    print("sid:%s call success!,data is:%s" % (sid, json.dumps(data, ensure_ascii=False)))
                result_text += result
        except Exception as e:
            if showDetail:
                print("receive msg,but parse exception:", e)

    def on_error(ws, error):
        if showDetail:
            print("### error:", error)

    def on_close(ws, close_status_code, close_msg):
        if showDetail:
            print("### closed ###")

    def on_open(ws):
        def run(*args):
            frameSize = 8000  # 每一帧的音频大小
            interval = 0.04  # 发送音频间隔(单位:s)
            status = STATUS_FIRST_FRAME  # 音频的状态信息，标识音频是第一帧，还是中间帧、最后一帧

            with open(wsParam.AudioFile, "rb") as fp:
                while True:
                    buf = fp.read(frameSize)
                    if not buf:
                        status = STATUS_LAST_FRAME
                    if status == STATUS_FIRST_FRAME:
                        d = {"common": wsParam.CommonArgs, "business": wsParam.BusinessArgs, "data": {"status": 0, "format": "audio/L16;rate=16000", "audio": str(base64.b64encode(buf), 'utf-8'), "encoding": "raw"}}
                        d = json.dumps(d)
                        ws.send(d)
                        status = STATUS_CONTINUE_FRAME
                    elif status == STATUS_CONTINUE_FRAME:
                        d = {"data": {"status": 1, "format": "audio/L16;rate=16000", "audio": str(base64.b64encode(buf), 'utf-8'), "encoding": "raw"}}
                        ws.send(json.dumps(d))
                    elif status == STATUS_LAST_FRAME:
                        d = {"data": {"status": 2, "format": "audio/L16;rate=16000", "audio": str(base64.b64encode(buf), 'utf-8'), "encoding": "raw"}}
                        ws.send(json.dumps(d))
                        time.sleep(1)
                        break
                    time.sleep(interval)
            ws.close()

        thread.start_new_thread(run, ())

    wsParam = Ws_Param(APPID='7adce23a', APISecret='OGY1OGQ2MjZkZDBiY2I3MDM0ZjI2NmFk', APIKey='4fb78af25b5af8c3a7a62ebf3a09c345', AudioFile=input_path)
    websocket.enableTrace(False)
    wsUrl = wsParam.create_url()
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    return result_text


class Ws_Param_dwa(object):
    def __init__(self, APPID, APIKey, APISecret, AudioFile):
        self.APPID = APPID
        self.APIKey = APIKey
        self.APISecret = APISecret
        self.AudioFile = AudioFile
        self.CommonArgs = {"app_id": self.APPID}
        self.BusinessArgs = {"domain": "iat", "language": "zh_cn", "accent": "mandarin", "vinfo": 1, "vad_eos": 10000, "dwa": "wpgs"}

    def create_url(self):
        url = 'wss://ws-api.xfyun.cn/v2/iat'
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        signature_origin = "host: ws-api.xfyun.cn\ndate: {}\nGET /v2/iat HTTP/1.1".format(date)
        signature_sha = hmac.new(self.APISecret.encode('utf-8'), signature_origin.encode('utf-8'), digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
        authorization_origin = 'api_key="{}", algorithm="{}", headers="{}", signature="{}"'.format(self.APIKey, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        v = {
            "authorization": authorization,
            "date": date,
            "host": "ws-api.xfyun.cn"
        }
        url = url + '?' + urlencode(v)
        return url

def recognize_speech_kdxf_dwa(input_path, showDetail=True):

    wsParam = Ws_Param_dwa(APPID='7adce23a', APISecret='OGY1OGQ2MjZkZDBiY2I3MDM0ZjI2NmFk', APIKey='4fb78af25b5af8c3a7a62ebf3a09c345', AudioFile=input_path)
    wsUrl = wsParam.create_url()

    final_result_text = ""  # 初始化结果文本
    is_final_saved = False

    def on_message(ws, message):
        nonlocal final_result_text, is_final_saved
        try:
            code = json.loads(message)["code"]
            sid = json.loads(message)["sid"]
            if code != 0:
                errMsg = json.loads(message)["message"]
                if showDetail:
                    print("sid:%s call error:%s code is:%s" % (sid, errMsg, code))
            else:
                data = json.loads(message)["data"]["result"]["ws"]
                result = ""
                for i in data:
                    for w in i["cw"]:
                        result += w["w"]
                if showDetail:
                    print("sid:%s call success!,data is:%s" % (sid, json.dumps(data, ensure_ascii=False)))
                if json.loads(message)["data"]["status"] != 2:
                    final_result_text = result
                elif json.loads(message)["data"]["status"] == 2 and not is_final_saved:
                    final_result_text += result
                    is_final_saved = True
                elif json.loads(message)["data"]["status"] == 2 and is_final_saved:
                    if showDetail:
                        print("Final result is already saved from previous frame.")
        except Exception as e:
            if showDetail:
                print("receive msg,but parse exception:", e)

    def on_error(ws, error):
        if showDetail:
            print("### error:", error)

    def on_close(ws, close_status_code, close_msg):
        if showDetail:
            print("### closed ###")

    def on_open(ws):
        def run(*args):
            frameSize = 8000
            interval = 0.04
            status = STATUS_FIRST_FRAME

            with open(wsParam.AudioFile, "rb") as fp:
                while True:
                    buf = fp.read(frameSize)
                    if not buf:
                        status = STATUS_LAST_FRAME
                    if status == STATUS_FIRST_FRAME:
                        d = {"common": wsParam.CommonArgs, "business": wsParam.BusinessArgs, "data": {"status": 0, "format": "audio/L16;rate=16000", "audio": str(base64.b64encode(buf), 'utf-8'), "encoding": "raw"}}
                        d = json.dumps(d)
                        ws.send(d)
                        status = STATUS_CONTINUE_FRAME
                    elif status == STATUS_CONTINUE_FRAME:
                        d = {"data": {"status": 1, "format": "audio/L16;rate=16000", "audio": str(base64.b64encode(buf), 'utf-8'), "encoding": "raw"}}
                        ws.send(json.dumps(d))
                    elif status == STATUS_LAST_FRAME:
                        d = {"data": {"status": 2, "format": "audio/L16;rate=16000", "audio": str(base64.b64encode(buf), 'utf-8'), "encoding": "raw"}}
                        ws.send(json.dumps(d))
                        time.sleep(1)
                        break
                    time.sleep(interval)
            ws.close()

        thread.start_new_thread(run, ())

    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(wsUrl, on_message=on_message, on_error=on_error, on_close=on_close)
    ws.on_open = on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

    return final_result_text




# 使用函数
# input_path = r'E:\code\V2AT\dataset\noise\output2_temp.wav'
# result_text = recognize_speech_baidu_stand(input_path)
# result_text = recognize_speech_baidu_fast(input_path)
# result_text = recognize_speech_kdxf_stand(input_path, False)
# result_text = recognize_speech_kdxf_dwa(input_path, True)
# print("Recognized Text:", result_text)


def recognize_speech(input_path, showDetail=True, model=0):

    if model == 0:
        result_text = recognize_speech_baidu_stand(input_path)
    elif model == 1:
        result_text = recognize_speech_baidu_fast(input_path)
    elif model == 2:
        result_text = recognize_speech_kdxf_stand(input_path, showDetail)
    else:
        result_text = recognize_speech_kdxf_dwa(input_path, showDetail)

    return result_text


def recognize_speech_all(input_path, showDetail=True):

    result_text = recognize_speech_baidu_stand(input_path)
    print("百度标准版：" + result_text)
    result_text = recognize_speech_baidu_fast(input_path)
    print("百度极速版：" + result_text)
    if showDetail: print("")
    result_text = recognize_speech_kdxf_stand(input_path, showDetail)
    print("科大讯飞标准版：" + result_text)
    if showDetail: print("")
    result_text = recognize_speech_kdxf_dwa(input_path, showDetail)
    print("科大讯飞动态修正：" + result_text)

