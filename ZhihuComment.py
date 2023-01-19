# -*- coding: utf-8 -*-
"""
Created on Mon Jan 16 19:52:56 2023
@author: Administrator
"""
import requests,time,re
import pandas as pd

answer_url = 'https://www.zhihu.com/question/59841312/answer/2760795083'


zhihu_comment = pd.DataFrame(columns = ['知乎用户','知乎ID','评论内容','IP属地','评论ID'])
#获取子评论
def get_child_comment(comment_id,zhihu_comment):
    child_comment = pd.DataFrame(columns = ['知乎用户','知乎ID','评论内容','IP属地','评论ID'])
    child_comment_url  = 'https://www.zhihu.com/api/v4/comment_v5/comment/%s/child_comment?order_by=ts&limit=20&offset='%(comment_id)
    resp_json = requests.get(child_comment_url).json()
    counts = resp_json['counts']['total_counts']
    print('该评论共有%s条子评论'%counts)
    while True:
        time.sleep(5)
        resp_json = requests.get(child_comment_url).json()
        dataList = resp_json['data']
        for data in dataList:
            comment_author = data['author']['name']
            comment_author_id = data['author']['url_token']
            comment_author_id = "'"+str(comment_author_id) #id
            comment_content = data['content'] #评论内容
            ip_location = data['comment_tag'][0]['text']
            ip_location = ip_location.replace('IP 属地','') #IP 属地
            comment_dict = {'知乎用户':comment_author,'知乎ID':comment_author_id,'评论内容':comment_content,'IP属地':ip_location,'评论ID':comment_id}
            child_comment = child_comment.append(comment_dict, ignore_index=True, sort=False)
        if resp_json['paging']['is_end'] == True:
            break
        print('子评论翻页')
        child_comment_url = resp_json['paging']['next']
    return child_comment
 
#评论清洗

def new_comment_content(comment_content):
    comment_content = comment_content.replace('<p>','')
    comment_content = comment_content.replace('<br>','')
    comment_content = comment_content.replace('</p>','')
    return comment_content

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'}

answer_no = re.findall('answer/(.*)', answer_url)[0] #答案ID

number_url = 'https://www.zhihu.com/api/v4/answers/%s/root_comments'%answer_no
total_counts = requests.get(number_url,headers=headers).json()['common_counts']
print('网页现实共有%s条评论'%total_counts)

page = 0
while True:
    print('-'*6)
    time.sleep(5)
    comment_ur = 'https://www.zhihu.com/api/v4/answers/%s/root_comments?order=normal&limit=20&offset=%s&status=open'%(answer_no,page)
    resp_json = requests.get(comment_ur,headers=headers).json()
    try:
        resp_json['error']
        print('验证码：'%resp_json['error']['redirect'])
        break
    except:
        pass
    if resp_json['data'] ==[]:
        print('主评论抓取完毕！')
        break
    data = resp_json['data'][0]
    comment_author = data['author']['member']['name'] #作者
    comment_author_id = data['author']['member']['url_token'] #id
    comment_author_id = str(comment_author_id)
    comment_content = data['content'] #评论内容
    ip_location = data['address_text']
    ip_location = ip_location.replace('IP 属地','') #IP 属地
    comment_id = data['id']
    print('%s:%s'%(comment_author,comment_content))
    comment_dict = {'知乎用户':comment_author,'知乎ID':comment_author_id,'评论内容':comment_content,'IP属地':ip_location,'评论ID':comment_id}
    zhihu_comment = zhihu_comment.append(comment_dict, ignore_index=True, sort=False)
    #获取子评论
    child_comment = get_child_comment(comment_id,zhihu_comment)  
    zhihu_comment = pd.concat([zhihu_comment,child_comment],ignore_index=True)
    page+=1
zhihu_comment['评论内容'] = zhihu_comment['评论内容'].apply(new_comment_content)
zhihu_comment.to_excel('ZhihuComment_%s.xlsx'%answer_no)