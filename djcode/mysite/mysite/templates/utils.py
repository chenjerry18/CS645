import csv
import datetime
import re
import random
from random import shuffle
import time
import psycopg2

def tokenize(s):
    r1 = r1 = re.sub(r'\n',"",s)
    r1 = re.sub(r',\s+',",",r1)
    r1 = re.sub(r'\s+'," ",r1)
    r1 = r1.lstrip()
    r1 = r1.rstrip()
    return r1

def getContent(s):
    s = s.upper()
    snip1 = s.split('FROM')
    content1 = snip1[0].split('SELECT')[1]
    snip3 = snip1[1].split('WHERE')
    if len(snip3)>1:
        content3 = snip3[1]
    else:
        content3 = ""
    content2 = snip3[0]
    r1 = tokenize(content1)
    r2 = tokenize(content2)
    r3 = tokenize(content3)
    return str(r1), str(r2), str(r3)


def generateFeatures(ss):
    
    
    cond_g = ss[2]
    copc_group = re.findall("(\w+[.]\w+\W\w+[.]\w+)",cond_g, re.M|re.I)
    copconstant_group = re.findall("(\w+[.]\w+\W\w+[.]?\w+)",cond_g, re.M|re.I)
    t_g = ss[1]
#     print("t_g", t_g)
    table_groups = re.findall("(\w+?\S+\s\w+)", t_g, re.M|re.I)
    
    if len(table_groups)==0:
        result_g = ss[0].split(",")
#         print("t_g==0: ",result_g)
        tables = ss[1].split(",")
        conditions = cond_g.split(",")
        conditionsNew = []
        for c in conditions:
            m2 = re.search("(\w+\W)",cond_g, re.M|re.I)
            cc = ""
            if m2 is not None:
                cc = c[m2.span()[0]:m2.span()[1]]+"#"
            else:
                cc = c
            conditionsNew.append(cc)
        return result_g, tables, conditionsNew
    else:
        dict_ = dict()
#         print("t_groups: ", table_groups)
        for t in table_groups:
            s_temp = t.split(" ")
#             print("s",s_temp)
    #         print(s_temp)
            t_name = s_temp[0]
            t_alias = s_temp[1]
            dict_[t_alias] = t_name
        #replace alias in select clause with true table name
        sql_ = ss[0]
        sql_g = sql_.split(",")
        set_g = set()
        for g in sql_g:
            if len(g.split())>1:
                set_g.add(g.split()[-1])
            else:
                set_g.add(g)
        result_g = []
        conditions = []
        for t in dict_:
            for g in set_g:
                m = re.search(t+".",g)
                if not m:
                    continue
                g = re.sub(t+".",dict_[t]+".",g)
                result_g.append(g)
            for c in copc_group:
                m = re.search(t+".",g)
                if not m:
                    continue
#         print("copc: ", copc_group)
        for c in copc_group:
            g = c
            for t in dict_:
#                 print("t: ", t)
                m = re.match(t+".", c)
#                 print("m: ", m)
#                 print("--", t+".")
                g = re.sub(t+".",dict_[t]+".",g)
            conditions.append(g)
#         print("constant: ", copconstant_group)
        for c in copconstant_group:
            if c in copc_group:
                continue
            else:
                g = c 
                m2 = re.search("\w+[.]\w+\W",g)
                if m2:
                    g = g[m2.span()[0]:m2.span()[1]]+"#"
                for t in dict_:
                    g = re.sub(t+".",dict_[t]+".",g)
                conditions.append(g)
        return  result_g, list(dict_.values()), conditions

def getSuggestionsFeatures(features, K, c):
    t1= time.clock()
    f_insert = ""
#     features = []
    count = 0
#     for f_ in f:
#         features += f
    length = len(features)
    
#     print("f: ", features)
    for f in features:
        count+=1
        f_insert += "'%s'"%(f)
        if count!=length:
            f_insert += ", "
#     print(f_insert)
    suggestions = []
    i = length
    while len(suggestions)<K and i>0:
        conn = psycopg2.connect("dbname=query_repo user=postgres password=223378")
        sql_pre = "with SimilarQueries AS (select query from queryfeatures2 where feature in (%s) group by query having count(feature)=%d) select qf.feature from queryfeatures2 qf, SimilarQueries s where qf.query = s.query and qf.feature not in (%s) and clause='%s' group by qf.feature order by count(s.query) desc" % (f_insert, i, f_insert,c)
#         print("sql: ",sql_pre)
        cur = conn.cursor()
        cur.execute(sql_pre)
        fetch_result = cur.fetchmany(K)
#         print("fetch: ",fetch_result)
        for f_r in fetch_result:
            sugg_temp = f_r[0]
            if sugg_temp not in suggestions:
                suggestions.append(f_r[0])
        i = i-1
    t2=time.clock()
    return suggestions, t2-t1

