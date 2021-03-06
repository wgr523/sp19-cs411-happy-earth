from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views import generic
from django.urls import reverse
from django.db import connection
from .models import *
import datetime
from background_task import background


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [ dict(zip(columns, row)) for row in cursor.fetchall() ]

def get_restaurant_date(rid):
    with connection.cursor() as c:
        c.execute('SELECT name, address, city, state, price_level FROM happyearth_restaurant WHERE id=%s;', [rid])
        r = dictfetchall(c)[0]
        r['price_level'] = '$'*r['price_level']
        c.execute('SELECT dish_id FROM happyearth_serve WHERE restaurant_id=%s;', [rid])
        d = dictfetchall(c)
        c.execute('SELECT c.date, c.rating, c.review FROM happyearth_comment c WHERE c.restaurant_id=%s AND c.dish_id IS NULL;', [rid])
        comments = dictfetchall(c)
        c.execute('SELECT c.date, c.dish_id, c.rating, c.review FROM happyearth_comment c WHERE c.restaurant_id=%s AND c.dish_id IS NOT NULL;', [rid])
        comments_dishes = dictfetchall(c)
        context = {'dishes': d, 'restaurant': r, 'comments': comments, 'comments_dishes': comments_dishes}
        return context

def user_home(request):
    if request.user.is_authenticated:
        username = request.user.get_username()
        if request.method.upper() == "POST":
            try:
                city = request.POST['city']
                state = request.POST['state']
                date = datetime.datetime.now().strftime("%Y-%m-%d")
                with connection.cursor() as c:
                    c.execute('INSERT IGNORE INTO happyearth_user (name, city, state, reg_date) VALUES (%s, %s, %s, %s);', [username, city, state, date])
            except:
                return HttpResponse("Error. Invalid POST request.")        
        user = User.objects.raw('SELECT name, city, state FROM happyearth_user WHERE name=%s LIMIT 1;', [username])
        if len(user)!=1:
            return render(request, 'happyearth/user_info.html')
        user_info = {"name":user[0].name, "city":user[0].city, "state":user[0].state}
        with connection.cursor() as c:
            c.execute('SELECT r.id, r.name, r.address, r.city, r.state FROM happyearth_restaurant AS r, happyearth_recommend as l WHERE l.user_id=%s AND l.restaurant_id = r.id AND r.city = %s AND r.state = %s;', [user_info['name'], user_info['city'], user_info['state']])
            restaurants = dictfetchall(c)
        context= {'restaurants': restaurants, 'user_info': user_info}
        return render(request, 'happyearth/user_home.html', context)
    else:#TODO: create a homepage with no user info
        return render(request, 'happyearth/user_home.html')
        #return HttpResponseRedirect(reverse('login'))

def user_favorites(request):
    if request.user.is_authenticated:
        username = request.user.get_username()
        user = User.objects.raw('SELECT name, city, state FROM happyearth_user WHERE name=%s LIMIT 1;', [username])
        if len(user)!=1:
            return HttpResponse("No this user data.")
        user_info = {"name":user[0].name, "city":user[0].city, "state":user[0].state}
        with connection.cursor() as c:
            c.execute('SELECT DISTINCT tag FROM happyearth_favorites WHERE user_id=%s;', [username])
            tags = dictfetchall(c)
        context = {'user_info': user_info, 'tags': tags}
        return render(request, 'happyearth/user_favorites.html', context)
    else:
        return HttpResponseRedirect(reverse('login'))

def user_favorites_tag(request, tag):
    if request.user.is_authenticated:
        username = request.user.get_username()
        user = User.objects.raw('SELECT name, city, state FROM happyearth_user WHERE name=%s LIMIT 1;', [username])
        if len(user)!=1:
            return HttpResponse("No this user data.")
        user_info = {"name":user[0].name, "city":user[0].city, "state":user[0].state}
        with connection.cursor() as c:
            c.execute('SELECT r.id, r.name, r.address, r.city, r.state FROM happyearth_favorites f, happyearth_restaurant r WHERE f.user_id=%s AND f.tag=%s AND r.id=f.restaurant_id;', [username, tag])
            restaurants = dictfetchall(c)
        context = {'user_info': user_info, 'restaurants': restaurants}
        return render(request, 'happyearth/favorites_tag.html', context)
    else:
        return HttpResponseRedirect(reverse('login'))

