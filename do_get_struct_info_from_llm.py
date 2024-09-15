import requests,os,sys,time,json,glob,random,io,copy,re
from fire import Fire
import lib_poc_llm
from pymongo import MongoClient

def build_one_poem_prompt(one_poem):
    output_format = """
```json{
    "人名":[{
         "原文人名":"原文人名"，
         "人物介绍":"人物介绍"
        }],
    "地名":[{
         "原文地名":"原文地名"，
         "现代地名":"现代地名"
        }]
}```
"""
    prompt = f"""
[任务]
你是一个古诗词分析助手，请按照下面步骤从[原始待处理古诗词中]找出包含的所有人名和地名；
1. 首先对原始信息A进行详细翻译得到译文A1；
2. 对译文A1进行补齐主语，并润色，得到最后译文A2；
3. 分析最终译文内容A2，并结合[外部参考译文]，找出其中所有相关地名，和人名并按照下面[输出内容及格式]输出
请按照上述step-by-step完成。

[外部参考译文]
{one_poem['translation']}

[输出内容及格式]
# 输出人名和地名，以如下JSON格式输出；
{output_format}

[原始待处理古诗词]
题目:{one_poem['title']}
作者:{one_poem['writer']}
内容:{one_poem['content']}

"""
    return prompt

def do_call_llm(one_poem,S_nlp_using_llm):
    try:
        prompt = build_one_poem_prompt(one_poem)
        print('\nprompt>>>',prompt)
        run_response = S_nlp_using_llm.chat(prompt,stream=False)
        res = run_response.choices[0].message.content
        res = lib_poc_llm.mdjson2dict(res)
        print('\nres>>>',res)
    except Exception as e:
        print(f'Error: {e}')
        res = None
    return res

def add_to_mongodb(one_poem,res):
    # 连接到MongoDB
    client = MongoClient('YOUR')
    db = client['poems']
    # 如果集合不存在，MongoDB会在第一次插入数据时自动创建
    collection = db['poems_info']

    # 准备要插入或更新的数据
    poem_data = {
        'title': one_poem['title'],
        'content': one_poem['content'],
        'translation': one_poem['translation'],
        'author': one_poem['writer'],
        'people_list': res.get('人名', []),
        'places_list': res.get('地名', [])
    }

    # 检查是否已存在相同的诗词（根据原文判断）
    existing_poem = collection.find_one({'content': one_poem['content']})

    if existing_poem:
        # 如果存在，更新数据
        collection.update_one(
            {'_id': existing_poem['_id']},
            {'$set': poem_data}
        )
        print(f"已更新诗词：{one_poem['title']}")
    else:
        # 如果不存在，插入新数据
        collection.insert_one(poem_data)
        print(f"已添加新诗词：{one_poem['title']}")

def app_main(json_file="/home/deeper/deeplim/poems/t.json"):
    S_nlp_using_llm = lib_poc_llm.D_nlp_using_llm()

    writer_list = ['李白','杜甫','王维','李商隐','苏轼','辛弃疾','李清照','陆游','王安石','辛弃疾','李清照','陆游','王安石']
    writer_list = ['毛泽东','辛弃疾']
    writer_list = ['李白','杜甫','王维','李商隐','陆游','白居易']
    writer_list = ['文天祥',"岳父","高适"]
    writer_list = ['王安石','李清照']
    #--读取json_file
    with open(json_file, 'r') as f:
        data = json.load(f)
        all_poems_data = data['poems']
        all_writers_data = data['writers']
        print(f'OK to read from [file:{json_file}] [poems:{len(all_poems_data)}] [writers:{len(all_writers_data)}]')

    #--
    count = 1
    for one_poem in all_poems_data:
        if one_poem['writer'] in writer_list:
            try:
                res = do_call_llm(one_poem,S_nlp_using_llm)
                if res is not None:
                    add_to_mongodb(one_poem,res)
                    print(f'OK to add to mongodb {count} poems')
                    time.sleep(3)
                    count += 1

            except Exception as e:
                print(f'Error: {e}')
                sys.exit(0)
            #break


if __name__ == "__main__":
    print('\nStart...\n')
    Fire(app_main)
    
    print('\nEnd\n')
