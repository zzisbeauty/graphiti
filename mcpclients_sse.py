#!/usr/bin/env python3  
"""  
使用官方 MCP 客户端连接到 SSE MCP server  
"""  
  
import asyncio  
import json  
from mcp import ClientSession  
from mcp.client.sse import sse_client  
  
poetry_data = [  
    {  
        "author": "劉吉",  
        "paragraphs": [  
            "八珍一箸千金價，往往精庖賤惠文。",  
            "莫道形模大剛拙，剖珠也解獻殷勤。"  
        ],  
        "title": "魰",  
        "id": "6ad0677d-1bcf-4564-9334-870b483c06ca"  
    },  
    {  
        "author": "劉吉",  
        "paragraphs": [  
            "一箭不中鵠，五湖歸釣魚。"  
        ],  
        "title": "句",  
        "id": "3ee5e66e-b9fb-4087-ab3a-e82e662ae88b"  
    },  
    {  
        "author": "湯悅",  
        "paragraphs": [  
            "却下烏臺建隼旟，侯封歸去襲龍舒。",  
            "嚴霜尚滿辭天闕，甘雨看隨入境車。"  
        ],  
        "title": "送季大夫牧舒州",  
        "id": "63454de7-b551-421c-ab9a-3a8d3996e9d1"  
    },  
    {  
        "author": "湯悅",  
        "paragraphs": [  
            "千里陵陽同陝服，鑿門胙土寄親賢。",  
            "曙烟已別黄金殿，晚照重登白玉筵。",  
            "江上浮光宜雨後，郡中遠岫列窗前。",  
            "天心待報期年政，留與工師播管弦。"  
        ],  
        "title": "奉和聖制送鄧王牧宣城",  
        "id": "50f5516c-2681-47f4-ad28-ee928d5a10c2"  
    },  
    {  
        "author": "湯悅",  
        "paragraphs": [  
            "正是花時節，思君寢復興。",  
            "市沽終不醉，春夢亦無憑。",  
            "嶽面懸清雨，河心走濁冰。",  
            "東門一條路，離恨正相仍。"  
        ],  
        "title": "早春寄華下同志",  
        "id": "b8a98cdd-d7d8-427c-b770-9a38e6bfa14d"  
    },  
    {  
        "author": "湯悅",  
        "paragraphs": [  
            "憶見萌芽日，還憐合抱時。",  
            "舊歡如夢想，物態暗還移。",  
            "素豔今無幾，朱顔亦自衰。",  
            "樹將人共老，何暇更悲絲。"  
        ],  
        "title": "鼎臣學士侍郎以東館庭梅昔翰苑之毫末今復半枯向時同僚零落都盡素髮垂領茲唯二人感舊傷懷發於吟詠惠然好我不能無言輒次來韻攀和",  
        "id": "3f6e946e-dfc2-4d0f-81c8-37d87387f350"  
    },  
    {  
        "author": "湯悅",  
        "paragraphs": [  
            "託植經多稔，頃筐向盛時。",  
            "枝條雖已故，情分不曾移。",  
            "莫向階前老，還同鏡裏衰。",  
            "更應憐墮葉，殘吹挂蟲絲。"  
        ],  
        "title": "再次前韻代梅答",  
        "id": "66a5b385-8447-455c-a0e0-ee6dcc12def4"  
    },  
    {  
        "author": "湯悅",  
        "paragraphs": [  
            "人物同遷謝，重成念舊悲。",  
            "連華得瓊玖，合奏發塤篪。",  
            "餘枿雖無取，殘芳尚獲知。",  
            "問君何所似，珍重杜秋詩。"  
        ],  
        "title": "鼎臣學士侍郎楚金舍人學士以再傷庭梅詩同垂寵和清絕感歎情致俱深因成四十字陳謝",  
        "id": "6c21edc7-0ce7-442c-a563-b45567dd8d2b"  
    },  
    {  
        "author": "楊文郁",  
        "paragraphs": [  
            "悠悠往古繼來今，天地無窮照孔林。",  
            "兩到金絲堂下拜，門生無負百年心。"  
        ],  
        "title": "謁聖林",  
        "id": "edcc5aef-2025-4428-8230-c0325810496a"  
    },  
    {  
        "author": "駱仲舒",  
        "paragraphs": [  
            "張鴻詩在楞伽峽，韓愈碑留燕喜亭。"  
        ],  
        "title": "句",  
        "id": "36899218-aef8-44c8-856b-2f0252d2b50e"  
    }  
]  
  
async def import_poetry_data():  
    """连接到已运行的 SSE MCP server 并导入数据"""  
      
    # 连接到您的 SSE MCP server  
    server_url = "http://localhost:8000/sse"  # 根据您的实际端口调整  
      
    try:  
        async with sse_client(server_url) as (read, write):  
            async with ClientSession(read, write) as session:  
                print(f"开始导入 {len(poetry_data)} 首古诗词...")  
                  
                for i, poem in enumerate(poetry_data, 1):  
                    # 将每首诗转换为 JSON 字符串  
                    poem_json = json.dumps(poem, ensure_ascii=False)  
                      
                    # 使用诗的标题和作者作为名称  
                    name = f"{poem['author']} - {poem['title']}"  
                    print(f"正在导入第 {i} 首: {name}")  
                      
                    # 调用 add_memory 工具  
                    result = await session.call_tool("add_memory", {  
                        "name": name,  
                        "episode_body": poem_json,  
                        "source": "json",  
                        "source_description": "古诗词数据",  
                        "group_id": "classical_poetry",  
                        "uuid": poem['id']  
                    })  
                      
                    print(f"导入结果: {result}")  
                      
                    # 添加小延迟避免过快请求  
                    await asyncio.sleep(0.5)  
                  
                print("所有古诗词数据导入完成！")  
                  
    except Exception as e:  
        print(f"导入过程中出现错误: {e}")  
  
if __name__ == "__main__":  
    asyncio.run(import_poetry_data())