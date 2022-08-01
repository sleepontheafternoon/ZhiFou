import numpy as np



# 执行sql语句
def Sql_operation(cursor, sql):
    cursor.execute(sql)
    results = cursor.fetchall()
    return results


# 获取答题情况
def Get_situation(results):
    stu2rows = {}
    row_num = -1
    ans = []
    # 获取答题情况
    for i in range(len(results)):
        # 判断是否是新的学生
        if results[i][0] not in stu2rows:
            row_num += 1
            stu2rows[results[i][0]] = row_num
            ans.append([])
        # 简单归一化得分
        ans[stu2rows[results[i][0]]].append(results[i][3] / 10)

    return np.array(ans), stu2rows


def Ques_konwledge(p_num, data1, data2, data3):
    konwledge_unit = []

    # 得到知识点的数目，然后去重
    for row in data1:
        ls = row[1].split(",")
        for k in ls:
            if k not in konwledge_unit:
                konwledge_unit.append(k)

    for row in data2:
        ls = row[1].split(",")
        for k in ls:
            if k not in konwledge_unit:
                konwledge_unit.append(k)

    for row in data3:
        ls = row[1].split(",")
        for k in ls:
            if k not in konwledge_unit:
                konwledge_unit.append(k)

    unit2pos = {konwledge_unit[i]: i for i in range(len(konwledge_unit))}

    Q = np.zeros([p_num, len(konwledge_unit)])

    row_num = 0

    for row in data1:
        ls = row[1].split(",")
        for k in ls:
            Q[row_num][unit2pos[k]] = 1
        row_num += 1

    for row in data2:
        ls = row[1].split(",")
        for k in ls:
            Q[row_num][unit2pos[k]] = 1
        row_num += 1

    for row in data3:
        ls = row[1].split(",")
        for k in ls:
            Q[row_num][unit2pos[k]] = 1
        row_num += 1

    return Q, unit2pos


def PartialSep(data1, data2, data3=[], data4=[]):
    n1, n2, n3, n4 = len(data1), len(data2), len(data3), len(data4)
    n = n1 + n2 + n3 + n4
    s, type = "", ""
    for i in range(n):
        if i < n1:
            s += str(data1[i]) + ","
            type += "1" + ","
        elif i < n1 + n2:
            s += str(data2[i - n1]) + ","
            type += "2" + ","
        elif i < n1 + n2 + n3:
            s += str(data3[i - n1 - n2]) + ","
            type += "3" + ","
        else:
            s += str(data4[i - n1 - n2 - n3])
            type += "4" + ","
    return s[:-1], type[:-1]


def GetKonwledgeunit(point, course, unit2pos):
    unit = {}
    x = []
    y = []
    dic = {}
    d_count = {}

    # 首先将章节和对应的知识点相匹配
    for k in unit2pos.keys():
        chapter = k[0:3]
        if chapter not in unit:
            unit[chapter] = []
            unit[chapter].append(k)

    # 得到认知诊断的x：知识点名称，和y:该知识点的得分
    for k, v in unit.items():
        for source in course:
            if k in source[1]:
                x.append(source[0])
                total = 0

                for u in v:
                    total += point[unit2pos[u]]  # 得分

                y.append(total / len(v))  # 所有该知识点的平均值

    # 得到它们最终结果
    for i in range(len(x)):
        if x[i] not in dic:
            dic[x[i]] = y[i]
            d_count[x[i]] = 1
        else:
            dic[x[i]] += y[i]
            d_count[x[i]] += 1

    # 计算得到知识点的平均得分

    for k in dic.keys():
        dic[k] = round(dic[k] / d_count[k], 2)

    return dic

def Name2id(cursor,sql,rec):
    source = Sql_operation(cursor,sql)
    dic = {}
    """try:
        
    except:
        return None"""
    for item in source:
        dic[item[1]] = item[0]

    ans = []
    for k in rec:
        ans.append(dic[k])
    return ans
