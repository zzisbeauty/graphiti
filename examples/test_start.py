# test_my_schema.py
import os, sys

def find_project_root(marker_files=('pyproject.toml', '.git', 'requirements.txt')):
    path = os.path.abspath(__file__)
    while path != os.path.dirname(path):
        if any(os.path.exists(os.path.join(path, marker)) for marker in marker_files):
            return path
        path = os.path.dirname(path)
    raise RuntimeError("Project root not found.")

project_root = find_project_root()
if project_root not in sys.path:
    sys.path.insert(0, project_root)


import asyncio  
from datetime import datetime, timezone  
from graphiti_core.graphiti import Graphiti  
from examples.test_server_config import embedder
from examples.test_server_config import llm_client
from examples.test_server_config import NEO4J_URL,NEO4J_USER,NEO4J_PASSWD
from examples.test_selfdefine_schema import entity_types,edge_type_map,edge_types



# =============================== test data

# test data
with open('/home/graphiti/examples/data/1.红楼梦.txt','r',encoding='utf-8') as f:
    hlm_data = f.read()
    print(len(hlm_data)) # 674178 个字符?  1 token = 3~4 个字符
    print(hlm_data[:500].replace(" ", "").replace('\n','').replace('\r',''))

print('*' * 50)

# with open('/home/graphiti/examples/data/从百草园到三味书屋.txt','r',encoding='utf-8', errors='ignore') as f:
#     bcy_data = f.read()
#     print(bcy_data[:100])


bingfabingxing = """ 并行（Parallel）是真正的同时发生，指多个任务在同一时刻在不同的处理器或核上同时执行，是真实意义上的同时进行。
而并发（Concurrent）只是指在同一时间段内多个任务都在处理，但它们不是在同一时间点上同时执行，而是通过任务的快速切换或时间片轮转等方式，让多个任务看起来像是在同时进行，其实是在交替进行。
总结来说，并行是物理上的同时进行，并发是逻辑上的同时进行，只有在多核或多处理器的情况下才能实现真正的并行，而在单核情况下只能实现并发.
"""

bingfabingxing_buchong = """
并发和并行在多核处理器中的表现区别

在多核处理器中，并发和并行的表现区别主要体现为：

- 并发（Concurrency）指的是多个任务在同一时间段内都处于运行状态，但在微观上这些任务不是同时执行的，它们在同一核上通过时间片快速切换交替进行。即使是多核，多任务也可以表现为并发，如果任务的执行依赖调度切换或共享资源时。这种方式能够有效利用单个处理器的时间，实现资源的高效使用。

- 并行（Parallelism）则是多个任务在不同的处理器核心或多个处理器上同时执行，在同一时间点上多线程或多进程真正实现同时运行。多核处理器允许多个任务并行处理，每个核心独立执行自己的任务，互不干扰，提高了处理速度和效率。

总结对比：

| 特性       | 并发                          | 并行                          |
|------------|-------------------------------|-------------------------------|
| 运行机制   | 多任务快速切换，逻辑上同时进行 | 多任务物理上同时进行           |
| 依赖硬件   | 适用于单核和多核               | 依赖于多核或多处理器           |
| 时间表现   | 同一时间段内交错执行           | 同一时间点真正同时执行         |
| 调度方式   | 由操作系统调度时间片           | 由多个核心同时独立执行         |
| 适用场景   | I/O密集型、线程间切换          | 计算密集型、独立任务并行处理   |

在多核处理器环境下，程序设计既可以利用并发特性来提升响应性和资源利用，也可以通过并行特性提高计算效率，二者常结合使用以提升整体性能.[1][2][3][4][5][6][7][8][9]

[1](https://www.cnblogs.com/wwwbdabc/p/10861680.html)
[2](https://developer.aliyun.com/article/904477)
[3](https://blog.csdn.net/qq_40586164/article/details/104954028)
[4](https://www.eet-china.com/mp/a305299.html)
[5](https://www.jos.org.cn/josen/article/html/5021)
[6](https://blog.csdn.net/zhzjn/article/details/142478420)
[7](https://www.itzhai.com/columns/faqs/juc/concurrency-vs-parallelism.html)
[8](https://blog.51cto.com/u_15558033/5664774)
[9](https://juejin.cn/post/7290837333926625299)
"""

from graphiti_core.nodes import EpisodeType

async def main():
    # 初始化 Graphiti  
    graphiti = Graphiti(uri=NEO4J_URL, user=NEO4J_USER, password=NEO4J_PASSWD,llm_client = llm_client, embedder=embedder)

    # 构建索引  
    await graphiti.build_indices_and_constraints()  
 
    # 测试添加数据
    """ 完全可以根据当前的数据信息自定义 source_description。这个参数的设计目的就是让你描述当前输入内容的来源背景 例如
    "学习笔记 - 操作系统课程第3章"
    "技术文档 - Redis 官方文档"
    "会议记录 - 项目讨论会"
    "个人思考 - 对并发编程的理解"
    """
    result = await graphiti.add_episode(
        # 不同内容 ID 不同；随着主题不同，这个参数就要不同；
        # 这是最重要的，因为 graphiti_core/graphiti.py:466-475 显示系统会根据 group_id 检索相关的历史 episodes 来建立关联。不同主题应该使用不同的 group_id 来避免不相关的关联。
        group_id='hlm_group', # group_id：最关键的分组参数，决定了知识关联的边界
        # 同主题，数据更新时； 需要修改：name 和 source_description | 完全不同的内容时，需要修改：name、source_description、group_id
        source_description='红中4',  # source_description：提供内容来源的上下文信息； 参数不是基于图谱中已经存在的数据，而是你主动提供的关于当前输入内容来源的描述信息。 会直接存入 EpisodicNode， 是真正的知识主题描述
        name='HLM中4', # name：用于标识和描述这个特定的学习记录，  是 EpisodicNode（source_description） 的一个标记，描述； 它可以在一个图谱中多次出现，比如我多次录入了 红楼梦 的相关内容

        entity_types=entity_types,
        edge_types=edge_types,
        edge_type_map=edge_type_map,

        # source=EpisodeType.text,  # 明确指定为文本类型
        # episode_body = bingfabingxing,
        # episode_body = bingfabingxing_buchong,
        episode_body=hlm_data[2500:3000].replace(" ", "").replace('\n','').replace('\r',''),
        # episode_body="这是一个简单的中文测试文本，包含曹雪芹和红楼梦等关键词。",  # 测试OK； 换了其他文本就失败
        # episode_body = "This is a simple test about Cao Xueqin and Dream of Red Chamber." ,

        # excluded_entity_types=['Entity'],  # 排除默认实体类型  
        # previous_episode_uuids = [], # 不加载历史上下文 ，防止上下文过长

        reference_time=datetime.now(timezone.utc),
    )

    # print(f"添加结果: {result}")

    # 检查保存后的内容
    episode = result.episode  
    print(f"保存后文本长度: {len(episode.content)}")  
    print(f"保存后文本前100字符: {episode.content[:100]}")

    # 关闭连接
    await graphiti.close()



if __name__ == "__main__":  
    asyncio.run(main())