def restaurant_id(request, rid):
    context = get_restaurant_date(rid)
    if request.user.is_authenticated:
        username = request.user.get_username()
        user = User.objects.raw('SELECT name, city, state FROM happyearth_user WHERE name=%s LIMIT 1;', [username])
        if len(user)!=1:
            return HttpResponse("No this user data.")
        user_info = {"name":user[0].name, "city":user[0].city, "state":user[0].state}
        with connection.cursor() as c:
            c.execute('SELECT * FROM happyearth_favorites WHERE user_id=%s AND restaurant_id=%s LIMIT 1;', [username, rid])
            if len(c.fetchall())>0:
                is_fav = True
            else:
                is_fav = False
            context.update({'user_info': user_info, 'is_favorite': is_fav })
    return render(request, 'happyearth/restaurant.html', context)

def restaurant_id_edit(request, rid):
    with connection.cursor() as c:
        c.execute('SELECT name, address, city, state, price_level FROM happyearth_restaurant WHERE id=%s;', [rid])
        r = dictfetchall(c)[0]
        r['price_level'] = '$'*r['price_level']
        c.execute('SELECT dish_id FROM happyearth_serve WHERE restaurant_id=%s;', [rid])
        d = dictfetchall(c)
        context = {'dishes': d, 'restaurant': r}
    if request.user.is_authenticated:
        username = request.user.get_username()
        user = User.objects.raw('SELECT name, city, state FROM happyearth_user WHERE name=%s LIMIT 1;', [username])
        if len(user)!=1:
            return HttpResponse("No this user data.")
        user_info = {"name":user[0].name, "city":user[0].city, "state":user[0].state}
        with connection.cursor() as c:
            c.execute('SELECT c.id, c.date, c.rating, c.review FROM happyearth_comment c WHERE c.user_id=%s AND c.restaurant_id=%s AND c.dish_id IS NULL;', [username, rid])
            comments = dictfetchall(c)
            c.execute('SELECT c.id, c.dish_id, c.date, c.rating, c.review FROM happyearth_comment c WHERE c.user_id=%s AND c.restaurant_id=%s AND c.dish_id IS NOT NULL;', [username, rid])
            comments_dishes = dictfetchall(c)
            c.execute('SELECT * FROM happyearth_favorites WHERE user_id=%s AND restaurant_id=%s LIMIT 1;', [username, rid])
            if len(c.fetchall())>0:
                is_fav = True
            else:
                is_fav = False
            context.update({'user_info': user_info, 'is_favorite': is_fav ,'comments': comments, 'comments_dishes': comments_dishes})
    return render(request, 'happyearth/restaurant_edit.html', context)

def restaurant_id_comment(request, rid):
    if request.user.is_authenticated:
        username = request.user.get_username()
        user = User.objects.raw('SELECT name, city, state FROM happyearth_user WHERE name=%s LIMIT 1;', [username])
        if len(user)!=1:
            return HttpResponse("No this user data.")
        user_info = {"name":user[0].name, "city":user[0].city, "state":user[0].state}
        ## Below process comment
        if request.method.upper() == "POST":
            try:
                rating = request.POST['rating']
                if 'is_dish' in request.POST:
                    dish = request.POST['dish']
                else:
                    dish = ""
                review = request.POST['review']
                date = datetime.datetime.now().strftime("%Y-%m-%d")
                with connection.cursor() as c:
                    if dish == "":
                        c.execute('INSERT INTO happyearth_comment (user_id, restaurant_id, rating, review, date) VALUES (%s, %s, %s, %s, %s);', [user_info['name'], rid, rating, review, date])
                    else:
                        c.execute('INSERT IGNORE INTO happyearth_dish (name, description) VALUES (%s, %s);', [dish, ''])
                        c.execute('INSERT IGNORE INTO happyearth_serve (dish_id, restaurant_id) VALUES (%s, %s);', [dish, rid])
                        c.execute('INSERT INTO happyearth_comment (dish_id, user_id, restaurant_id, rating, review, date) VALUES (%s, %s, %s, %s, %s, %s);', [dish, user_info['name'], rid, rating, review, date])
                return HttpResponseRedirect('..')
            except:
                return HttpResponse("Error when creating comment.")
        ## Process comment ends
        with connection.cursor() as c:
            c.execute('SELECT name, address, city, state, price_level FROM happyearth_restaurant WHERE id=%s;', [rid])
            r = dictfetchall(c)[0]
            r['price_level'] = '$'*r['price_level']
            c.execute('SELECT dish_id FROM happyearth_serve WHERE restaurant_id=%s;', [rid])
            d = dictfetchall(c)
            context = {'user_info': user_info, 'dishes': d, 'restaurant': r}
        return render(request, 'happyearth/restaurant_comment.html', context)
    else:
        return HttpResponseRedirect(reverse('login'))

