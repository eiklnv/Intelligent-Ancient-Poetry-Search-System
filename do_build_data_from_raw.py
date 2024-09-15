import requests,os,sys,time,json,glob,random,io,copy,re
from fire import Fire

class D_raw_data(object):
    def __init__(self):
        return
    
    def strim_content(self,s):
        #--处理s的不规范字符
        #--去除html标签
        s = re.sub(r'<[^>]+>', '', s)

        #--把多个空格替换为一个空格，把tab\u3000等非标准空格替换为空格
        s = re.sub(r'\s+', ' ', s)
        s = s.replace('\t','').replace('\u3000','')

        return s.strip()

    def strim_data(self,data):
        #--data是一个字典，把字典内容中的字符串中用stream_content处理
        for k,v in data.items():
            if type(v) == str:
                data[k] = self.strim_content(v)
        return data

class D_chinese_gushiwen(D_raw_data):
    def __init__(self,root_path = '/home/deeper/deeplim//poems/raw_data/chinese-gushiwen/'):
        self.root_path = root_path
        self.poems_path = os.path.join(root_path, 'guwen')
        self.poems_files = glob.glob(f'{self.poems_path}/*.json')
        self.writers_path = os.path.join(root_path, 'writer')
        self.writers_files = glob.glob(f'{self.writers_path}/*.json')

        return

    def normal_one_poem(self,one_data):
        #--one_data是一个字典，返回一个新的处理后的字典
        new_data = {}
        poem_schema = {
            'title':'title',
            'dynasty':'dynasty',
            'content':'content',
            'remark':'remark',
            'translation':'translation',
            'writer':'writer',
        }

        for k,v in poem_schema.items():
            #--如果one_data中有k，就加入new_data中
            new_data[v] = ""
            if k in one_data:
                new_data[v] = self.strim_content(one_data[k])

        return new_data

    def read_poems(self):
        #--获取guwen目录中所有的json文件
        all_poems_data = []
        for file in self.poems_files:
            with open(file, 'r') as f:
                #--读取每一行
                for line in f:
                    #--转换为json
                    data = json.loads(line)
                    new_data = self.normal_one_poem(data)
                    all_poems_data.append(new_data)
        return all_poems_data

    def normal_one_writer(self,one_data):
        #--one_data是一个字典，返回一个新的处理后的字典
        new_data = {}
        writer_schema = {
            'name':'name',
            'simpleIntro':'simpleIntro',
            'detailIntro':'detailIntro',
        }

        for k,v in writer_schema.items():
            #--如果one_data中有k，就加入new_data中
            if k in one_data:
                new_data[v] = self.strim_content(one_data[k])
            else:
                new_data[v] = ""

        return new_data

    def read_writers(self):
        #--获取write目录中所有的json文件
        all_writers_data = {}
        for file in self.writers_files:
            with open(file, 'r') as f:
                #--读取每一行
                for line in f:
                    #--转换为json
                    data = json.loads(line)
                    new_data = self.normal_one_writer(data)
                    try:
                        new_name = new_data['name'].split()[0]
                        assert(len(new_name)>0)
                        new_data['name'] = new_name
                        all_writers_data[new_name] = new_data
                    except:
                        continue
        return all_writers_data

