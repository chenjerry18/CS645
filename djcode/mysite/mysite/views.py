from django.http import HttpResponse, Http404
from django.shortcuts import render_to_response
import datetime
from django.views.decorators.csrf import csrf_exempt
import psycopg2
import json
import re
import random
import time
# from utils import getContent, generateFeatures, getSuggestionsFeatures

def hello(request):
    return HttpResponse("Hello world")

def current_datetime(request):
    now = datetime.datetime.now()
    # html = "<html><body>It is now %s.</body></html>" % now
    # return HttpResponse(html)
    return render_to_response('current_datetime.html', {'current_date': now})


def hours_ahead(request, offset):
    try:
        offset = int(offset)
    except ValueError:
        raise Http404()
    dt = datetime.datetime.now() + datetime.timedelta(hours=offset)
    html = "<html><body>In %s hour(s), it will be %s.</body></html>" % (offset, dt)
    return HttpResponse(html)

@csrf_exempt 
def change(request):
    if 'input' in request.GET:
        p1 = request.GET['input']
        print("input------------: ", p1)
        conn = psycopg2.connect("dbname=query_repo user=postgres password=223378")
        sql = "select qfid, feature from queryfeatures limit 5"
        cursor = conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchmany(4)
        state_dict = []
        for r in result:
            state_dict.append({"shortcut":str(r[0]),"fullname":r[1]})
        print("state_dict: ", state_dict)
        return render_to_response('basic.html', {'item_list': state_dict})

@csrf_exempt
def datagrid(request):
    if 'input' in request.GET and 'clause' in request.GET:
        p1 = request.GET['input']
        p2 = request.GET['clause']
        if isinstance(p1, str) and len(p1) and isinstance(p2, str) and len(p2):
            ss = getContentSugg(p1)
            # print('ss: ', ss)
            result_raw = generateFeatures(ss)
            result = []
            for r in result_raw:
                result += r
            result_g = []
            for r in result:
                r_temp = r.replace(" ","")
                # print("r_temp: ", r_temp)
                result_g.append(r_temp)
            print('result_g: ', result_g)
            original_features = []
            for r in result_g:
                original_features.append(r)
            clause = str(p2).upper()
            sugg, t_cost = getSuggestionsFeatures(original_features, 3, clause)
            # print("sugg: ", sugg)
            s_list = []
            for s in sugg:
                s_list.append({"suggestion":s,"response_time":("%.4f" % t_cost)})
            # print("input------------: ", p1)
            # r_time = json.dumps("2mms")
            # sugg = json.dumps("sss")
            # s_list = [{"suggestion":str(p1)},{"suggestion":str(p2)}]
            print("s_list: ",s_list)
            ealist = {"rows":s_list}
            easylist = json.dumps(ealist)
            return HttpResponse(easylist)
        else:
            s_list = []
            ealist = {"rows":s_list}
            easylist = json.dumps(ealist)
            return HttpResponse(easylist)
    else:
        s_list = []
        ealist = {"rows":s_list}
        easylist = json.dumps(ealist)
        return HttpResponse(easylist)

@csrf_exempt 
def combobox(request):
    if 'input' in request.GET and 'clause' in request.GET:
        p1 = request.GET['input']
        p2 = request.GET['clause']
        # print("input------------: ", p1)
        conn = psycopg2.connect("dbname=query_repo user=postgres password=223378")
        sql = "select qfid, feature from queryfeatures limit 5"
        cursor = conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchmany(4)
        state_dict = []
        for r in result:
            state_dict.append({"shortcut":r[0],"fullname":r[1]})
        print("state_dict: ", state_dict)
        return render_to_response('basic.html', {'item_list': state_dict})
    else:
        # state_dict = [{"shortcut":"MA","fullname":"Massachusetts"},{"shortcut":"NY","fullname":"New York"},{"shortcut":"WA","fullname":"Washigton"}]
        # state_dict= []
        conn = psycopg2.connect("dbname=query_repo user=postgres password=223378")
        sql = "select qfid, feature from queryfeatures limit 5"
        cursor = conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchmany(4)
        state_dict = []
        for r in result:
            state_dict.append({"shortcut":r[0],"fullname":r[1]})
        print("state_dict: ", state_dict)
        return render_to_response('basic.html', {'item_list': state_dict})

def tokenize(s):
    r1 = r1 = re.sub(r'\n',"",s)
    r1 = re.sub(r',\s+',",",r1)
    r1 = re.sub(r'\s+'," ",r1)
    r1 = r1.lstrip()
    r1 = r1.rstrip()
    return r1

def getContentSugg(s):
    s = s.upper()
    # print("s: ",s)
    s_exist = re.search('SELECT', s)
    w_exist = re.search('WHERE', s)
    f_exist = re.search('FROM', s)
    # print("s_exist: ",s_exist)
    content1 = ""
    content2 = ""
    content3 = ""
    if s_exist is not None:
        temp1 = s.split('SELECT')
        # print("temp1",temp1)
        if len(temp1)>1:
            content1 = temp1[1]
    # print("content1: ", content1)
    if s_exist is not None and f_exist is not None:
        temp2 = content1.split('FROM')
        if len(temp2)>1:
            content2 = temp2[1]
        content1 = content1.split('FROM')[0]
    # print("content2: ", content2)
    if s_exist is not None and f_exist is not None and w_exist is not None:
        temp3 = content2.split('WHERE')
        if len(temp3)>1:
            content3 = temp3[1]
        content2 = content2.split('WHERE')[0]
    return str(content1), str(content2), str(content3)


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
    
    # print("f: ", features)
    for f in features:
        count+=1
        f_insert += "'%s'"%(f)
        if count!=length:
            f_insert += ", "
    # print("f_insert: ",f_insert)
    suggestions = []
    # print("len:", length)

    i = length
    while len(suggestions)<K and i>0:
        conn = psycopg2.connect("dbname=query_repo user=postgres password=223378")
        sql_pre = "with SimilarQueries AS (select query from queryfeatures2 where feature in (%s) group by query having count(feature)=%d) select qf.feature from queryfeatures2 qf, SimilarQueries s where qf.query = s.query and qf.feature not in (%s) and clause='%s' group by qf.feature order by count(s.query) desc" % (f_insert, i, f_insert,c)
        # print("sql: ",sql_pre)
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
    print("suggestions: ",suggestions)
    return suggestions, t2-t1

