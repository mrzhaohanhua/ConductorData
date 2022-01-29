from math import pi, sqrt


def get_resistance(r20: float, alpha: float, temperature: float) -> float:
    """
    计算指定温度下的直流电阻（Ω/m）
    :param r20: 20℃时的直流电阻（Ω/m）
    :param alpha: 电阻温度系数
    :param temperature: 计算温度（℃）
    :return: 返回指定温度下的直流电阻
    """
    return r20 * (1 + alpha * (temperature - 20))


class Conductor(object):
    """
    导线的基础类
    """
    __slots__ = ('name', 'diameter')
    sign_str = ''
    IACS = 58000000  # IACS电导率 S/m
    conductor_iacs = {'L3': 0.625,
                      'L2': 0.62,
                      'L1': 0.615,
                      'L': 0.61,
                      'LHA4': 0.585,
                      'LHA3': 0.57,
                      'LHA2': 0.53,
                      'LHA1': 0.525,
                      'LB40': 0.40,
                      'LB35': 0.35,
                      'LB27': 0.27,
                      'LB20A': 0.203}  # 常见导体对应的IACS百分比

    def __init__(self, name: str, diameter: float):
        """
        导线类的初始化方法
        :param name: 导线型号
        :param diameter: 导线外径（mm）
        """
        self.name = name
        self.diameter = diameter

    def get_rdc(self, temperature: float) -> float:
        """
        计算指定温度下的直流电阻
        :param temperature:指定温度（℃）
        :return:
        """
        pass

    def get_k(self, intensity: float, fq: float, temperature: float) -> float:
        """
        计算交直流电阻比
        :param intensity:导线电流（A）
        :param fq: 频率（Hz）
        :param temperature:导线温度（℃）
        :return:
        """
        pass

    @staticmethod
    def parse(text: str):
        """
        由字符串生成各绞线类的实例对象
        :param text: 文本字符串
        :return:返回某一绞线类的实例对象
        """
        args = text.split(',')  # 将text拆分为列表
        sign = args[0].strip().upper()  # 标识符大写
        if sign == ConductorHomo.sign_str:  # ConductorHomo
            return ConductorHomo.parse(args)
        elif sign == ConductorCompositeAluminum.sign_str:  # 对象为ConductorCompositeAluminum
            return ConductorCompositeAluminum.parse(args)
        elif sign == ConductorCompositeSteel.sign_str:  # 对象为ConductorCompositeSteel
            return ConductorCompositeSteel.parse(args)
        else:
            return None

    @classmethod
    def get_rou20(cls, iacs_percent) -> float:
        """
        根据IACS系数计算电阻率 Ω·mm2/m
        :param iacs_percent:50%IACS时，参数为0.5
        :return:
        """
        try:
            return 1 / (float(iacs_percent) * cls.IACS) * 1000000
        except ValueError:
            return 0