def restaurant_id_edit_comment(request, rid, cid):
    if request.user.is_authenticated:
        username = request.user.get_username()
        user = User.objects.raw('SELECT name, city, state FROM happyearth_user WHERE name=%s LIMIT 1;', [username])
        if len(user)!=1:
            return HttpResponse("No this user data.")
        user_info = {"name":user[0].name, "city":user[0].city, "state":user[0].state}
        ## Below process comment
        if request.method.upper() == "POST":
            try:
                rating = request.POST['rating']
                if 'is_dish' in request.POST:
                    dish = request.POST['dish']
                else:
                    dish = ""
                review = request.POST['review']
                date = datetime.datetime.now().strftime("%Y-%m-%d")
                with connection.cursor() as c:
                    if dish == "":
                        c.execute('UPDATE happyearth_comment SET dish_id=NULL, rating=%s, review=%s, date=%s WHERE id=%s AND user_id=%s;', [rating, review, date, cid, user_info['name']])
                    else:
                        c.execute('INSERT IGNORE INTO happyearth_dish (name, description) VALUES (%s, %s);', [dish, ''])
                        c.execute('INSERT IGNORE INTO happyearth_serve (dish_id, restaurant_id) VALUES (%s, %s);', [dish, rid])
                        c.execute('UPDATE happyearth_comment SET dish_id=%s, rating=%s, review=%s, date=%s WHERE id=%s AND user_id=%s;', [dish, rating, review, date, cid, user_info['name']])
                return HttpResponseRedirect('..')
            except:
                return HttpResponse("Error when editing comment.")
        ## Process comment ends
        with connection.cursor() as c:
            c.execute('SELECT name, address, city, state, price_level FROM happyearth_restaurant WHERE id=%s;', [rid])
            r = dictfetchall(c)[0]
            r['price_level'] = '$'*r['price_level']
            c.execute('SELECT dish_id FROM happyearth_serve WHERE restaurant_id=%s;', [rid])
            d = dictfetchall(c)
            c.execute('SELECT rating, review, dish_id FROM happyearth_comment WHERE id=%s;', [cid])
            comment = dictfetchall(c)
            if len(comment)!=1:
                return HttpResponse("No such comment.")
            context = {'user_info': user_info, 'dishes': d, 'restaurant': r, 'comment': comment[0]}
        return render(request, 'happyearth/restaurant_comment.html', context)
    else:
        return HttpResponseRedirect(reverse('login'))

def restaurant_id_delete_comment(request, rid, cid):
    if request.user.is_authenticated:
        username = request.user.get_username()
        user = User.objects.raw('SELECT name, city, state FROM happyearth_user WHERE name=%s LIMIT 1;', [username])
        if len(user)!=1:
            return HttpResponse("No this user data.")
        user_info = {"name":user[0].name, "city":user[0].city, "state":user[0].state}
        try:
            with connection.cursor() as c:
                c.execute('DELETE FROM happyearth_comment WHERE id=%s AND user_id=%s;', [cid, user_info['name']])
        except:
            return HttpResponse("Error when deleting comment.")
        return HttpResponseRedirect('../..')
    else:
        return HttpResponseRedirect(reverse('login'))

@background(schedule=0)
def insert_recommend_background(uid, rid):
    with connection.cursor() as c:
        c.execute('CALL InsertRecommendRestaurant(%s, %s);', [uid, rid])
        c.execute('CALL InsertRecommendRestaurant2(%s, %s);', [uid, rid])

