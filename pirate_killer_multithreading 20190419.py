import threading
import time
from xianyu_crawler import *
from wxpy import *


def auto_add_friend(msg):
    # 自动添加好友
    time.sleep(3)
    new_friend = bot.accept_friend(msg.card)
    bot.messages.remove(msg)
    return new_friend


def send_greeting(wechat_user):
    # 欢迎消息
    time.sleep(1)
    wechat_user.send_msg('我是盗版杀手机器人，请通过回复配置你的信息')
    return 0


def confirm_key_word(wechat_user, kword_list, confirm_status, cond):
    # 确认关键词

    time.sleep(2)
    cond.acquire()

    confirm_kword_msg = '收到配置信息如下：\n\n' + '搜索关键词：\n' \
                        + ', '.join(kword_list) + '\n\n' \
                        + '确认请回复 1\n如需修改请回复 2'
    wechat_user.send_msg(confirm_kword_msg)

    confirm_status['key word'] = False

    @bot.register(chats=wechat_user)
    def get_confirm(confirm_msg):
        thread_confirm_func = bot.registered.enabled[-1].func
        cond.acquire()
        if confirm_msg.text == '1':
            confirm_status['key word'] = True
            back_msg = '关键词列表已确认，请稍后...'
        elif confirm_msg.text == '2':
            kword_list.clear()
            back_msg = '收到，即将重新开始'
        else:
            back_msg = '请回复 1 或 2'
        bot.messages.remove(confirm_msg)
        # 关闭本监听线程
        bot.registered.disable(thread_confirm_func)

        cond.notify()
        cond.release()

        return back_msg

    thread_confirm_func = bot.registered.enabled[-1].func

    # 等待接收消息与超时处理
    waiting_status = cond.wait(timeout=120)
    if not waiting_status:
        msg_end = '还未收到回复，机器人先退出了...'
        wechat_user.send_msg(msg_end)
        bot.registered.disable(thread_confirm_func)
        confirm_status['no responding'] = True

    cond.release()

    return confirm_status


def get_keyword_list(wechat_user, kword_list, confirm_status, cond):
    # 获取关键词

    time.sleep(2)
    wechat_user.send_msg('第一步：配置闲鱼搜索的关键词，从而定位盗版商品\n\n'
                         '请按格式回复你的关键词配置信息，格式如下，请把内容替换成你的内容:\n\n'
                         '搜索关键词：麻瓜编程, 自动办公, 实用主义学Python')

    cond.acquire()

    @bot.register(chats=wechat_user)
    def listen_keyword_list(msg):
        thread_kword_func = bot.registered.enabled[-1].func
        cond.acquire()
        if '搜索关键词' in msg.text:
            raw_msg = msg.text.replace('：', ':').replace('搜索关键词:', '').replace('，', ',').split(',')
            kword_list.clear()
            for iMsg in raw_msg:
                kword_list.append(iMsg.strip())
        else:
            warning_msg = '请根据提示按格式回复你的关键词配置信息 \n' \
                          '即将重新开始...'
            wechat_user.send_msg(warning_msg)
            kword_list.clear()

        bot.messages.remove(msg)
        # 关闭本监听线程
        bot.registered.disable(thread_kword_func)

        cond.notify()
        cond.release()

        return None

    thread_kword_func = bot.registered.enabled[-1].func

    # 等待接收消息与超时处理
    waiting_status = cond.wait(timeout=120)
    if not waiting_status:
        msg_end = '还未收到回复，机器人先退出了...'
        wechat_user.send_msg(msg_end)
        bot.registered.disable(thread_kword_func)
        confirm_status['no responding'] = True

    cond.release()

    return kword_list


def pirate_killer(wechat_user):
    # 盗版杀手机器人主函数

    keyword_list = []
    confirmation = {'key word': False, 'no responding': False}
    cond = threading.Condition()

    send_greeting(wechat_user)
    while not confirmation['key word']:
        # 获取关键词
        if len(keyword_list) == 0:
            thread_kword = threading.Thread(target=get_keyword_list, args=(wechat_user, keyword_list, confirmation, cond,))
            thread_kword.start()
            thread_kword.join()
        # 确认关键词
        if len(keyword_list) > 0:
            thread_confirm = threading.Thread(target=confirm_key_word,
                                              args=(wechat_user, keyword_list, confirmation, cond,))
            thread_confirm.start()
            thread_confirm.join()
        # 超时退出
        if confirmation['no responding']:
            break

    # 闲鱼搜索
    if not confirmation['no responding']:
        count = 0
        for iKword in keyword_list:
            count += 1
            # 闲鱼搜索
            attention_list = do_xianyu(xianyu_word=iKword)
            # 本来应该用关键词来命名，但因为wxpy发送中文文件名有问题，所以用了数字命名
            data_path = f'./xianyu_{count}.txt'
            save_xianyu_info(data_list=attention_list, filepath_write=data_path)
            wechat_user.send_msg('发现如下的商品，请看一下哦 \n' \
                                 'csv 文件在windows下可能乱码 所以写成了txt...')
            send_wechat_notice(wechat_user=wechat_user, filepath_send=data_path)

    return 0


if __name__ == '__main__':

    bot = Bot(cache_path=True)

    # 自动处理新好友请求
    @bot.register(msg_types=FRIENDS)
    def auto_add_friends(msg):
        if "盗版杀手" in msg.text:
            killer_user = bot.accept_friend(msg.card)
            killer_user.send_msg('您好！请回复 “盗版杀手” 以开始使用！')

    # 监听含有 "盗版杀手" 关键词的消息
    @bot.register(chats=User)
    def listen_start_killer(msg):
        time.sleep(2)
        if "盗版杀手" in msg.text:
            killer_user = msg.sender
            bot.messages.remove(msg)
            pirate_killer(killer_user)

    embed()










