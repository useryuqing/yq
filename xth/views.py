from django.shortcuts import render, redirect

from xth.models import SlideShow, MainDescription, Product, CategorieGroup, ChildGroup, User,Address,Cart,Order
import random
from xth.sms import send_sms
from django.http import JsonResponse
import uuid

# Create your views here.
def home(request):
    #获取轮播图数据
    slideList = SlideShow.objects.all()
    #获取5大模块数据
    mainList = MainDescription.objects.all()
    for item in mainList:
        products = Product.objects.filter(categoryId=item.categoryId)
        item.product1 = products.get(productId=item.product1)
        item.product2 = products.get(productId=item.product2)
        item.product3 = products.get(productId=item.product3)
    return render(request, "home/home.html", {"slideList":slideList, "mainList":mainList})
def market(request, gid, cid, sid):
    #左侧分组数据
    leftCategorieList = CategorieGroup.objects.all()

    #获取分组商品的信息
    products = Product.objects.filter(categoryId=gid)
    #获取子类数据
    if cid != "0":
        products = products.filter(childId=cid)
    #排序
    if sid == "1":
        # products = products.order_by()
        pass
    elif sid == "2":
        products = products.order_by("price")
    elif sid == "3":
        products = products.order_by("-price")

    #获取子组信息
    childs = ChildGroup.objects.filter(categorie__categorieId=gid)

    return render(request, "market/market.html", {"leftCategorieList":leftCategorieList, "products":products, "childs":childs, "gid":gid, "cid":cid})

def details(request,rid):
    overimg = Product.objects.get(pk=rid)
    return render(request,"details/details.html",{"overimg":overimg})


def cart(request):
    # 判断是否登录
    tokenValue = request.COOKIES.get("token")
    if not tokenValue:
        # 说明没登录
        return redirect("/login/")
    try:
        user = User.objects.get(tokenValue=tokenValue)
    except User.DoesNotExist as e:
        return redirect("/login/")
    carts = Cart.objects.filter(user__tokenValue=tokenValue)
    return render(request, "cart/cart.html", {"carts": carts})

def qOrder(request):
    # 判断是否登录
    tokenValue = request.COOKIES.get("token")
    #找到当前可用的订单,当前登录用户的默认flag为0的变为可用
    order = Order.orders2.filter(user__tokenValue=tokenValue).get(flag=0)
    order.flag = 1
    order.save()

    #属于该订单的购物车选中数据的isOrder置为Flase,先拿出全部的订单然后过滤当前的订单，在过滤选中的订单，在模型中已经过滤掉了isOrder等于False的，所以要把加入购物车的商品变为不显示
    carts = Cart.objects.filter(user__tokenValue=tokenValue).filter(order=order).filter(isCheck=True)
    for cart in carts:
        cart.isOrder = False
        cart.save()

    #将没有被选中的数据添加到新的订单中，创建新的订单
    newOrder = Order.create(str(uuid.uuid4()),User.objects.get(tokenValue=tokenValue),Address.objects.get(pk=1),0)
    newOrder.save()
    #把没选中的放入新的订单中
    oldCarts =  Cart.objects.filter(user__tokenValue=tokenValue)
    for cart in oldCarts:
        cart.order = newOrder
        cart.save()
    return JsonResponse({"error":0})

def changecart2(request):
    #获取请求的那个商品
    cartid = request.POST.get("cartid")
    #找到那个商品
    cart = Cart.objects.get(pk=cartid)
    # 改变isCheck
    cart.isCheck = not cart.isCheck
    cart.save()
    return JsonResponse({"error":0,"flag":cart.isCheck})