class ConductorHomo(Conductor):
    """
    单一材质绞线 homogeneous conductor
    """
    __slots__ = ('name', 'diameter', 'r20', 'alpha')
    sign_str = 'HOMO'

    def __init__(self, name: str, diameter: float, r20: float, alpha: float):
        """
        初始化实例对象
        :param name:导线型号
        :param diameter: 导线外径（mm）
        :param r20: 20℃时导线直流电阻率（Ω/km）
        :param alpha: 电阻温度系数1/℃
        """
        super(ConductorHomo, self).__init__(name, diameter)
        self.r20 = r20
        self.alpha = alpha

    def get_rdc(self, temperature: float) -> float:
        """
        计算指定温度的直流电阻Rdc（Ω/km）
        :param temperature: 计算温度（℃）
        :return: 返回指定温度的直流电阻（Ω/km）
        """
        return get_resistance(self.r20, self.alpha, temperature)

    def get_k(self, intensity: float, fq: float, temperature: float) -> float:
        """
        计算交直流电阻比
        :param intensity: 导线电流（A）
        :param fq: 频率（Hz）
        :param temperature:导线温度（℃）
        :return:返回交直流电阻比
        """
        x = 0.01 * sqrt(8 * pi * fq / self.get_rdc(temperature))
        k1 = 0.99609 + 0.018578 * x - 0.030263 * pow(x, 2) + 0.020735 * pow(x, 3)
        k2 = 1
        return k1 * k2

    def __eq__(self, other) -> bool:
        """
        重载==运算
        :param self:
        :param other:
        :return:
        """
        return \
            type(self) == type(other) and \
            self.name == other.name and \
            self.diameter == other.diameter and \
            self.r20 == other.r20 and \
            self.alpha == other.alpha

    def __str__(self):
        """
        重载__str__方法
        :return:
        """
        return self.sign_str.upper() + ",\t" + self.name + ",\t" + str(self.diameter) + ",\t" + str(
            self.r20) + ",\t" + str(
            self.alpha)

    @classmethod
    def parse(cls, args: list):
        """
        由参数列表生成实例对象
        :param args:参数列表
        :return:返回实例对象
        """
        if len(args) != 5:  # 参数列表内元素数量不对
            return None
        name = str(args[1]).strip().upper()  # 读取name参数
        if name == '':  # 绞线型号为空时返回None
            return None
        try:
            diameter = float(str(args[2]).strip())
            r20 = float(str(args[3]).strip())
            alpha = float(str(args[4]).strip())
        except ValueError:  # 转换数字有异常，则返回None
            return None
        if diameter * r20 * alpha == 0:  # 参数有0值，则返回None
            return None
        return cls(name, diameter, r20, alpha)