class D_poems_db(D_raw_data):
    def __init__(self,root_path = '/home/deeper/deeplim/poems/raw_data/poems-db/'):
        self.root_path = root_path
        self.poems_files = []
        for fname in ['poems1.json','poems2.json','poems3.json','poems4.json']:
            self.poems_files.append(os.path.join(self.root_path,fname))
        
        self.writers_files = []
        for fname in ['poems-authors.json']:
            self.writers_files.append(os.path.join(self.root_path,fname))

        return

    def normal_one_poem(self,one_data):
        #--one_data是一个字典，返回一个新的处理后的字典
        new_data = {}
        poem_schema = {
            'name':'title',
            'dynasty':'dynasty',
            'content':'content',
            'notes':'remark',
            'translate':'translation',
            'author':'writer',
        }

        for k,v in poem_schema.items():
            #--如果one_data中有k，就加入new_data中
            new_data[v] = ""
            if k in one_data:
                if type(one_data[k]) == list and len(one_data[k])>0:
                    new_s = "".join(one_data[k])
                    new_data[v] = self.strim_content(new_s)
                elif type(one_data[k]) == str:
                    new_data[v] = self.strim_content(one_data[k])

        return new_data

    def read_poems(self):
        #--获取guwen目录中所有的json文件
        all_poems_data = []
        for file in self.poems_files:
            with open(file, 'r') as f:
                #--读取每一行
                for line in f:
                    #--转换为json
                    data = json.loads(line)
                    new_data = self.normal_one_poem(data)
                    all_poems_data.append(new_data)
        return all_poems_data

    def normal_one_writer(self,one_data):
        #--one_data是一个字典，返回一个新的处理后的字典
        new_data = {}
        writer_schema = {
            'name':'name',
            'lifetime':'simpleIntro',
            'detailIntro':'detailIntro',
        }

        for k,v in writer_schema.items():
            #--如果one_data中有k，就加入new_data中
            if k in one_data:
                new_data[v] = self.strim_content(one_data[k])
            else:
                new_data[v] = ""

        return new_data

    def read_writers(self):
        #--获取write目录中所有的json文件
        all_writers_data = {}
        for file in self.writers_files:
            with open(file, 'r') as f:
                #--读取每一行
                for line in f:
                    #--转换为json
                    data = json.loads(line)
                    new_data = self.normal_one_writer(data)
                    try:
                        new_name = new_data['name'].split()[0]
                        assert(len(new_name)>0)
                        new_data['name'] = new_name
                        all_writers_data[new_name] = new_data
                    except:
                        continue
        return all_writers_data

def merge_delete_repeat_poems(all_poems_data_1,all_poems_data_2):
    all_poems_data = []
    poem_index = {}
    max_len = 0
    for one_poem in all_poems_data_1+all_poems_data_2:
        max_len = max(max_len,len(str(one_poem)))
        #--去掉content的空格、回车换行
        content = one_poem['content'].replace(' ','').replace('\n','')
        #--如果content有成对括号，去掉括号及括号的内容
        content = re.sub(r'\(.*?\)','',content)
        #--只保留中文字符，并去掉标点符号
        content = re.sub(r'[^\u4e00-\u9fa5]','',content)
        #--去掉所有中文标点符号
        content = re.sub(r'[，。、；：？！“”‘’—…《》]', '', content)
        #--去掉前后空格
        content = content.strip()
        if content in poem_index:
            continue
        else:
            poem_index[content] = 1
            all_poems_data.append(one_poem)
    print("max_len>>>>",max_len)
    return all_poems_data

def app_main(to_file):
    S_chinese_gushiwen = D_chinese_gushiwen()
    #--get_writer，并print结果
    all_writers_data = S_chinese_gushiwen.read_writers()
    print(f"OK to read writers [data_num:{len(all_writers_data)}]")

    S_poems_db = D_poems_db()
    #--get_writer，并print结果
    all_writers_data_2 = S_poems_db.read_writers()
    print(f"OK to read writers [data_num:{len(all_writers_data_2)}]")

    #--合并两个writers
    for k,v in all_writers_data_2.items():
        if k not in all_writers_data:
            all_writers_data[k] = v
    print(f"OK to merge writers [data_num:{len(all_writers_data)}]")    

    #--get_poems
    all_poems_data_1 = S_chinese_gushiwen.read_poems()
    print(f"OK to read poems [data_num:{len(all_poems_data_1)}]")

    all_poems_data_2 = S_poems_db.read_poems()
    print(f"OK to read poems [data_num:{len(all_poems_data_2)}]")

    #--合并两个poems
    all_poems_data = merge_delete_repeat_poems(all_poems_data_1,all_poems_data_2)
    print(f"OK to merge poems [data_num:{len(all_poems_data)}]")

    #--随机显示5条数据
    for i in range(10):
        print(i,all_poems_data[random.randint(0,len(all_poems_data)-1)])
        
    #--显示前5条数据
    for i in range(10,15):
        print(i,all_poems_data[i])
        
    final_data = {
        'writers':all_writers_data,
        'poems':all_poems_data,
    }

    #--写入json文件
    with open(to_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False,indent=4)
        print(f'OK to write to [file:{to_file}] [poems:{len(all_poems_data)}] [writers:{len(all_writers_data)}]')



if __name__ == "__main__":
    print('\nStart...\n')

    #--调用测试入口
    Fire(app_main)
    
    print('\nEnd\n')
