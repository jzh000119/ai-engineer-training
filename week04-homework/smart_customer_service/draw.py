from langchain_core.runnables.graph import MermaidDrawMethod


def draw_graph_png(file_path, graph):
    """
    生成图的 png 文件
    :param file_path:
    :param graph:
    :return:
    """
    image_data = graph.get_graph().draw_mermaid_png(draw_method=MermaidDrawMethod.PYPPETEER)
    file_path.write_bytes(image_data)