def restaurant_id_favorite(request, rid):
    if request.user.is_authenticated:
        username = request.user.get_username()
        user = User.objects.raw('SELECT name, city, state FROM happyearth_user WHERE name=%s LIMIT 1;', [username])
        if len(user)!=1:
            return HttpResponse("No this user data.")
        user_info = {"name":user[0].name, "city":user[0].city, "state":user[0].state}
        ## Below process favorite
        if True:
            with connection.cursor() as c:
                c.execute('INSERT IGNORE INTO happyearth_favorites (user_id, restaurant_id, tag) VALUES (%s, %s, %s);', [user_info['name'], rid, 'default'])
                insert_recommend_background(user_info['name'], rid)
        return HttpResponseRedirect('..')
        ## Process ends
    else:
        return HttpResponseRedirect(reverse('login'))

def search_result(request):
    if request.method.upper() == "GET":
        try:
            if 'restaurant' in request.GET:
                r = request.GET['restaurant'].lower()
            else:
                r = ''
            if 'address' in request.GET:
                a = request.GET['address'].lower()
            else:
                a = ''
            rank_by_rating = 'rank' in request.GET
        except:
            return HttpResponse("Error. Invalid GET request.")
    if request.user.is_authenticated:
        username = request.user.get_username()
        user = User.objects.raw('SELECT name, city, state FROM happyearth_user WHERE name=%s LIMIT 1;', [username])
        if len(user)!=1:
            return HttpResponse("No this user data.")
        user_info = {"name":user[0].name, "city":user[0].city, "state":user[0].state}
        with connection.cursor() as c:
            if rank_by_rating:
                c.execute('SELECT r.id, r.name, r.address, r.city, r.state, n.avg_rating FROM happyearth_restaurant AS r, restaurant_rating AS n WHERE r.id = n.restaurant_id AND r.city=%s AND r.state=%s AND lower(r.name) LIKE %s AND lower(r.address) LIKE %s ORDER BY n.avg_rating DESC;', [user_info['city'], user_info['state'], r'%'+r+r'%', r'%'+a+r'%'])
            else:
                c.execute('SELECT id, name, address, city, state FROM happyearth_restaurant WHERE city=%s AND state=%s AND lower(name) LIKE %s AND lower(address) LIKE %s;', [user_info['city'], user_info['state'], r'%'+r+r'%', r'%'+a+r'%'])# we only search restaurant in same city, state
            restaurants = dictfetchall(c)
        context= {'restaurants': restaurants, 'user_info': user_info}
    else:
        with connection.cursor() as c:
            if rank_by_rating:
                c.execute('SELECT r.id, r.name, r.address, r.city, r.state, n.avg_rating FROM happyearth_restaurant AS r, restaurant_rating AS n WHERE r.id = n.restaurant_id AND lower(name) LIKE %s AND lower(address) LIKE %s ORDER BY n.avg_rating DESC LIMIT 100;', [r'%'+r+r'%', r'%'+a+r'%'])
            else:
                c.execute('SELECT id, name, address, city, state FROM happyearth_restaurant WHERE lower(name) LIKE %s AND lower(address) LIKE %s LIMIT 100;', [r'%'+r+r'%', r'%'+a+r'%'])
            restaurants = dictfetchall(c)
        context = {'restaurants': restaurants}
    return render(request, 'happyearth/search_list.html', context)

