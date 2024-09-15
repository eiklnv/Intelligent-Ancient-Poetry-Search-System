import streamlit as st
import sys,os,json,copy,re
import time,datetime,subprocess,pytz,signal
import pandas as pd

#--设置pages为根目录
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
import lib_poem,lib_poc_llm

st.set_page_config(
    page_title="古诗词智能搜索",
    layout="wide",
    menu_items={
        'About': "# 古诗词智能搜索!"
    }

)



# 居中显示
st.markdown("""
<div style="font-size:40px; text-align: center;">
古诗词智能搜索
</div>
""", unsafe_allow_html=True)


st.markdown("""
<div style="font-size:24px; text-align: center;color:blue;">

</div>
""", unsafe_allow_html=True)

raw_query = st.text_area(label="请输入",height=32, max_chars=256,key="raw_query")
if raw_query:
    print('raw_query>>>',raw_query)
    with st.expander("（1）搜索意图转换",expanded=True):
        prompt = lib_poem.build_convert_raw_query_prompt(raw_query)
        print('\nprompt>>>',prompt)
        stream = lib_poem.S_nlp_using_llm.chat(prompt,stream=True)
        run_response = st.write_stream(stream)
        print('run_response>>>',run_response)
        query_json = lib_poc_llm.mdjson2dict(run_response)

    data = []
    with st.expander("（2）执行数据库查询",expanded=True):
        if query_json:
            db_result = lib_poem.do_mongodb_query(query_json)
            if db_result:
                # 将查询结果转换为列表
                result_list = list(db_result)
                
                if result_list:
                    # 只选择title和content两列
                    columns = ['title', 'author', 'content']
                    for key in query_json:
                        if key not in ['title', 'author', 'content']:
                            columns.append(key)
                    
                    # 创建一个只包含title和content的数据列表
                    data = []
                    for doc in result_list:
                        one_data = [str(doc.get(r, '')) for r in columns]
                        data.append(one_data)
                    
                    # 使用st.table()显示结果
                    st.table(pd.DataFrame(data, columns=columns))
                else:
                    st.write("没有找到匹配的结果。")
        else:
            data = []
            st.write('转换失败')

    with st.expander("（3）总结回复",expanded=True):
        if len(data)>0:
            # 将data转换为markdown格式
            markdown_result = "# 搜索结果\n\n"
            for row in data:
                markdown_result += f"## {row[0]}\n\n"
                markdown_result += f"作者: {row[1]}\n\n"
                markdown_result += f"内容:\n{row[2]}\n\n"
                for i in range(3, len(row)):
                    markdown_result += f"{columns[i]}: {row[i]}\n\n"
                markdown_result += "---\n\n"
            
            stream = lib_poem.do_summarize_poem(raw_query,markdown_result)
            run_response = st.write_stream(stream)
        