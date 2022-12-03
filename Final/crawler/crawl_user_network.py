"""
Crawl connections
"""

import requests
import json
import csv 
import jsonpath
import random
from time import sleep

# Setup
urlTemplate = "https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_{uid}&since_id="

# You need your own cookie
cookie = "YOUR_COOKIE"


def get_fans_network(user_id):
    # Root
    users = ["6099859539"]

    num = 0
    
    # store following-relationship: {"source":source_user.id, "target":target_user.id} 
    followship = []

    # store user_info
    userInfo = []

    # store userId lists to avoid repeatment
    userId = ["6099859539"]
    
    flag = True
    layer = 1
    while True:
        size = len(users)
        print("-------------Layer{layerNum}------------".format(layerNum=layer))
        for i in range(size):
            target_user = users[0]
            users = users[1:]
            sleep(random.randint(6, 10))
            for offset in range(1,4):
                url = urlTemplate.format(uid = target_user) + str(offset)
                myHeader['User-Agent'] = random.choice(user_agents)
                response = requests.get(url,headers = myHeader)
                
                # unspecial conditions
                if response==b'':
                    break
                try:
                    result = json.loads(response.text)
                except Exception as e:
                    break
                if result['ok']==0:
                    break
                
                try:
                    cardgroup = jsonpath.jsonpath(result,"$..card_group")[0]
                except Exception as e:
                    break

                for fan in cardgroup:
                    try:
                        id = jsonpath.jsonpath(fan, "$..id")[0]
                        nickname = jsonpath.jsonpath(fan, "$..screen_name")[0]
                        followers_count = jsonpath.jsonpath(fan, "$..followers_count")[0]
                        following_count = jsonpath.jsonpath(fan, "$..follow_count")[0]
                        description = jsonpath.jsonpath(fan, "$..desc1")[0]
                        print(num,id,nickname,followers_count,following_count,description)
                        
                        if str(id) not in userId:
                            userId.append(str(id))
                            users.append(id)
                            userInfo.append({"id":id,"nickname":nickname,"followers_count":followers_count,"following_count":following_count,"description":description})
                            num += 1
                        followship.append({"source":id,"target":target_user})
                    except Exception as e:
                        print(e)
            if num>900:
                flag = False
                break
        if flag==False:
            break

        layer += 1
    
    f1 = open("User.csv",'w',encoding='utf-8-sig')

    csv_writer = csv.writer(f1)
    csv_writer.writerow(['id','昵称','粉丝数','关注数','个人简介'])
    for user_info in userInfo:
        csv_writer.writerow([val for val in user_info.values()])
    f1.close()

    f2 = open("Edge.csv",'w',encoding='utf-8-sig')
    csv_writer = csv.writer(f2)
    csv_writer.writerow(['source','target'])
    for edge in followship:
        csv_writer.writerow([edge["source"],edge["target"]])
    f2.close()


def generate_more_edges():
    def getFollowing(user_id, follow_num):
        # Too many fans
        if follow_num>10000:
            return []
        follow_num = min(1000,follow_num)
        page_num = int(follow_num/20) #确定爬取页数
        following = []
    
        for i in range(1,page_num+1):
            url = "https://m.weibo.cn/api/container/getSecond?containerid=100505{uid}_-_FOLLOWERS&page={page}".format(uid=user_id,page=i)
            try:
                req = requests.get(url)
                jsondata = req.text
                data = json.loads(jsondata)
                content = data["data"]['cards']
       
                for i in content:
                    followingId = i['user']['id']
                    following.append(followingId)
            except Exception as e:
                print(e)
                return following
        return following
        
    def getFans(user_id,fans_num):
        urlTemplate = "https://m.weibo.cn/api/container/getIndex?containerid=231051_-_fans_-_{uid}&since_id="
        if fans_num>10000:
            return []
        fans_num = min(fans_num,1000)
        page_num = int(fans_num/20)
        fans = []
    
        for offset in range(1,page_num+1):
            url = urlTemplate.format(uid = user_id) + str(offset)
            response = requests.get(url)
            result = json.loads(response.text)
            try:
                cardgroup = jsonpath.jsonpath(result,"$..card_group")[0]
            except Exception as e:
                print(e)
                return fans
                
                for fan in cardgroup:
                    try:
                        user_id = jsonpath.jsonpath(fan, "$..id")[0]
                        fans.append(user_id)
                    except Exception as e:
                        print(e)
        return fans


    ids = []
    users = []

    with open("User.csv",'r') as file:
        reader = csv.reader(file)
        users = list(reader)
    
    f2 = open('edges.csv','a+',encoding='utf-8-sig')
    edge_writer = csv.writer(f2)
    edge_writer.writerow(['source','target'])

    num = 1
    users = users[1:]
    
    for user in users:
        ids.append(user[0])

    for user in users:
        sleep(random.randint(10,20))
        id, follow_num, fans_num = user[0], int(user[3]), int(user[2])
        following = getFollowing(id,follow_num)
       
        fans = getFans(id,fans_num)
       
        for follow in following:
            if str(follow) in ids:
                f2 = open('edges.csv','a+',encoding='utf-8-sig')
                edge_writer = csv.writer(f2)
                edge_writer.writerow([id,follow])
                print('-'*20+str(id)+" FOLLOW "+str(follow)+'-'*20)
        for fan in fans:
            if str(fan) in ids:
                f2 = open('edges.csv','a+',encoding='utf-8-sig')
                edge_writer = csv.writer(f2)
                edge_writer.writerow([fan,id])
                print('-'*20+str(fan)+" FOLLOW "+str(id)+'-'*20)
        print('*'*20+"第"+str(num)+"用户处理完毕"+'*'*20)
        num+=1



if __name__ == "__main__":
    user_id = "USER_ID"
    get_fans_network(user_id)
    #generate_more_edges()