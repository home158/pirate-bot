import re
import json

data = [
    "254 +  12/24 yuming730    □ Test",
    "255    12/24 -            □ (本文已被刪除) [yehchge]",
    "256 +  12/24 apeter83     □ 初音",
    "257 +  12/24 imdelight    □ [測試] test",
    "258    12/24 -            □ (本文已被刪除) [whitefox]",
    "259 + 112/24 chienhank    □ [測試] test pics",
    "260    12/24 -            □ (本文已被刪除) [a4537]",
    "261    12/24 -            □ (本文已被刪除) [a4537]",
    "262   112/24 -            □ (本文已被刪除) [wenasd012]",
    "263    12/25 -            □ (本文已被刪除) [ms7689519]",
    "264    12/25 -            □ (本文已被刪除) [copy]",
    "265 +  12/25 TokiwaKurumi □ [測試] ip",
    "266    12/25 -            □ (本文已被刪除) [jason911152]",
    "267 +  12/25 jcjczx       □ [測試]",
    "268 +  12/25 IDL          R: [測試] ip",
    "269 +  12/25 IDL          □ [測試] abcd"
]

# 更新的正則表達式，用於提取文章編號、作者和標題，將 'R:' 視為一組字串
pattern = r'(\d+)\s+.*\s+([^\s]+)\s+([□R:]+)\s*(.*)'

# 提取結果並儲存為 JSON 格式
result = []
for line in data:
    match = re.search(pattern, line)
    if match:  # 檢查是否匹配成功
        article = {
            "id": int(match.group(1)),
            "author": match.group(2),
            "content": match.group(4).strip()  # 將 'R:' 和內容組合起來
        }
        result.append(article)
    else:
        print(f"無法匹配這一行: {line}")  # 可以選擇打印無法匹配的行進行調試

# 輸出為 JSON 字串
json_result = json.dumps(result, ensure_ascii=False, indent=2)
print(json_result)
