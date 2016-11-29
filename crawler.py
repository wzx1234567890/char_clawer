from urllib import request
import threading
from time import sleep
from queue import Queue
import pickle
from lxml import html
import chardet

raw_url = 'http://www.baidu.com/s?wd={}'

#这个函数是为了转换字符 将内容转为utf-8解码格式
def char_trans(word, target='utf-8'):
    word = str(word.encode(target))
    word = word[2:-1]
    return  word.replace('\\x', '%')

#打开文件words并读取，赋值给target_words
f = open('words', 'rb')
target_words= pickle.load(f)
f.close()

#这个函数是初始化URL
def raw_clawer(word,que, url_fmt = raw_url):
    fmt_word = char_trans(word)
    if not fmt_word:
        return que.put(word, 'not word!')
    url = url_fmt.format(fmt_word)
    try:
        r = request.urlopen(url, timeout=1)
        data = r.read().decode('utf-8')
        #data = r.readall()
        que += [(word, data)]               
    except:
        sleep(3)
        print('failed url: {}'.format(url))
        return raw_clawer(word, que, url_fmt)




target_words = list(target_words)
words = target_words
#words = target_words[0:200]
report_N = int(len(words) / 100)
i = 0


file = open('word_searchfile','rb')
que = pickle.load(file)
file.close()
finished_words = [tp[0] for tp in que]

while True:
    if i >= len(words):
        break
    if i % report_N == 1:
        print('finished: {}'.format(i / report_N / 100))#每1%打印进度一次
    #print(i)
    word = words[i]
    raw_clawer(word, que)
    i += 1
    if word in finished_words:
        continue
    if i%1000 == 1:
        file = open('word_searchfile','wb')
        pickle.dump(que,file)
        file.close()    
    

##这个是干嘛，要把数据重新生成一次么？？？
#这次生成是为了避免刚刚生成的过程中有遗漏。
file = open('word_searchfile','wb')
pickle.dump(que,file)
file.close()  

que1 = que[1430:-1]
lcl_data = []
m = 0
for x in que1:
    if not x[0].strip():
        continue
    data_a = x[1]
    print(x[0])
    #page_word = data_a.decode(chardet.detect(data_a)['encoding'])
    data = html.fromstring(data_a)
    try:
        content_left = data.findall('*//div[@id="content_left"]')[0]
    except:
        temp_data = []
        raw_clawer(x[0], temp_data)
        data = html.fromstring(temp_data[0][1])
        content_left = data.findall('*//div[@id="content_left"]')[0]   
    iter_content = content_left.iterfind('.//div[@tpl]')
    try:
        for it in iter_content:
            if not it.findall('.//h3/a'):
                lk = it.findall('.//a')[0]
            else:
                lk = it.findall('.//h3/a')[0]
            href = lk.attrib['href']
            title = lk.text_content()
            lcl_data += [(title,href)]
    except:
        pass
    file = open('search_result','wb')
    pickle.dump(lcl_data,file)
    file.close() 
    m += 1
    if m%1000 == 1:
        print('the process is :',m)
    


file = open('search_result','wb')
pickle.dump(lcl_data,file)
file.close()    
  


