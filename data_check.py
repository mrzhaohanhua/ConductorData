import os
import csv


def get_data_files() -> list:
    """
    获取数据文件列表
    :return:
    """
    csv_files = []
    for file_name in os.listdir('.'):
        if os.path.splitext(file_name)[-1] == '.csv':
            csv_files.append(file_name)
    return csv_files


if __name__ == '__main__':
    data_files = get_data_files()  # 获取csv文件名列表
    # data_files.sort()
    for data_file in data_files:
        file = open(data_file, 'rt', encoding='utf-8')  # 打开文件
        csv_reader = csv.reader(file)
        line_index = 0
        for line in csv_reader:
            if line_index > 0:
                item_index = 0
                for item in line:
                    if item_index > 0:
                        try:
                            float(item)  # 尝试将内容转为浮点数
                        except ValueError:
                            if item == '':
                                print(f'"{data_file}" 文件中：第{line_index + 1}行，第{item_index + 1}列数据为空！')
                            else:
                                print(f'"{data_file}" 文件中：第{line_index + 1}行，第{item_index + 1}列数据有误！数据为："{item}"')
                    item_index += 1
            line_index += 1
        file.close()
    print(f"检查完毕！")
