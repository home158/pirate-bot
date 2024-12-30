import re

# 定義關鍵字
PTTMAIL_KEYWORDS_ONLY = '推薦人今網|推薦今網|今網推薦|徵求今網|徵今網推薦人|徵今網業務|徵求一位今網推薦|測試|簽名|周杰倫|初音|問題'
PTTMAIL_KEYWORDS_DENY = '已徵得|已徵到'

def validate_string(input_string):
    # 移除字串中所有的空白（包括前後及中間）
    cleaned_string = re.sub(r'\s+', '', input_string)

    # 檢查是否符合關鍵字 ONLY
    only_match = re.search(PTTMAIL_KEYWORDS_ONLY, cleaned_string)
    # 檢查是否包含排除關鍵字 DENY
    deny_match = re.search(PTTMAIL_KEYWORDS_DENY, cleaned_string)
    
    # 如果符合 ONLY 且不包含 DENY，返回 True
    if only_match and not deny_match:
        return True
    return False


# 測試範例
test_strings = [
    "徵求今網推薦人", 
    "已徵得 今網推薦人",
    "今網推薦人", 
    "測試周杰倫徵今網推薦", 
    "徵求一位今網推薦已徵到",
    "徵求一位今網推薦人",
    "徵求一位推薦人今網", 
    "徵求一位推薦人 今網", 
    "徵求一位推薦人(今網)", 
]

for test in test_strings:
    result = validate_string(test)
    print(f"'{test}' -> {result}")
