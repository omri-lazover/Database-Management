
from django.shortcuts import render
from .models import Programranks, Households, Recordorders, Programs, Recordreturns
from django.db import connection

# Create your views here.
def dictfetchall(cursor):
    # Returns all rows from a cursor as a dict
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def index(request):
    return render(request, 'index.html')

def Query_results(request):
    with connection.cursor() as cursor:
        cursor.execute("""
    SELECT P.genre, P.title, P.duration
    FROM MaxDurationTitle MDT inner join Programs P on MDT.title = P.title
    EXCEPT
    SELECT P.genre, P.title, P.duration
    FROM MaxDurationTitle MDT inner join Programs P on MDT.title = P.title
    WHERE P.title>MDT.title
    ORDER BY genre; """)

        sql_res1 = dictfetchall(cursor)


    with connection.cursor() as cursor:
        cursor.execute("""  
    SELECT PR.title, cast(avg(cast(PR.rank as float))as decimal(10,2)) as AvgRank
    FROM ProgramRanks PR, EnoughGoodGrades EGG
    WHERE PR.title=EGG.title
    GROUP BY PR.title
    ORDER BY AvgRank desc, PR.title;
    """)
        sql_res2 = dictfetchall(cursor)

    with connection.cursor() as cursor:
        cursor.execute("""
    SELECT Distinct TMO.title
FROM tenOrMoreOrders TMO inner join RichFamiliesReturned RFR
    on TMO.title=RFR.title
WHERE 0.5*TMO.familiesOrdered<RFR.RichReturned
EXCEPT
SELECT DISTINCT PR.title
FROM ProgramRanks PR
WHERE PR.rank<2;""")

        sql_res3 = dictfetchall(cursor)



    return render(request, 'Query_results.html',{'sql_res1': sql_res1, 'sql_res2': sql_res2, 'sql_res3': sql_res3})

def Records_Management(request):
    sql = """
    SELECT top 3 count(*) as TotalOrders, Tos.hID
FROM TotalOrders Tos
GROUP BY Tos.hID
ORDER BY TotalOrders desc, Tos.hID;
    """
    sql_res = Households.objects.raw(sql)




    if request.method == 'POST' and request.POST:
        hid = int(request.POST["hID"])
        title = request.POST["Title"]
        if not Households.objects.filter(hid=hid).exists():
            return render(request, 'Records_Management.html', {'exeption1': 1, 'sql_res': sql_res})
        if not Programs.objects.filter(title=title).exists():
            return render(request, 'Records_Management.html', {'exeption2': 1, 'sql_res': sql_res})

        Message_me = Recordorders.objects.filter(hid=hid).count()
        if Message_me == 3:
            return render(request, 'Records_Management.html', {'exeption3': 1, 'sql_res': sql_res})

        if Recordorders.objects.filter(title=title, hid=hid).exists():
            return render(request, 'Records_Management.html', {'exeption5': 1, 'sql_res': sql_res})
        if Recordorders.objects.filter(title=title).exists():
            return render(request, 'Records_Management.html', {'exeption4': 1, 'sql_res': sql_res})
        if Recordreturns.objects.filter(title=title, hid=hid).exists():
            return render(request, 'Records_Management.html', {'exeption6': 1,'sql_res': sql_res})


        sql_res7 = Households.objects.raw("""select *
        from Households H, Programs P
        WHERE P.genre = 'Adults only' and P.title = %s and  H.hID = %s and H.ChildrenNum>0
            """, [title, hid])
        if sql_res7:
            return render(request, 'Records_Management.html', {'exeption7': 1,'sql_res': sql_res})
        else:
            new_request = Recordorders(title=Programs.objects.get(title=title), hid=Households.objects.get(hid=hid))
            new_request.save()
            return render(request, 'Records_Management.html', { 'NoProblem': 1, 'sql_res': sql_res})


    return render(request, 'Records_Management.html', {'sql_res': sql_res})


