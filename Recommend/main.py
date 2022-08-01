import random
import pymysql
from SQL_Operation import Sql_operation,Get_situation,Ques_konwledge,PartialSep,GetKonwledgeunit,Name2id
from draw_my_line import DrawLine
from My_recommend import Lackkonwlege,SimilarRecommend,InitialRecommend,JudgeStu,TraceRecommend,Initial_key
from FuzzyCDF import FuzzyCDF
from Parameter_evaluate import cal_alpha_mastery
import json

def Draw_Recommend(sid,path="basic_line_chart.html",**database_info):

    db = pymysql.connect(host=database_info["host"],
                         user=database_info["user"],
                         password=database_info["password"],
                         database=database_info["database"])
    cursor = db.cursor()


    # 获取所有做Java题目的学生的做题信息
    # sql语句
    # 获取答题情况
    sql = "select sid,question,questionType,score from answer_copy1 \
    where quizId=15"

    # 获取题目的数量
    sql1 = "select choiceNum,judgeNum,subqueNum from quiz_copy1 \
    where quizId=15"

    # 获取题目相关知识点
    # 选择题
    sql2 = "select KonwledgeMeta1,KonwledgeMeta2 from choice_copy1"

    # 判断题
    sql3 = "select KonwledgeMeta1,KonwledgeMeta2 from judge_copy1"

    # 主观题
    sql4 = "select KonwledgeMeta1,KonwledgeMeta2 FROM subque"

    # 进行数据访问，得到数据,返回得到的都是元组
    results = Sql_operation(cursor, sql)  # 答题情况

    re2 = Sql_operation(cursor, sql1)  # 选择、判断题和主观题的题目数量

    # 获取题目数量
    p_num = re2[0][0] + re2[0][1] + re2[0][2]
    objIndex = list(range(re2[0][0] + re2[0][1]))  # 客观题下标
    subIndex = list(range(re2[0][0] + re2[0][1], p_num))  # 主观题下标

    choice_k = Sql_operation(cursor, sql2)  # 获取选择题知识点

    judge_k = Sql_operation(cursor, sql3)  # 获取判断题知识点

    subque_k = Sql_operation(cursor, sql4)  # 获取主观题知识点

    # 获取当前的做题情况
    sql_answer = "select sid,quizId from answer_copy1 \
    where quizId=15"
    sid_ans = Sql_operation(cursor, sql_answer)

    # 获取目前已有的测试
    sql_q = "select quizName from quiz"
    sql_quiz = Sql_operation(cursor, sql_q)
    advise_quiz = list(range(len(sql_quiz)))

    # 获取当前的视频资源
    sql_v_s = "select course,link from moocresource"
    sql_vedio_source = Sql_operation(cursor, sql_v_s)
    advise_source = list(range(len(sql_vedio_source)))

    # 获取学生做测试的情况
    sql_problem = "select DISTINCT sid,quizId from answer_copy1"
    sql_p_source = Sql_operation(cursor, sql_problem)

    # 获取学生学习科目情况
    sql_subject = "SELECT DISTINCT sid,moocvedio from users_dwelltime_tran_copy"
    sql_sub = Sql_operation(cursor, sql_subject)

    # 获取选择题和判断题的相应知识点说明
    sql_choice = "select id,knowledgeMeta2 from choicequestion"
    sql_judge = "select id,knowledgeMeta2 from judgementquestion"
    sql_subque = "select id,konwledgeMeta2 from subquestion"

    # 获取课件知识点信息
    sql_course = "select name,knowledgeMeta1,knowledgeMeta2 from coursewareresource"

    # 获取学生浏览课件信息
    sql_browse_ppt = "select sid,ppt_name from ppt_record"

    # 获取初始兴趣
    sql_initial_state = "select sid,interests from initial_interests"

    # ppt名称和id的映射关系
    ppt_project = "select id,name from coursewareresource"

    # mooc名称和id的映射关系
    mooc_project = "select id,course from moocresource"

    # quiz名称和id的映射关系
    quiz_project = "select quizId,quizName from quiz_copy1"

    choice_source = Sql_operation(cursor, sql_choice)
    judge_source = Sql_operation(cursor, sql_judge)
    subque_source = Sql_operation(cursor, sql_subque)

    ppt_source = Sql_operation(cursor, sql_course)  # 课件信息



    if JudgeStu(sid, sid_ans):
        X, stu2rows = Get_situation(results)  # 学生答题情况及行的映射关系，x学生，y答题情况
        Q, unit2pos = Ques_konwledge(p_num, choice_k, judge_k, subque_k)  # 问题知识点及知识点的列映射关系，x题目，y知识点

        pos2unit = {v: k for k, v in unit2pos.items()}
        rows2stu = {v: k for k, v in stu2rows.items()}

        stu_num, konw_num = len(X), len(Q[0])

        cdm = FuzzyCDF(X, Q, stu_num, p_num, konw_num, objIndex, subIndex, skip_value=-1)

        cdm.train(epoch=20, burnin=5)

        ls = [1, 2]  # 错题推荐，相似度推荐
        option = random.choice(ls)
        # 下面这部分需要放到经过判断后的错题推荐之上
        alpha, others = cal_alpha_mastery(cdm.a, cdm.b, cdm.theta, cdm.q_m, cdm.obj_prob_index, cdm.sub_prob_index)
        A_alls = alpha.copy()
        A_alls[A_alls < 0.6] = 0  # x为学生 y为知识点
        A_alls[A_alls >= 0.6] = 1

        point = A_alls[stu2rows[sid]]  # 暂时先放在这里

        x_y_unit = GetKonwledgeunit(point, ppt_source, unit2pos)  # 获取知识点得分，有名称
        # 作图
        DrawLine(x_y_unit,sid,path)  # 还有一个参数是path,默认为该路径

        dic = {}

        #  错题推荐

        sql = "insert into error_recommend(sid,recommend,type) values(%s,%s,%s) on duplicate key update recommend = values(recommend),type = values(type)"
        rec = Lackkonwlege(point, pos2unit, choice_source, judge_source, subque_source, ppt_source, rec_num=5)

         # 第一行是选择题，第二行是判断题
        s, type = PartialSep(rec[0], rec[1], rec[2], rec[3])  # 1c 2j 3 sub 4ppt
        cursor.execute(sql, (str(sid), s, type))
        db.commit()

        dic["Erro Recommend"]=[]
        dic["Erro Recommend"].append({"choice":rec[0]})
        dic["Erro Recommend"].append({"judge":rec[1]})
        dic["Erro Recommend"].append({"subject":rec[2]})


        # 相似度推荐

        sql = "insert into collaboration_recommend(sid,recommend,type) values(%s,%s,%s) on duplicate key update recommend = values(recommend),type = values(type)"
        sql_ppt = Sql_operation(cursor, sql_browse_ppt)

        rec2 = SimilarRecommend(sid, sql_p_source, stu2rows, rows2stu, A_alls, num=5) # 测试
        rec_ppt = SimilarRecommend(sid, sql_ppt, stu2rows, rows2stu, A_alls, num=5)  # ppt
        rec_v = SimilarRecommend(sid, sql_sub, stu2rows, rows2stu, A_alls, num=5)  # 视频

        rec_v = Name2id(cursor, mooc_project, rec_v)
        s, type = PartialSep(rec_v, rec, data4=rec_ppt)
        cursor.execute(sql, (str(sid), s, type))
        db.commit()


        dic["Similar Recommend"]=[]
        dic["Similar Recommend"].append({"mooc_vedio":rec_v})

        dic["Similar Recommend"].append({"quiz":rec2})
        PPT_source = list(set(rec[3]+rec_ppt))

        PPT_source = Name2id(cursor,ppt_project,PPT_source)

        dic["PPT Source"] = PPT_source

        # 关闭数据库连接
        db.close()
        return json.dumps(dic)
        # dic转换成json
    else:

        initial_state = Sql_operation(cursor, sql_initial_state)
        sql = "insert into initial_recommend(sid,recommend,type) values(%s,%s,%s) on duplicate key update recommend = values(recommend),type = values(type)"
        dic = {}

        if JudgeStu(sid, initial_state):

            dic["Initial_key"] = []
            name1 = Initial_key(sql_vedio_source, initial_state,sid)  # 推荐视频


            name2 = Initial_key(sql_quiz, initial_state,sid)  # 推荐测试


            ls = []
            for k in initial_state:
                if sid == k[0]:
                    ls = k[1].split(",")
                    break

            if "java" in ls:
                advise_ppt = list(range(len(ppt_source)))
                name4 = InitialRecommend(advise_ppt, ppt_source)
                # 获取要提交上去的元组组成元素
                name1 = Name2id(cursor, mooc_project, name1)
                name2 = Name2id(cursor, quiz_project, name2)
                name4 = Name2id(cursor, ppt_project, name4)
                s, type = PartialSep(name1, name2, data4=name4)



                dic["Initial_key"].append({"mooc_vedio": name1})
                dic["Initial_key"].append({"quiz": name2})
                dic["Initial_key"].append({"ppt":name4})

            else:
                name1 = Name2id(cursor, mooc_project, name1)
                name2 = Name2id(cursor, quiz_project, name2)
                s, type = PartialSep(name1, name2)
                dic["Initial_key"].append({"mooc_vedio":name1})
                dic["Initial_key"].append({"quiz": name2})
        else:
            dic["Initial"] = []
            # 初始化，随机推荐
            name1 = InitialRecommend(advise_source, sql_vedio_source)  # 推荐视频


            name2 = InitialRecommend(advise_quiz, sql_quiz)  # 推荐测试


            advise_ppt = list(range(len(ppt_source)))
            name4 = InitialRecommend(advise_ppt, ppt_source)

            name1 = Name2id(cursor, mooc_project, name1)
            name2 = Name2id(cursor, quiz_project, name2)
            name4 = Name2id(cursor, ppt_project, name4)

            # 获取要提交上去的元组组成元素
            s, type = PartialSep(name1, name2, data4=name4)

            dic["Initial"].append({"mooc_vedio":name1})
            dic["Initial"].append({"quiz":name2})
            dic["Initial"].append({"ppt":name4})

        # dic转换成json

        cursor.execute(sql, (sid, s, type))
        db.commit()
        # 关闭数据库连接
        db.close()
        return json.dumps(dic)


if __name__ == "__main__":
    d = {"host": "localhost", "user": "root", "password": "111111", "database": "online_edu"}
    sid = 1
    print(Draw_Recommend(sid,**d))