class ConductorCompositeAluminum(Conductor):
    """
    内层为含铝材质的复合材质导线 Composite Conductor with Aluminum
    内外不同材质均有电流通过的导体模型
    """
    __slots__ = ('name', 'diameter',
                 'outer_lambda', 'outer_section', 'outer_rou20', 'outer_alpha',
                 'inner_lambda', 'inner_section', 'inner_rou20', 'inner_alpha',
                 'structure')
    sign_str = 'COMP_AL'
    structures = {'s4_3': (1.51, 1.51),
                  's12_7': (2.17, 1.29),
                  's30_7': (2.23, 1.29),
                  's54_7': (2.31, 1.29),
                  's18_19': (2.49, 1.58),
                  's42_19': (2.44, 1.58),
                  's72_19': (2.45, 1.58),
                  's24_37': (2.67, 1.84),
                  's42_37': (2.44, 1.84),
                  's54_37': (2.57, 1.84)}  # key为导线结构 s铝线根数_铝合金根数 value(铝增量,铝合金增量) GB1179-2017表5

    @classmethod
    def __get_lambda(cls, structure: str) -> tuple | None:
        return cls.structures.get(structure, None)

    def __init__(self, name: str, diameter: float,
                 outer_section: float, outer_rou20: float, outer_alpha: float,
                 inner_section: float, inner_rou20: float, inner_alpha: float,
                 structure: str):
        """
        初始化实例对象
        :param name:导线型号
        :param diameter: 导线外径（mm）
        :param outer_section: 外层导体截面积（mm2）
        :param outer_rou20: 外层导体电阻率（Ω/mm2/km）
        :param outer_alpha: 外层导体电阻温度系数
        :param inner_section:内层导体截面积（mm）
        :param inner_rou20:内层导体电阻率（Ω/mm2/km）
        :param inner_alpha:内层导体电阻温度系数
        :param structure:导线结构
        """
        super(ConductorCompositeAluminum, self).__init__(name, diameter)
        lam = ConductorCompositeAluminum.__get_lambda(structure)
        self.outer_lambda = 1 + lam[0] / 100
        self.outer_section = outer_section
        self.outer_rou20 = outer_rou20
        self.outer_alpha = outer_alpha
        self.inner_lambda = 1 + lam[1] / 100
        self.inner_section = inner_section
        self.inner_rou20 = inner_rou20
        self.inner_alpha = inner_alpha
        self.structure = structure

    def get_rdc(self, temperature: float) -> float:
        """
        计算指定温度的直流电阻Rdc（Ω/km）
        :param temperature: 计算温度（℃）
        :return:返回指定温度的直流电阻（Ω/km）
        """
        r1 = self.inner_rou20 * self.inner_lambda / self.inner_section
        r2 = self.outer_rou20 * self.outer_lambda / self.outer_section
        rdc1 = get_resistance(r1, self.inner_alpha, temperature)
        rdc2 = get_resistance(r2, self.outer_alpha, temperature)
        return 1 / (1 / rdc1 + 1 / rdc2)

    def get_k(self, intensity: float, fq: float, temperature: float) -> float:
        """
        计算交直流电阻比
        :param intensity: 导线电流（A）
        :param fq: 频率（Hz）
        :param temperature:导线温度（℃）
        :return:返回交直流电阻比
        """
        x = 0.01 * sqrt(8 * pi * fq / self.get_rdc(temperature))
        k1 = 0.99609 + 0.018578 * x - 0.030263 * pow(x, 2) + 0.020735 * pow(x, 3)
        k2 = 1
        return k1 * k2

    def __eq__(self, other):
        """
        重载==运算
        :param other:
        :return:
        """
        return \
            type(self) == type(other) and \
            self.name == other.name and \
            self.diameter == other.diameter and \
            self.outer_section == other.outer_section and \
            self.outer_rou20 == other.outer_rou20 and \
            self.outer_alpha == other.outer_alpha and \
            self.inner_section == other.inner_section and \
            self.inner_rou20 == other.inner_rou20 and \
            self.inner_alpha == other.inner_alpha and \
            self.structure == other.structure

    def __str__(self):
        """
        重载__str__方法
        :return:
        """

        return self.sign_str.upper() + ",\t" + self.name + ",\t" + str(
            self.diameter) + ",\t" + str(
            self.outer_section) + ",\t" + str(
            self.outer_rou20) + ",\t" + str(
            self.outer_alpha) + ",\t" + str(
            self.inner_section) + ",\t" + str(
            self.inner_rou20) + ",\t" + str(
            self.inner_alpha) + ",\t" + self.structure

    @classmethod
    def parse(cls, args: list):
        if len(args) != 10:
            return None
        name = str(args[1]).strip().upper()  # 读取name参数
        if name == '':  # 绞线型号为空时返回None
            return None
        try:
            diameter = float(str(args[2]).strip())
            outer_section = float(str(args[3]).strip())
            outer_rou20 = float(str(args[4]).strip())
            outer_alpha = float(str(args[5]).strip())
            inner_section = float(str(args[6]).strip())
            inner_rou20 = float(str(args[7]).strip())
            inner_alpha = float(str(args[8]).strip())
        except ValueError:  # 转换数字有异常，则返回None
            return None
        if diameter * \
                outer_section * outer_rou20 * outer_alpha * \
                inner_section * inner_rou20 * inner_alpha == 0:  # 参数中含有 0 则返回None
            return None
        structure = str(args[9]).strip().lower()
        if structure not in cls.structures.keys():
            return None
        return cls(name, diameter,
                   outer_section, outer_rou20, outer_alpha,
                   inner_section, inner_rou20, inner_alpha,
                   structure)


