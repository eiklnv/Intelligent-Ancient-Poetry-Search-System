import requests,os,sys,time,json,glob,random,io,copy,re
import lib_poc_llm
from pymongo import MongoClient
S_nlp_using_llm = lib_poc_llm.D_nlp_using_llm() 
mongodb_client = MongoClient('YOUR')

def build_convert_raw_query_prompt(raw_query):
    prompt = """
[任务]
你是一个古诗词搜索意图分析助手，把[原始搜索请求]转换为Mongodb查询命令，具体步骤如下：
1、首先对原始搜索请求进行语义分析，提取其中的篇名、作者、任务、地点等信息，并确定搜索目标是原文、还是在人物、地点等
2、根据第1步语义分析结果，参考[数据表的定义]，生成Mongodb查询指令；
3、生成的查询内容带上id，便于后续进一步查询；
4、请参考[转换示例]。

[转换示例]
# 例1：
## 搜索请求：李白诗中地名包括庐山
## 输出mongodb查询指令：
```json
{
    "author": "李白",
    "places_list": {
        "$elemMatch": {
            "$or":[
                {"原文地名": { "$regex": "庐山" }}, 
                {"现代地名": { "$regex": "庐山" }} 
            ]
        }
    }
}
```

# 例2：
## 搜索请求：哪些诗中人名同时包括丹丘生和曹植
## 输出mongodb查询指令：
```json
{
    "people_list": {
        "$elemMatch": {
            "$or":[
                {"原文人名": { "$regex": "曹植" },"人物介绍": { "$regex": "曹植" }}, 
                {"原文人名": { "$regex": "丹丘生" },"人物介绍": { "$regex": "丹丘生" }}, 
        ],
        }
     }
}
```

# 例3：
## 搜索请求：锄禾日当午的下一句是什么
## 输出mongodb查询指令：
```json
{
    "content": { "$regex": "锄禾日当午" }
}
```

# 例4：
## 搜索请求：白居易的诗包括哪些人物
## 输出mongodb查询指令：
```json
{
    "author": "白居易",
}
```

# 例4：
## 搜索请求：北固亭和什么地址相关
## 输出mongodb查询指令：
```json
{
    "places_list": {
        "$elemMatch": {
            "$or":[
                {"原文地名": { "$regex": "北固亭" }}, 
                {"现代地名": { "$regex": "北固亭" }} 
            ]
        }
    }
}
```


[数据表的定义]
```json
{
  "title": "", // 字符串类型，表示古诗词标题名
  "author": "", // 字符串类型，表示古诗词作者
  "content": "", // 字符串类型，表示古诗词原文
  "people_list": [
      {
          "原文人名": "", // 字符串类型，表示古诗词中的一个人名
          "人物介绍": "", // 字符串类型，表示古诗词中该人名的介绍
      }
   ], // 数组类型，表示古诗词中报告的人名信息
  "places_list": [
      {
          "原文地名": "", // 字符串类型，表示古诗词中的一个原文地名
          "现代地名": "", // 字符串类型，表示古诗词中该地名对应的现代地名
      }
   ] // 数组类型，表示古诗词中报告的地点信息
}
```

[输出内容及格式]
# 输出查询mongodb查询指令，以如下JSON格式输出；


[原始搜索请求]
"""
    prompt = prompt + '\n' + raw_query
    return prompt

def do_mongodb_query(query_json):
    db = mongodb_client['poems']
    collection = db['poems_info']
    res = collection.find(query_json)
    return res

def do_summarize_poem(raw_query,markdown_result):
    prompt = f"""
[任务]
你是一个古诗词搜索回复助手，请[古诗词列表]的内容，总结回复[用户原始搜索问题]。
1、回复时，分析[古诗词列表]每一首诗的内容，总结出[用户原始搜索问题]的答案；
2、回复时，附上相关的原文，不要把所有全文附上；
3、回复时，以列表方式，中文回复。

[古诗词列表]
{markdown_result}

[用户原始搜索问题]
{raw_query}
"""
    stream = S_nlp_using_llm.chat(prompt,stream=True)
    return stream