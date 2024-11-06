"""
    0-3对应三种识别方法
    0：百度语音识别标准版
    1：百度语音识别极速版
    2：科大讯飞标准版
    3：科大讯飞动态修正
    wav2csv: 识别单个语音
    wav2csv_file: 识别整个文件夹
"""
import os

from wav2text_sum import recognize_speech, recognize_speech_all
from pre_wav import convert_audio_to_wav
from pre_text2csv_multi import text2csv


def wav2csv(input_path, showDetail=False, select_model=2, saveCsv=True, csv_path="./label_test.csv"):
    # 变更wav采样率
    input_path = convert_audio_to_wav(input_path)
    # 语音识别
    result_text = recognize_speech(input_path, showDetail, select_model)
    if result_text == "":
        print("The selected ASR model did not recognize the text, try Baidu ASR.")
        result_text = recognize_speech(input_path, showDetail, 1)
    print("Recognized Text:", result_text)
    # 文本转CSV
    if saveCsv:
        text2csv(input_path, result_text, csv_path)
    # 删除temp文件
    if '_temp.wav' in input_path:
        os.remove(input_path)
    return result_text


def wav2csv_file(folder_path, showDetail=False, select_model=2, saveCsv=True, csv_path="./label_test.csv"):

    # 获取文件夹下的所有文件和文件夹名称
    all_files = os.listdir(folder_path)

    # 过滤出文件名，排除文件夹
    file_names = [f for f in all_files if os.path.isfile(os.path.join(folder_path, f))]

    # 打印文件名
    for file_name in file_names:
        # 使用函数
        input_path = os.path.join(folder_path, file_name)

        # 调用wav转csv的函数
        wav2csv(input_path, showDetail, select_model, saveCsv, csv_path)