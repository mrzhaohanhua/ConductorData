import csv
from conductor import *


def get_alpha():
    """
    获取电阻温度系数
    :return:
    """
    file_alpha = open("电阻温度系数.csv", 'rt', encoding='utf-8')
    alpha_dic = {}
    for line_ in csv.reader(file_alpha):
        try:
            key = line_[0].strip().upper()
            value = float(line_[1])
            alpha_dic[key] = value
        except ValueError:
            continue
    file_alpha.close()
    return alpha_dic


alphas = get_alpha()
conductors = []  # 导线列表
# 生成钢芯铝绞线
# 读取文件至列表
file_name = "GBT1179\表A.7-1 JLG1A、JLG2A、JLG3A，JL1G1A、JL1G2A、JL1G3A、JL2G1A、JL2G2A、JL2G3A、JL3G1A、JL3G2A、JL3G3A钢芯铝绞线性能.csv"
file = open(file_name, 'rt', encoding='utf-8')
lines = []
for line in csv.reader(file):
    lines.append(line)
al_dic = {'L': 18, 'L1': 19, 'L2': 20, 'L3': 21}
for al in al_dic.keys():
    for g in ['1', '2', '3']:
        for line in lines:
            name = f"J{al}/G{g}A-{line[0]}"
            diameter = line[10].strip()
            core_diameter = line[9].strip()
            r20 = line[al_dic.get(al)].strip()
            alpha = alphas.get(al, 0)
            section = line[4].strip()
            structure = f"s{line[5].strip()}_{line[6].strip()}"
            conductor = Conductor.parse(
                f"{ConductorCompositeSteel.sign_str},{name},{diameter},{core_diameter},{r20},{alpha},{section}, {structure}")
            # print(conductor)
            if conductor is None:
                continue
            conductors.append(conductor)
file.close()

file_name = "GBT1179\表A.7-2 JLG1A、JLG2A、JLG3A，JL1G1A、JL1G2A、JL1G3A、JL2G1A、JL2G2A、JL2G3A、JL3G1A、JL3G2A、JL3G3A钢芯铝绞线性能.csv"
file = open(file_name, 'rt', encoding='utf-8')
lines = []
for line in csv.reader(file):
    lines.append(line)
al_dic = {'L': 15, 'L1': 16, 'L2': 17, 'L3': 18}
for al in al_dic.keys():
    for g in ['1', '2', '3']:
        for line in lines:
            name = f"J{al}/G{g}A-{line[0].strip().upper()}"
            diameter = line[10].strip()
            core_diameter = line[9].strip()
            r20 = line[al_dic.get(al)].strip()
            alpha = alphas.get(al, 0)
            section = line[4].strip()
            structure = f"s{line[5].strip()}_{line[6].strip()}"
            conductor = Conductor.parse(
                f"{ConductorCompositeSteel.sign_str},{name},{diameter},{core_diameter},{r20},{alpha},{section}, {structure}")
            # print(conductor)
            if conductor is None:
                continue
            conductors.append(conductor)
file.close()

file_name = "GBT1179\表A.14 JLLHA1、JL1LHA1、JL2LHA1、JL3LHA1铝合金芯铝绞线性能.csv"
file = open(file_name, 'rt', encoding='utf-8')
lines = []
for line in csv.reader(file):
    lines.append(line)
al_dic = {'L': 12, 'L1': 13, 'L2': 14, 'L3': 15}
for al in al_dic.keys():
    for line in lines:
        name = f"J{al}/LHA1-{line[0].strip().upper()}"
        diameter = line[9].strip()
        outer_section = line[1].strip()
        outer_rou20 = "%.4f" % Conductor.get_rou20(Conductor.conductor_iacs.get(al))
        outer_alpha = alphas.get(al, 0)
        inner_section = line[2].strip()
        inner_rou20 = "%.4f" % Conductor.get_rou20(Conductor.conductor_iacs.get('LHA1'))
        inner_alpha = alphas.get('LHA1', 0)
        structure = f"s{line[4].strip()}_{line[5].strip()}"
        conductor = Conductor.parse(
            f"{ConductorCompositeAluminum.sign_str},{name},{diameter},{outer_section},{outer_rou20},{outer_alpha},{inner_section},{inner_rou20},{inner_alpha},{structure}"
        )
        if conductor is None:
            continue
        conductors.append(conductor)
file.close()

file_name = "GBT1179\表A.15 JLLHA2、JL1LHA2、JL2LHA2、JL3LHA2铝合金芯铝绞线性能.csv"
file = open(file_name, 'rt', encoding='utf-8')
lines = []
for line in csv.reader(file):
    lines.append(line)
al_dic = {'L': 12, 'L1': 13, 'L2': 14, 'L3': 15}
for al in al_dic.keys():
    for line in lines:
        name = f"J{al}/LHA2-{line[0].strip().upper()}"
        diameter = line[9].strip()
        outer_section = line[1].strip()
        outer_rou20 = "%.4f" % Conductor.get_rou20(Conductor.conductor_iacs.get(al))
        outer_alpha = alphas.get(al, 0)
        inner_section = line[2].strip()
        inner_rou20 = "%.4f" % Conductor.get_rou20(Conductor.conductor_iacs.get('LHA2'))
        inner_alpha = alphas.get('LHA2', 0)
        structure = f"s{line[4].strip()}_{line[5].strip()}"
        conductor = Conductor.parse(
            f"{ConductorCompositeAluminum.sign_str},{name},{diameter},{outer_section},{outer_rou20},{outer_alpha},{inner_section},{inner_rou20},{inner_alpha},{structure}"
        )
        if conductor is None:
            continue
        conductors.append(conductor)
file.close()

file_name = "GBT1179\表A.2 JLHA1、JLHA2铝合金绞线性能.csv"
file = open(file_name, 'rt', encoding='utf-8')
lines = []
for line in csv.reader(file):
    lines.append(line)
lh_dic = {'LHA1': 8, 'LHA2': 9}
for lh in lh_dic.keys():
    for line in lines:
        name = f"J{lh}-{line[0].strip().upper()}"
        diameter = line[4].strip()
        r20 = line[lh_dic.get(lh)].strip()
        alpha = alphas.get(lh, 0)
        conductor = Conductor.parse(
            f"{ConductorHomo.sign_str},{name},{diameter},{r20},{alpha}"
        )
        if conductor is None:
            continue
        conductors.append(conductor)
file.close()

file_name = "GBT1179\表A.3 JLHA3、JLHA4铝合金绞线性能.csv"
file = open(file_name, 'rt', encoding='utf-8')
lines = []
for line in csv.reader(file):
    lines.append(line)
lh_dic = {'LHA3': 8, 'LHA4': 9}
for lh in lh_dic.keys():
    for line in lines:
        name = f"J{lh}-{line[0].strip().upper()}"
        diameter = line[4].strip()
        r20 = line[lh_dic.get(lh)].strip()
        alpha = alphas.get(lh, 0)
        conductor = Conductor.parse(
            f"{ConductorHomo.sign_str},{name},{diameter},{r20},{alpha}"
        )
        if conductor is None:
            continue
        conductors.append(conductor)
file.close()

# 输出至文件
output_file_name = "conductor_electrical_data.txt"
output_file = open(output_file_name, 'wt', encoding='utf-8')
for conductor in conductors:
    output_file.write(f"{str(conductor)}\n")
output_file.close()
print("end")
