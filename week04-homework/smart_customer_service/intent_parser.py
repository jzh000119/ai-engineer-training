import re
from dataclasses import dataclass, field


@dataclass
class IntentResult:
    """
    意图识别数据类
    """
    intent: str = "unknown"
    confidence: float = 0.0
    matched_rules: [str] = field(default_factory=list)
    extracted_entities: [tuple] = None


class RegexIntentParser:
    """
    正则意图识别器
    """
    def __init__(self):
        # self.patterns = {
        #     'query_order': [
        #         r'查.订单(?:.*([A-Za-z]+\d+))?',  # 查订单AB12345
        #
        #         r'查.订单',
        #
        #     ],
        #     'refund': [
        #         r'退.*订单(?:.*([A-Za-z]+\d+))?',  # 退订单AB12345
        #         r'申请退款.*订单(?:.*([A-Za-z]+\d+))?'
        #     ]
        # }

        self.patterns = {
            'query_order': [
                r'查订单(?:.*?([A-Za-z]+\d+))?', # 查订单AB12345
                r'查.订单(?:.*?([A-Za-z]+\d+))?',
                r'订单号(?:.*?([A-Za-z]+\d+))?'
            ],
            'refund': [
                r'退.*订单(?:.*?([A-Za-z]+\d+))?', # 退订单AB12345
                r'申请退款.*订单(?:.*?([A-Za-z]+\d+))?'
            ]
        }

    def parse(self, text) -> IntentResult:
        """
        解析文本并返回意图结果
        """
        for intent, patterns in self.patterns.items():
            for i, pattern in enumerate(patterns):
                match = re.match(pattern, text)
                if match:
                    return IntentResult(
                        intent=intent,
                        confidence=0.9,
                        matched_rules=[f"regex_{intent}_{i}"],
                        extracted_entities=match.groups() if match.groups() else None
                    )
        return IntentResult()


if __name__ == '__main__':
    test = "查订单AB12345"
    test2 = "查订单"
    test3 = "查订单ABC123"
    parser = RegexIntentParser()
    result = parser.parse(test3)
    print(result)
