import operator
from pathlib import Path
from langgraph.constants import START, END
from typing_extensions import TypedDict
from typing import Annotated
from langgraph.graph import StateGraph
from intent_parser import RegexIntentParser
from draw import draw_graph_png

class GraphState(TypedDict):
    question: str # 用户问题
    tool_calls: list # 工具列表
    order_id: str # 订单号
    response: str # 返回结果


def query_order(order_id):
    """
    订单查询 工具
    :param order_id:
    :return:
    """
    order_id = str(order_id).strip()
    status = {
            "SF123456": {
            "status": "运输中",
            "location": "北京分拣中心",
            "estimated_delivery": "2024-01-15"
        },
        "YT789012": {
            "status": "已签收",
            "location": "上海浦东",
            "delivery_date": "2024-01-10"
        }
    }
    if order_id in status:
        info = status[order_id]
        if 'estimated_delivery' in info:
            return f"快递单号: {order_id}, 状态: {info['status']}, 位置: {info['location']}, 预计送达: {info['estimated_delivery']}"
        else:
            return f"快递单号: {order_id}, 状态: {info['status']}, 位置: {info['location']}, 送达日期: {info['delivery_date']}"
    else:
        return f"未找到快递单号 {order_id} 的信息"


def intent(state):
    text = state['question']
    parser = RegexIntentParser()
    result = parser.parse(text)
    print("result :", result)
    state['response'] = result
    state['order_id'] = result.extracted_entities[0] if result.extracted_entities else None
    return state


def route_by_order_status(state):
    """
    条件边，判断是否有订单号
    :param state:
    :return:
    """
    result = state['order_id']
    if result is None:
        return "ROUTE_NO_ORDER"
    else:
        return "ROUTE_HAS_ORDER"

def order_not_found(state):
    """"
    处理没有订单号的情况
    """
    print("没有在您的问题里面找到订单号， 请手动输入订单号，以便帮您继续查询。")
    state['order_id'] = input("请输入单号：")
    return state

def order_found(state):
    """
    处理存在订单号的情况
    :param state:
    :return:
    """
    order_func = state['tool_calls'][0]
    state['response'] = order_func(state['order_id'])
    return state


def create_order_workflow():
    """
    创建并编译 LangGraph 工作流
    :return:
    """
    workflow = StateGraph(GraphState)

    workflow.add_node("intent", intent)
    workflow.add_node("order_not_found", order_not_found)
    workflow.add_node("order_found", order_found)

    workflow.set_entry_point("intent")

    workflow.add_edge(START, "intent")

    # 添加了订单号后，跳转到 订单号查询节点
    workflow.add_edge("order_not_found", "order_found")

    # 添加条件边
    workflow.add_conditional_edges(
        "intent",
        route_by_order_status,
        {
            "ROUTE_NO_ORDER": "order_not_found",
            "ROUTE_HAS_ORDER": "order_found"
        }
    )
    workflow.add_edge("order_found", END)
    return workflow.compile() # 图编译


def main():
    graph = create_order_workflow()
    print("---测试用例 1： 有订单号---")
    result1 = graph.invoke({
        "question": "查订单SF123456",
        "tool_calls": [query_order],
        "order_id": "",
        "response": ""
    })
    print("最终结果 : ", result1['response'])

    # 可输入单号：YT789012   SF123456
    print("---测试用例 2： 无订单号---")
    result2 = graph.invoke({
        "question": "查订单",
        "tool_calls": [query_order],
        "order_id": "",
        "response": ""
    })
    print("最终结果 : ", result2['response'])

    # 画图
    file_path = Path('/Users/jzh/PycharmProjects/work_new/0917_homework/graph.png')
    draw_graph_png(file_path, graph)

if __name__ == '__main__':
    main()
