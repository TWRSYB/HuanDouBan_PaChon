class StrToContainer:
    def __init__(self, the_str):
        self.the_str = the_str
        self.index = 0

    def get_monomer(self, close_symbol=''):
        """
        获取一个单体: dict 或 list 或 str
        :param close_symbol: 结束符号, 在非预期开头时, 使用该符号作为结尾返回一个字符串
        :return:
        """
        self.pass_empty()
        if self.the_str[self.index] == '{':
            new_dict = {}
            self.add_entry_for_dict(new_dict)
            # print(f"当前index: {self.index}, 获取到一个dict: {new_dict}")
            return new_dict
        elif self.the_str[self.index] == '[':
            new_list = []
            self.add_element_for_list(new_list)
            # print(f"当前index: {self.index}, 获取到一个list: {new_list}")
            return new_list
        else:
            new_str = ''
            if self.the_str[self.index] == '"':
                self.index += 1
                new_str = self.get_quote_str(new_str, '"')
                # print(f'当前index: {self.index}, 获取到一个"str": {new_str}')
                self.index += 1
            elif self.the_str[self.index] == "'":
                self.index += 1
                new_str = self.get_quote_str(new_str, "'")
                # print(f"当前index: {self.index}, 获取到一个'str': {new_str}")
                self.index += 1
            else:
                new_str = self.get_no_quote_str(new_str, close_symbol)
                # print(f"当前index: {self.index}, 获取到一个str: {new_str}")
            return new_str

    def add_entry_for_dict(self, new_dict):
        """
        在获取单体时遇到 { 则会进入填充 dict 的逻辑, 递归为 dict 添加元素, 直到遇到 } 结束逻辑
        :param new_dict:
        :return:
        """
        self.index += 1
        self.pass_empty()
        if self.get_close('}'):
            self.index += 1
            return new_dict
        else:
            key = '' if self.get_close(':') else self.get_monomer(':')
            self.index += 1
            value = '' if self.get_close(',') else self.get_monomer([',', '}'])
            new_dict[key] = value
            if self.get_close('}'):
                self.index += 1
                return new_dict
            self.add_entry_for_dict(new_dict)

    def add_element_for_list(self, new_list):
        """
        在获取单体时遇到 [ , 则会进入填充 list 的逻辑, 递归为 list 添加元素, 直到遇到 ] 结束逻辑
        :param new_list: 新的列表
        :return: 新的列表
        """
        self.index += 1
        self.pass_empty()
        if self.get_close(']'):
            self.index += 1
            return new_list
        else:
            element = '' if self.get_close(',') else self.get_monomer([',', ']'])
            new_list.append(element)
            if self.get_close(']'):
                self.index += 1
                return new_list
            self.add_element_for_list(new_list)

    def get_quote_str(self, new_str, quote):
        """
        获取单体时, 如果是以引号开头, 则开启获取字符串逻辑, 拼接字符串, 直到遇到下一个对应的引号结束
        :param quote: 引号 ' 或 "
        :param new_str:
        :return:
        """
        if self.get_close(quote):
            return new_str.strip()
        else:
            new_str = new_str + self.the_str[self.index]
            self.index += 1
            return self.get_quote_str(new_str, quote)

    def get_no_quote_str(self, new_str, end_symbol=[',', ' ', '}', ']']):
        """
        获取单体时, 如果单体不是 dict 或 list 且不是以引号开头, 则开启获取字符串逻辑, 拼接字符串, 直到遇到下一个对应结束符号
        :param end_symbol: 结束符号
        :param new_str:
        :return:
        """
        if self.get_close(end_symbol):
            return new_str.strip()
        else:
            new_str = new_str + self.the_str[self.index]
            self.index += 1
            return self.get_no_quote_str(new_str, end_symbol)

    def get_close(self, symbol):
        """
        用于判断是否到达结束符号, 用于调用逻辑的结束判断
        :param symbol: 结束符号
        :return: bool
        """
        if self.the_str[self.index] in symbol:
            if self.the_str[self.index - 1] == '\\':
                if self.the_str[self.index - 2] == '\\':
                    if self.the_str[self.index - 3] == '\\':
                        return False
                    else:
                        return True
                else:
                    return False
            else:
                return True
        else:
            return False

    def pass_empty(self):
        """
        在获取下一个单体前 跳过空格
        :return: None
        """
        if self.the_str[self.index] in [' ']:
            self.index += 1
            self.pass_empty()


def tran_dict_by_param_dict(the_dict: dict, param_dict):
    for key, value in the_dict.items():
        print(key, type(value), value)
        if isinstance(value, str):
            if value and len(value) < 3:
                if value in param_dict.keys():
                    the_dict[key] = param_dict[value]
        elif isinstance(value, dict):
            tran_dict_by_param_dict(value, param_dict)
        elif isinstance(value, list):
            for sub in value:
                tran_dict_by_param_dict(sub, param_dict)