def Record_Return(request):
    sql = """
        SELECT top 3 count(*) as TotalOrders, PR.hID, max(PR.title) as title
        FROM ProgramRanks PR
        GROUP BY PR.hID
        ORDER BY TotalOrders desc, PR.hID
        """
    sql_res = Households.objects.raw(sql)

    hid = int(request.POST["hID"])
    title = request.POST["Title"]
    if not Households.objects.filter(hid=hid).exists():
        return render(request, 'Records_Management.html', {'exeption8': 1, 'sql_res': sql_res})
    if not Programs.objects.filter(title=title).exists():
        return render(request, 'Records_Management.html', {'exeption9': 1, 'sql_res': sql_res})
    if not Recordorders.objects.filter(title=title, hid=hid).exists():
        return render(request, 'Records_Management.html', {'exeption10': 1, 'sql_res': sql_res})
    else:

        deleted = Recordorders.objects.get(title=title, hid=hid)
        deleted.delete()

        with connection.cursor() as cursor:
            cursor.execute("""INSERT INTO RecordReturns (title, hID) 
            VALUES (%s,%s)
         """, [title, hid])
        return render(request, 'Records_Management.html', {'sql_res': sql_res, 'exeption11': 1})

def Rankings(request):
    with connection.cursor() as cursor:
        families_scroll_sql = """select hID from Households"""
        cursor.execute(families_scroll_sql)
        hIDs = dictfetchall(cursor)

        program_scroll_sql = """select title from Programs"""
        cursor.execute(program_scroll_sql)
        titles = dictfetchall(cursor)

        cursor.execute("""
                        SELECT Genre as genre
                        FROM Programs
                        group by Genre
                        HAVING count(distinct title)>=5;
                        """)
        sql_res1 = dictfetchall(cursor)




    if request.method == 'POST' and request.POST:
        if 'addGrade' in request.POST:
            hid = int(request.POST["hID"])
            title = request.POST["Title"]
            grade = request.POST["grade"]
            if not Programranks.objects.filter(hid=hid, title=title).exists():
                with connection.cursor() as cursor:
                    cursor.execute("""
                    INSERT INTO ProgramRanks (title, hID, rank)
VALUES (%s, %s, %s)
                                               """, [title, hid, grade])
                return render(request, 'Rankings.html', {'sql_res1': sql_res1,
                                                         'hIDs': hIDs,
                                                         'titles': titles})
            else:
                programRank = Programranks.objects.filter(hid=hid, title=title).update(rank=grade)
                #programRank.rank=grade
                #programRank.save(update_fields=['rank'])
                return render(request, 'Rankings.html', {'sql_res1': sql_res1,
                                                         'hIDs': hIDs,
                                                         'titles': titles})
        else:
            minrank=request.POST["minRank"]
            genre = request.POST["Genre"]
            with connection.cursor() as cursor:
                min_ranks_sql = """select TOP 5 PR.title, cast(avg(cast((PR.rank) as decimal)) as decimal(10,2)) as Average_Rank
                                from ProgramRanks PR
                                where PR.title in (select P.title from Programs P where genre=%s)
                                group by PR.title
                                having count(*) >= %s
                                order by Average_Rank desc"""
                cursor.execute(min_ranks_sql, [genre, minrank])
                min_ranks_sql = dictfetchall(cursor)
                n = len(min_ranks_sql)
                if n < 5:
                    with connection.cursor() as cursor:
                        complete_table_sql = """SELECT TOP (5-%s) PR.title, 0 as Average_Rank
                                        FROM Programs PR
                                        WHERE PR.title in (SELECT P.title FROM Programs P WHERE genre = %s)
                                        And PR.title not in 
                                        (
                                        select TOP 5 PR.title
                                from ProgramRanks PR
                                where PR.title in (select P.title from Programs P where genre=%s)
                                group by PR.title
                                having count(*) >= %s
                                        )
                                        GROUP BY PR.title
                                        HAVING count(*) < %s
                                        ORDER BY PR.title ASC"""
                        cursor.execute(complete_table_sql, [n, genre, genre, minrank, minrank])
                        min_ranks_sql += dictfetchall(cursor)
            return render(request, 'Rankings.html', {'sql_res1': sql_res1,
                                                     'min_ranks_sql': min_ranks_sql,
                                                     'hIDs': hIDs,
                                                     'titles': titles})







    return render(request, 'Rankings.html', {'sql_res1': sql_res1,
                                             'hIDs': hIDs,
                                             'titles': titles})
