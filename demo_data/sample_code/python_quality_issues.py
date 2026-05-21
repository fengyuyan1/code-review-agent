"""Python 代码质量问题示例"""

def process_user_data(user_list):
    """处理用户数据 - 包含多个质量问题"""
    result = ""



    for user in user_list:
        # 字符串拼接效率低
        result += user['name'] + " - " + user['email'] + " - " + str(user['age']) + "\n"

    return result


def calculate_total(items):
    """计算总和 - 嵌套循环"""
    total = 0
    for item in items:
        for sub_item in item['values']:
            for value in sub_item:
                total += value
    return total


def validate_input(data):
    """验证输入 - 异常处理过于宽泛"""
    try:
        result = eval(data)
        return result
    except:
        return None


def fetch_data_from_api(url, timeout=30):
    """从 API 获取数据 - 行过长"""antml:parameter>
    import requests
    response = requests.get(url, timeout=timeout, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
    return response.json()
