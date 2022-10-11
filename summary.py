import requests,json,main,time,os,re
with open('result.json','r',encoding='utf8') as origin_file:
    origin=origin_file.read()
origin=json.loads(origin)
pushdata={'desp':'详细结果：\n', 'title':''}
config=main.config
#推送渠道
# pushdata['channel']=config['push']['channel']
# pushdata['template']='html'

try:
    token=os.environ['PUSHTOKEN']
except:
    config['push']['push'] = 'no'
    print('Token读取失败，不再推送！')
    pass

if config['study']['dailycheckin'] == 'yes' or config['study']['studychannel'] == 'yes' or config['study']['answer_questions'] == 'yes':
    time.sleep(60)#平台统计有延迟
    for member in origin:
        XLtoken=main.ConverMidToXLToken(member['member'])
        profile=main.GetProfile(XLtoken)
        score_now=profile.score()
        score_add=score_now-member['score']
        score_thrsh = [100, 200, 500, 1000, 5000]
        score_need = 0
        for threshold in score_thrsh:
            if score_now < threshold:
                score_need = threshold - score_now
                break
        member['result']+=f'此次执行增加了{str(score_add)}积分，当前为{profile.medal()}，距离下一徽章还需{str(score_need)}积分\n'
        pushdata['desp'] += f"名称:{member['name']}: {member['result']}"
else:
    pushdata['desp'] += "\n".join(f"名称:{member['name']}: {member['result']}" for member in origin)

#检查token
if ('token' in locals().keys()) == True:
    pass
else:
    exit('+===============+\n| Token未定义! |\n+===============+')

failed_members = set(mem['name'] for mem in origin if mem['status'] == 'error')
n_member = len(main.memberlist)
n_success = n_member - len(failed_members)
pushdata['title'] = f'自动智慧团建：({n_success}/{n_member})人已完成'
if failed_members:
    if n_success == 0:
        pushdata['desp'] += '\n所有人任务均失败'
    else:
        pushdata['desp'] += f'\n失败名单：{failed_members}'

#向Server酱出推送请求
try:
    if config['push']['push']=='yes':
        push=json.loads(requests.post(f'https://sctapi.ftqq.com/{token}.send',data=pushdata).text)
        if push['code'] == 200:
            print('推送成功')
        else:
            exit('推送失败：'+push['msg'])
except:
    pass

#Actions Summary
print('正在生成运行结果')
summary='## 执行结果\n#### PS：由于安全性问题，详细结果请使用推送功能\n|序号|青年大学习打卡状态|\n|-|-|'
count=0
for i in origin:
    count+=1
    summary+='\n|'+str(count)+'|'
    if i['status'] != 'error':
        summary+='✅|'
    else:
        summary+='❌|'
with open(os.environ['GITHUB_STEP_SUMMARY'],'w+',encoding='utf8') as finaloutput:
    finaloutput.write(summary)