def changecart(request,flag):
    #如果flag等于1，就是减法，否则就是加法
    num = 1
    if flag == "1":
        num = -1

    #判断是否登录
    tokenValue = request.COOKIES.get("token")
    if not tokenValue:
        return JsonResponse({"error":1})
    #在判断用户的token是否存在
    try:
        user = User.objects.get(tokenValue=tokenValue)
    except User.DoesNotExist as e:
        return JsonResponse({"error":2})

    pid = request.POST.get("pid")
    #大组的id可能是重的，找到商品id
    product = Product.objects.get(pk=pid)

    try:
        # 看下购物车里有没有这条数据,防止重复
        cart = Cart.objects.get(product__id=pid)

        #判断库存,如果加法就判断
        if flag == "2":
            if product.storeNums == "0":
                return JsonResponse({"error":0,"num":cart.num})
        #买过该商品，会得到该数据加一
        cart.num = cart.num + num
        #加减都会执行
        product.storeNums = str(int(product.storeNums) - num)
        product.save()
        #如果减到0就从数据库购物车里删掉
        if cart.num == 0:
            cart.delete()
        else:
            #无论加和减都要改变库存
            cart.save()

    except Cart.DoesNotExist as e:
        #如果是减号就什么都不做
        if flag == "1":
            return JsonResponse({"error":0,"num":0})

        #因为是主键关联的，所以刚注册的用户没有订单就不能加入购物车，所以创个假订单，创建一个flag为0，isdelete为False的,所有订单中只有一个订单为0
        #找到用户所有订单
        try:
            #找到了订单
            order = Order.orders2.filter(user__tokenValue=tokenValue).get(flag=0)
        except Order.DoesNotExist as e:
            #没找到订单，生成一个随机订单号,生成一个假订单
            orderId = str(uuid.uuid4())
            #找到用户地址
            address = Address.objects.get(pk=1)
            order = Order.create(orderId,user,address,0)
            order.save()
        #没有购买过该商品，创建该条购物车数据
        cart = Cart.create(user,product,order,1)
        cart.save()
        product.storeNums = str(int(product.storeNums) - num)
        product.save()
    #告诉客户端添加成功
    return JsonResponse({"error":0,"num":cart.num})


def mine(request):
    phone = request.session.get("phoneNum", default="未登录")
    return render(request, "mine/mine.html", {"phone":phone})

from django.contrib.auth import logout
def quit(request):
    logout(request)
    return redirect("/mine/")

def login(request):
    if request.method == "GET":
        if request.is_ajax():
            # 生产验证码
            strNum = '1234567890'
            # 随机选取4个值作为验证码
            rand_str = ''
            for i in range(0, 6):
                rand_str += strNum[random.randrange(0, len(strNum))]
            msg = "您的验证码是：%s。请不要把验证码泄露给其他人。"%rand_str
            phone = request.GET.get("phoneNum")
            send_sms(msg, phone)
            #存入session
            request.session["code"] = rand_str
            response = JsonResponse({"data":"ok"})
            return response
        else:
            return render(request, "mine/login.html")
    else:
        phone  = request.POST.get("username")
        passwd = request.POST.get("passwd")
        code   = request.session.get("code")

        if passwd == code:
            #验证码验证成功
            #判断用户是否存在
            uuidStr = str(uuid.uuid4())
            try:
                user = User.objects.get(pk=phone)
                user.tokenValue = uuidStr
                user.save()
            except User.DoesNotExist as e:
                #注册
                user = User.create(phone,None,uuidStr,"sunck good")
                user.save()
            request.session["phoneNum"] = phone
            response = redirect("/mine/")
            #将tokenValue写入cookie,cookie存储的是字典，上面要用键去判断用户是否登录，所以要存入字典
            response.set_cookie("token",uuidStr)
            return response
        else:
            # 验证码验证失败
            return redirect("/login/")

def Shipping(request):
    #获取地址信息
    addresses = Address.objects.filter(user__phoneNum=request.session.get("phoneNum"))
    return render(request,"Shipping/Shipping.html",{"addresses":addresses})


def addsite(request):
    if request.method == "GET":
        return render(request,"addsite/addsite.html")
    else:
        name = request.POST.get("name")
        telphone = request.POST.get("telphone")
        sex = request.POST.get("sex")

        if sex == "0":
            sex = False
        sex = True
        control1 = request.POST.get("control1")
        control2 = request.POST.get("control2")
        control3 = request.POST.get("control3")
        control4 = request.POST.get("control4")
        control5 = request.POST.get("control5")
        email = request.POST.get("email")

        #找到收货地址
        allAddress = control1 + control2 + control3 + control4 + control5
        #拿到用户的账号
        phone = request.session.get("phoneNum")
        user = User.objects.get(pk=phone)
        address = Address.create(name,sex,telphone,control1,control2,allAddress,control3,control4,control5,email,user)
        address.save()
        return redirect("/Shipping/")



from axf.models import Product,MainDescription,SlideShow
from axf.serializers import ProductSerializer
from rest_framework import mixins
from rest_framework import generics