import librosa
import numpy as np
import wave
import os

"""
    输入：原始音频地址
    中间处理：将原始音频按照ASR语音识别的格式进行转换
    输出：修改后的音频地址，加了一个_temp的后缀
    如果修改后的音频存在，就不转换了，直接用之前的
"""

def convert_audio_to_wav(input_path):
    """
        将输入的音频文件按照指定API的格式转为WAV格式，并保存为临时文件。
    """
    # 指定变换后的路径名字
    temp_path = input_path.replace(".wav", "_temp.wav")
    file_exists = os.path.exists(temp_path)
    if file_exists:
        print(f"{os.path.basename(temp_path)} already exists!")
        return temp_path
    else:
        # 使用librosa加载音频文件
        audio_array, sr = librosa.load(input_path, sr=16000)  # 设置采样率为16000Hz

        # 将音频转换为单声道
        if audio_array.ndim > 1:
            audio_array = np.mean(audio_array, axis=1)

        # 将音频数据写入WAV文件
        with wave.open(temp_path, 'wb') as wav_file:
            wav_file.setnchannels(1)  # 设置为单声道
            wav_file.setsampwidth(2)  # 设置为16位深度
            wav_file.setframerate(16000)  # 设置采样率为16000Hz

            # 将音频数据写入文件
            # 音频数据需要转换为16位整型
            audio_int16 = np.int16(audio_array * 32767)
            wav_file.writeframes(audio_int16.tobytes())

        print(f"Converted {os.path.basename(input_path)} to {os.path.basename(temp_path)}")
        return temp_path