class ConductorCompositeSteel(Conductor):
    """
    内层为钢材质的复合材质导线 Composite Conductor with Steel
    内外不同材质，内层为钢材质，由于集肤效应内层无电流通过的导体模型
    """

    __slots__ = ('name', 'diameter', 'core_diameter', 'r20', 'alpha', 'section',
                 'structure', 'surface_layers')
    sign_str = 'COMP_ST'
    # structure为绞线结构的字典，字典键为绞线结构代码，字典值为绞线外层导体层数
    structures = {'s6_1': 1,
                  's7_7': 1,
                  's12_7': 1,
                  's18_1': 2,
                  's22_7': 2,
                  's24_7': 2,
                  's26_7': 2,
                  's30_7': 2,
                  's42_7': 3,
                  's45_7': 3,
                  's48_7': 3,
                  's54_7': 3,
                  's72_7': 4,
                  's76_7': 4,
                  's84_7': 4,
                  's30_19': 2,
                  's54_19': 2,
                  's72_19': 4,
                  's76_19': 4,
                  's84_19': 4,
                  's88_19': 4}

    def __init__(self, name: str, diameter: float, core_diameter: float, r20: float, alpha: float, section: float,
                 structure: str):
        super(ConductorCompositeSteel, self).__init__(name, diameter)
        self.core_diameter = core_diameter
        self.r20 = r20
        self.alpha = alpha
        self.section = section
        if structure in ConductorCompositeSteel.structures:
            self.structure = structure
            self.surface_layers = ConductorCompositeSteel.structures.get(structure, 0)
        else:
            self.structure = 'unknown'
            self.surface_layers = 0

    def get_rdc(self, temperature: float) -> float:
        """
        计算指定温度的直流电阻Rdc（Ω/km）
        :param temperature: 计算温度（℃）
        :return:返回指定温度的直流电阻（Ω/km）
        """
        return get_resistance(self.r20, self.alpha, temperature)

    def get_k(self, intensity: float, fq: float, temperature: float) -> float:
        """
        计算交直流电阻比
        :param intensity: 导线电流（A）
        :param fq: 频率（Hz）
        :param temperature:导线温度（℃）
        :return:返回交直流电阻比
        """
        x = 0.01 * (self.diameter + 2 * self.core_diameter) / (self.diameter + self.core_diameter) * sqrt(
            8 * pi * fq * (self.diameter - self.core_diameter) / (
                    self.diameter + self.core_diameter) / self.get_rdc(
                temperature))
        k1 = 0.99609 + 0.018578 * x - 0.030263 * pow(x, 2) + 0.020735 * pow(x, 3)

        if self.surface_layers >= 3 and self.surface_layers % 2 == 0:
            # 当绞线外层导体层数为3层以上的奇数时
            y = intensity / self.section
            k2 = 0.99947 + 0.028895 * y - 0.0059348 * pow(y, 2) + 0.00042259 * pow(y, 3)
        else:
            k2 = 1
        return k1 * k2

    def __eq__(self, other):
        """
        重载==运算
        :param other:
        :return:
        """
        return \
            type(self) == type(other) and \
            self.name == other.name and \
            self.diameter == other.diameter and \
            self.core_diameter == other.core_diameter and \
            self.r20 == other.r20 and \
            self.alpha == other.alpha and \
            self.section == other.section and \
            self.structure == other.structure

    def __str__(self):
        """
        重载__str__方法
        :return:
        """
        return self.sign_str.upper() + ",\t" + self.name + ",\t" + str(
            self.diameter) + ",\t" + str(
            self.core_diameter) + ",\t" + str(
            self.r20) + ",\t" + str(
            self.alpha) + ",\t" + str(
            self.section) + ",\t" + self.structure

    @classmethod
    def parse(cls, args: list):
        """
        由参数列表生成实例对象
        :param args: 参数列表
        :return:
        """
        if len(args) != 8:  # 参数列表内元素数量不对
            return None
        name = str(args[1]).strip().upper()  # 读取name参数
        if name == '':  # 绞线型号为空时返回None
            return None
        try:
            diameter = float(str(args[2]).strip())
            core_diameter = float(str(args[3]).strip())
            r20 = float(str(args[4]).strip())
            alpha = float(str(args[5]).strip())
            section = float(str(args[6]).strip())
        except ValueError:  # 转换数字有异常，则返回None
            return None
        structure = str(args[7]).strip().lower()  # structure永远小写
        if structure not in cls.structures.keys():  # 判断structure是否合法
            return None
        if diameter * core_diameter * r20 * alpha * section == 0:  # 参数中含有 0 则返回None
            return None
        return cls(name, diameter, core_diameter, r20, alpha, section, structure)
