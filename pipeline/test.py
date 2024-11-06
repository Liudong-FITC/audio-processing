"""
    0-3对应三种识别方法
    0：百度语音识别标准版
    1：百度语音识别极速版
    2：科大讯飞标准版
    3：科大讯飞动态修正
"""
import os

from wav2text_sum import recognize_speech, recognize_speech_all
from pre_wav import convert_audio_to_wav
from pre_text2csv import text2csv
from pre_text2csv_multi import text2csv
from pre_wav2csv import wav2csv, wav2csv_file


# """单个音频"""
# # 使用函数
# # input_path = r'E:\code\V2AT\dataset\noise\denoised_audio_wiener_filter.wav'
# input_path = r'E:\code\V2AT\dataset\1\VID_20241104_151915_new.wav'
# # 变更wav采样率
# input_path = convert_audio_to_wav(input_path)
# # 语音识别
# result_text = recognize_speech(input_path, False, 1)
# print("Recognized Text:", result_text)
#
# # recognize_speech_all(input_path, True)
#
# # 文本转CSV
# text2csv(input_path, result_text)


# """多个音频"""
# # 指定文件夹路径
# folder_path = r'E:\code\V2AT\dataset\2'  # 替换为您的文件夹路径
#
# # 获取文件夹下的所有文件和文件夹名称
# all_files = os.listdir(folder_path)
#
# # 过滤出文件名，排除文件夹
# file_names = [f for f in all_files if os.path.isfile(os.path.join(folder_path, f))]
#
# # 打印文件名
# for file_name in file_names:
#
#     # 使用函数
#     input_path = os.path.join(folder_path, file_name)
#     # 变更wav采样率
#     input_path = convert_audio_to_wav(input_path)
#     # 语音识别
#     result_text = recognize_speech(input_path, False, 1)
#     print("Recognized Text:", result_text)
#
#     # recognize_speech_all(input_path, False)
#     # 文本转CSV
#     text2csv(input_path, result_text, './label2_baidu.csv')


"""整合函数"""
# 整合函数
input_path = r'E:\code\V2AT\dataset\1\VID_20241104_151915_new.wav'
result_text = wav2csv(input_path, showDetail=False, select_model=1, saveCsv=True, csv_path="./label_test.csv")
print(result_text)



"""识别文件夹"""
# 识别文件夹
# 指定文件夹路径
folder_path = r'E:\code\V2AT\dataset\1'  # 替换为您的文件夹路径

wav2csv_file(folder_path, showDetail=False, select_model=2, saveCsv=True, csv_path="./label2_test.csv")



# # 获取文件夹下的所有文件和文件夹名称
# all_files = os.listdir(folder_path)
#
# # 过滤出文件名，排除文件夹
# file_names = [f for f in all_files if os.path.isfile(os.path.join(folder_path, f))]
#
# # 打印文件名
# for file_name in file_names:
#
#     # 使用函数
#     input_path = os.path.join(folder_path, file_name)
#
#     # 调用wav转csv的函数
#     wav2csv(input_path, showDetail=False, select_model=2, csv_path="./label_test.csv")
