import numpy as np
import random
import requests


def GetStudentId():
    url = "http://localhost:8081/student/getStudentBySid"
    sid = requests.post(url)
    return sid.text


# 计算余弦相似度
def CalCos(x, y):
    x = np.array(x)
    y = np.array(y)
    mod_x = sum(x * x) ** 0.5
    mod_y = sum(y * y) ** 0.5
    return sum(x * y) / (mod_x * mod_y)


# 查看是否有做题信息
def JudgeStu(sid, data):
    n = [k[0] for k in data]
    return sid in n


# 不同资源推荐
def DifferSource(point, konw_source, subit):
    for i in range(len(konw_source)):
        if (point in konw_source[i][1]) and (konw_source[i][0] not in subit):
            subit.append(konw_source[i][0])
    return subit


# 选取不同的资源
def SampleSource(subit, rec_num, final_rec):
    if 1 <= len(subit) <= rec_num:
        final_rec.append(subit)
    elif len(subit) > rec_num:
        final_rec.append(random.sample(subit, 5))
    else:
        final_rec.append([])
    return final_rec


# 缺失知识点推荐
def Lackkonwlege(know_p, pos2unit, choice_source, judge_source, subque_source, ppt_source, rec_num=5):
    rec_choice = []
    rec_judge = []
    rec_sub = []
    rec_ppt = []

    final_rec = []

    for i in range(len(know_p)):
        # 如果做错了，得到相应的知识点，然后再进行推荐
        if know_p[i] == 0:
            point = pos2unit[i]

            DifferSource(point, choice_source, rec_choice)
            DifferSource(point, judge_source, rec_judge)
            DifferSource(point, subque_source, rec_sub)
            DifferSource(point, ppt_source, rec_ppt)

    rec_ppt = list(set(rec_ppt))  # 去重
    # 根据知识点随机选择几道题目，最后推荐得到的是选择题，其次是填空题
    SampleSource(rec_choice, rec_num, final_rec)
    SampleSource(rec_judge, rec_num, final_rec)
    SampleSource(rec_sub, rec_num, final_rec)
    SampleSource(rec_ppt, rec_num, final_rec)

    return final_rec  # 第一行选择题，第二行填空题,第三行主观题


# 返回与当前学生的相似程度排行，从大到小放在列表里
def SimilarRanking(stu2rows, rows2stu, data, sid):
    similar_ranking = []
    for i in range(len(data)):
        if stu2rows[sid] == i:
            continue
        else:
            similar = CalCos(data[stu2rows[sid]], data[i])
            similar_ranking.append([rows2stu[i], similar])
    similar_ranking = sorted(similar_ranking, key=lambda x: x[1], reverse=True)  # 从大到小排列
    return similar_ranking


# 根据相似度进行推荐
def SimilarRecommend(sid, sql_data, stu2rows, rows2stu, data, num=5):
    similar_ranking = SimilarRanking(stu2rows, rows2stu, data, sid)
    recommend = []
    dont_re = []
    for q in range(len(sql_data)):
        if sql_data[q][0] == sid:
            dont_re.append(sql_data[q][1])

    neighbor_num = min(len(similar_ranking), num)
    for v in range(neighbor_num):
        for q in range(len(sql_data)):
            if sql_data[q][0] == similar_ranking[v][0] and sql_data[q][1] not in dont_re:
                recommend.append(sql_data[q][1])
    return recommend


# 开始随机推荐,返回名字
def InitialRecommend(advise_source, sql_source, num=5):
    num = min(num, len(advise_source))
    num = random.sample(advise_source, num)
    rec_name = []
    for i in range(len(num)):
        rec_name.append(sql_source[num[i]][0])
    return rec_name


def Initial_key(source, initial_state, sid, num=5):
    final = []
    ans = []
    # 得到兴趣列表
    for k in initial_state:
        if sid == k[0]:
            ls = k[1].split(",")
            break

    for s in ls:
        for name in source:
            if s in name[0]:
                final.append(name[0])

    final = list(set(final))
    number = list(range(len(final)))

    num = min(num, len(final))
    choose = random.sample(number, num)

    for i in choose:
        ans.append(final[i])

    return ans


# 痕迹浏览推荐
def TraceRecommend(sql_user_time, sql_vedio_source, num=2):
    dic = {}
    for i in range(len(sql_user_time)):
        subject = sql_user_time[i][0]
        if subject in dic:
            dic[subject] += sql_user_time[i][1] + 30  # 如果重复浏览是有加成的
        else:
            dic[subject] = sql_user_time[i][1]
        final_score = sorted(dic.items(), key=lambda x: x[1], reverse=True)
    num = min(num, len(final_score))
    trace_recommend = []
    for j in range(num):
        for k in range(len(sql_vedio_source)):
            if final_score[j][0] in sql_vedio_source[k][0]:
                trace_recommend.append([sql_vedio_source[k][0], sql_vedio_source[k][1]])
    num = min(num, len(trace_recommend))
    return random.sample(trace_recommend, num)