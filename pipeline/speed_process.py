import librosa
import soundfile as sf
import numpy as np
import os
from wav2text_sum import recognize_speech, recognize_speech_all
from pre_wav import convert_audio_to_wav

##语速调整
def recognize_segment(segment, sr):
    temp_filename = "temp_segment.wav"
    temp_filename_segment = 'temp_segment_temp.wav'

    sf.write(temp_filename, segment, sr)

    try:
        # 语音转文本
        input_path = convert_audio_to_wav(temp_filename)
        text = recognize_speech(input_path, False, 0)
        print(f"识别结果: {text}")
        if os.path.exists(temp_filename_segment):
          os.remove(temp_filename_segment)
        return text
    except:
        print("无法识别该段音频")

def audio_to_text_by_segments(audio_file, top_db=50):
    y, sr = librosa.load(audio_file, sr=None) 
    segments = librosa.effects.split(y, top_db=top_db) 

    full_text = []  # 存储所有识别的文本
    for start, end in segments:
        segment = y[start:end] 
        text = recognize_segment(segment, sr)  
        if text: 
            full_text.append(text)

    return " ".join(full_text)


def speed_by_segment(audio_file, output_file, target_speed=10, top_db=50):
    print("正在进行语音识别...")
    text = audio_to_text_by_segments(audio_file, top_db)
    print(f"完整识别结果: {text}")

    # 加载音频
    y, sr = librosa.load(audio_file, sr=None)
    segments = librosa.effects.split(y, top_db=top_db)
    print(f"语音段数: {len(segments)}")

    processed_audio = [] 

    for start, end in segments:
        segment = y[start:end]
        speed = len(text) / librosa.get_duration(y=segment, sr=sr)  # 计算实际语速
        print(f"语音段语速: {speed:.2f} 帧/秒")

        # 如果语速不在标准范围内，则调整
        if speed > 3.3:
            speed_factor = speed / target_speed
            print(speed_factor)
            speed_factor = abs(speed_factor)
            adjusted_segment = librosa.effects.time_stretch(y=segment, rate=speed_factor)
            processed_audio.append(adjusted_segment)
        elif speed < 2.7:
            speed_factor = target_speed / speed
            print(speed_factor)
            speed_factor = abs(speed_factor)
            adjusted_segment = librosa.effects.time_stretch(y=segment, rate=speed_factor)
            processed_audio.append(adjusted_segment)
        else:
            print("语速在标准范围内，无需调整。")
            processed_audio.append(segment)

    # 拼接所有处理后的语音段
    output_audio = np.concatenate(processed_audio, axis=0)

    # 保存处理后的音频
    sf.write(output_file, output_audio, sr)
    print(f"处理后的音频已保存至: {output_file}")





## 语调调整
import librosa
import numpy as np
import soundfile as sf

def vad_segments(y, sr, top_db=30):
    intervals = librosa.effects.split(y, top_db=top_db)
    return intervals

def compute_average_pitch_yin(y, sr, fmin=50, fmax=400):
    pitches = librosa.yin(y, fmin=fmin, fmax=fmax, sr=sr)
    avg_pitch = np.median(pitches)
    return avg_pitch

def calculate_n_steps(avg_pitch, target_pitch_range):
    # 计算目标音高范围
    min_target_pitch = avg_pitch - target_pitch_range
    max_target_pitch = avg_pitch + target_pitch_range

    # 计算将音高降低或升高到目标范围的 n_steps
    n_steps_down = 12 * np.log2(min_target_pitch / avg_pitch)
    n_steps_up = 12 * np.log2(max_target_pitch / avg_pitch)

    # 返回绝对值较小的 n_steps，以保持在目标范围内
    n_steps = n_steps_down if abs(n_steps_down) < abs(n_steps_up) else n_steps_up
    return n_steps

def apply_uniform_pitch_shift(y, sr, n_steps):
    # 对音频应用统一的音高调整
    adjusted_y = librosa.effects.pitch_shift(y = y, sr = sr, n_steps=n_steps)
    return adjusted_y

def pitch_by_segment(input_path, output_path, target_pitch_range=5, top_db=30):
    y, sr = librosa.load(input_path)

    speech_intervals = vad_segments(y, sr, top_db=top_db)

    voiced_audio = np.concatenate([y[start:end] for start, end in speech_intervals])
    avg_pitch = compute_average_pitch_yin(voiced_audio, sr)
    print(avg_pitch)

    n_steps = calculate_n_steps(avg_pitch, target_pitch_range)
    print(n_steps)

    # 创建一个数组存储处理后的音频
    smoothed_audio = np.copy(y)

    # 仅对有语音的片段应用音高调整
    for start, end in speech_intervals:
        smoothed_audio[start:end] = apply_uniform_pitch_shift(y[start:end], sr, n_steps)

    # 保存处理后的音频文件
    sf.write(output_path, smoothed_audio, sr)



