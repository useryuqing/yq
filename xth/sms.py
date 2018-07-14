# #-*- coding:utf-8 -*-
# import http.client
# import urllib
#
# host  = "106.ihuyi.com"
# sms_send_uri = "/webservice/sms.php?method=Submit"
#
# account  = "C66204495"
# password = "f4bcaf08bcd2d18b8325763abf61935c"
#
# def send_sms(text, mobile):
#     params = urllib.parse.urlencode({'account': account, 'password' : password, 'content': text, 'mobile':mobile,'format':'json' })
#     headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
#     conn = http.client.HTTPConnection(host, port=80, timeout=30)
#     conn.request("POST", sms_send_uri, params, headers)
#     response = conn.getresponse()
#     response_str = response.read()
#     conn.close()
#     return response_str
#
# if __name__ == '__main__':
#
#     mobile = "18439585828"
#     text = "您的验证码是：121254。请不要把验证码泄露给其他人。"
#
#     print(send_sms(text, mobile))

# 请求地址
url = 'https://api.miaodiyun.com/20150822/industrySMS/sendSMS'
# 请求头
headers = {'Content-type':'application/x-www-form-urlencoded'}
# 账户ID
accountSid = 'b9b3b69397d44bdab2d934b1fca8c8d8'
auth_token = 'eef9b4b9786f4443bc794637195bd923'



def send_sms(yzm,to):
    # 时间戳
    import time
    timestamp = time.strftime('%Y%m%d%H%M%S')
    sig = accountSid + auth_token + timestamp


    # md5加密
    import hashlib
    md = hashlib.md5()
    md.update(sig.encode('utf_8'))
    sig = md.hexdigest()

    # 短信模版参数
    yzm = yzm
    t = '5'
    param = yzm + ',' + t
    # 表单数据
    form_shu = {
    'accountSid':accountSid,
    'templateid':'194555171',
    'to':to,
    'timestamp': timestamp,
    'sig':sig,
    'param':param,
    }
    # 将字典转化为url参数
    from urllib.parse import urlencode
    form_shu = urlencode(form_shu)
    # 创建浏览对象
    import http.client
    connect = http.client.HTTPConnection('api.miaodiyun.com')
    # 发送post请求
    connect.request(method= 'POST',url= url,body= form_shu,headers= headers)
    resp = connect.getresponse()
    # 打印响应
    print(resp.read().decode('utf_8'))