def user_together(request):
    if request.user.is_authenticated:
        username = request.user.get_username()
        user = User.objects.raw('SELECT name, city, state FROM happyearth_user WHERE name=%s LIMIT 1;', [username])
        if len(user)!=1:
            return HttpResponse("No this user data.")
        user_info = {"name":user[0].name, "city":user[0].city, "state":user[0].state}
        if request.method.upper() == "POST":
            try:
                code = request.POST['code']
                with connection.cursor() as c:
                    c.execute('DELETE FROM happyearth_together WHERE user_id = %s;', [user_info['name']])#delete the code from last time
                    c.execute('INSERT INTO happyearth_together (user_id, code) VALUES (%s, %s);', [user_info['name'], code])
                return HttpResponseRedirect('.')
            except:
                return HttpResponse("Error. Invalid POST request.")
        with connection.cursor() as c:
            c.execute('SELECT code FROM happyearth_together WHERE user_id=%s LIMIT 1;', [user_info['name']])
            code = dictfetchall(c)
        if len(code)!=1:
            return HttpResponse("You didn't start the function 'ear together' or it expires.")
        code = code[0]['code']
        with connection.cursor() as c:
            c.execute('SELECT user_id FROM happyearth_together WHERE code=%s;', [code])
            friends = dictfetchall(c)
            for f in friends:
                c.execute('SELECT name FROM happyearth_user WHERE name=%s AND city = %s AND state = %s;', [f['user_id'], user_info['city'], user_info['state']])
                if len(dictfetchall(c))!=1:
                    context = {'friends': friends, 'user_info': user_info, 'refresh': False, 'warning': 'Your friends are not in the same location with you!'}
                    return render(request, 'happyearth/user_together.html', context)
            intersect_rid = set()
            union_rid = set()
            for i, f in enumerate(friends):
                c.execute('SELECT restaurant_id FROM happyearth_recommend WHERE user_id=%s;', [f['user_id']])
                rids = dictfetchall(c)
                l = [r['restaurant_id'] for r in rids]
                if i == 0:
                    intersect_rid.update(l)
                else:
                    intersect_rid.intersection_update(l)
                union_rid.update(l)
            union_rid = list(union_rid.difference(intersect_rid))
            intersect_rid = list(intersect_rid)
            if len(intersect_rid)>0:
                c.execute('SELECT id, name, address, city, state FROM happyearth_restaurant WHERE id IN %s AND city = %s AND state = %s;', [intersect_rid, user_info['city'], user_info['state']])
                restaurants = dictfetchall(c)
            else:
                restaurants = []
            if len(union_rid)>0:
                c.execute('SELECT id, name, address, city, state FROM happyearth_restaurant WHERE id IN %s AND city = %s AND state = %s;', [union_rid, user_info['city'], user_info['state']])
                restaurants.extend(dictfetchall(c))
        context = {'friends': friends, 'user_info': user_info, 'refresh': True, 'restaurants': restaurants}
        return render(request, 'happyearth/user_together.html', context)
    else:
        return HttpResponseRedirect(reverse('login'))
    
def user_together_delete(request):
    if request.user.is_authenticated:
        username = request.user.get_username()
        with connection.cursor() as c:
            c.execute('DELETE FROM happyearth_together WHERE user_id = %s;', [username])
        return HttpResponseRedirect(reverse('homepage'))
    else:
        return HttpResponseRedirect(reverse('login'))
    
def edit_user(request):
    if request.user.is_authenticated:
        username = request.user.get_username()
        if request.method.upper() == "POST":
            try:
                city = request.POST['city']
                state = request.POST['state']
                with connection.cursor() as c:
                     c.execute('UPDATE happyearth_user SET city = %s, state = %s WHERE name = %s', [city, state, username])
                return render(request, 'happyearth/user_home.html')
            except:
                return HttpResponse("Error. Invalid POST request.")
        else:
            return render(request, 'happyearth/user_info.html')
    else:
        return HttpResponseRedirect(reverse('login'))
        
def clear_user(request):
    if request.user.is_authenticated:
        username = request.user.get_username()
        with connection.cursor() as c:
            c.execute('DELETE FROM happyearth_user WHERE name = %s', [username])
    return HttpResponseRedirect(reverse('login'))

def clear_recommend(request):
    if request.user.is_authenticated:
        username = request.user.get_username()
        with connection.cursor() as c:
            c.execute('DELETE FROM happyearth_recommend WHERE user_id = %s', [username])
    return HttpResponseRedirect(reverse('homepage'))

def user_favorites_remove(request, tag, rid):
    if request.user.is_authenticated:
        username = request.user.get_username()
        with connection.cursor() as c:
            c.execute('DELETE FROM happyearth_favorites WHERE user_id = %s AND tag = %s AND restaurant_id = %s;', [username, tag, rid])
    return HttpResponseRedirect('../..')
