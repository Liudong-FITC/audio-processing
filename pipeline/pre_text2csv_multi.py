import csv
import os

def text2csv(input_path, result_text, csv_filename="./label.csv"):
    # 输入变量
    input_path = input_path.replace("_temp.wav", ".wav")
    video_id = os.path.basename(os.path.dirname(input_path))
    clip_id = os.path.splitext(os.path.basename(input_path))[0]
    text = result_text

    # 默认值
    label = 0
    label_T = 0
    label_A = 0
    label_V = 0
    annotation = "Positive"
    mode = "test"

    # 检查文件是否存在
    if not os.path.exists(csv_filename):
        # 文件不存在，创建文件并写入标题行和数据行
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["video_id", "clip_id", "text", "label", "label_T", "label_A", "label_V", "annotation", "mode"])
            writer.writerow([video_id, clip_id, text, label, label_T, label_A, label_V, annotation, mode])
        print(f"CSV file '{csv_filename}' has been created with the provided data.")
    else:
        # 文件存在，以追加模式打开文件并写入数据行
        with open(csv_filename, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([video_id, clip_id, text, label, label_T, label_A, label_V, annotation, mode])
        print(f"Data has been appended to CSV file '{csv_filename}'.")

# 示例调用
# text2csv("path/to/input.wav", "This is a sample text.")