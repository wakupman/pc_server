# -*- coding: utf-8 -*-
import os
import logging
import time
import telegram
import threading
import mysql.connector
from datetime import datetime
from datetime import time as time2
import pytz
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
from mysql.connector import Error
from dateutil.relativedelta import relativedelta



from telegram import __version__ as TG_VER
try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"这戈程序不适应当前的TG版本{TG_VER}. 查看"
        f"{TG_VER} 此程序的版本, "
        f"访问 https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html"
    )
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update,Bot,constants,InputMediaPhoto
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters, 
    
)

dbconfig = {
    'host': 'localhost',
    'database': 'pc_db',
    'user': 'root',
    'password': '!123456xyZ'
}
pool = mysql.connector.pooling.MySQLConnectionPool(pool_name='mypool', pool_size=3, **dbconfig)


'''
CREATE TABLE person (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  NAME VARCHAR(100),
  logo_url VARCHAR(100),
  channel_id BIGINT, 
  c_message_id BIGINT,
  vote_count BIGINT,
  create_date DATE
  
);

CREATE INDEX name_idx ON person(NAME)
CREATE INDEX channel_idx ON person(channel_id);
CREATE INDEX c_message_idx ON person(c_message_id);


CREATE TABLE channel_group_rel (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  channel_id BIGINT, 
  c_message_id BIGINT,
  group_id BIGINT,
  g_message_id BIGINT
  
  
);

CREATE INDEX channel_id_idx ON channel_group_rel(channel_id); 
CREATE INDEX c_message_id_idx ON channel_group_rel(c_message_id); 
CREATE INDEX group_id_idx ON channel_group_rel(group_id); 
CREATE INDEX g_message_id_idx ON channel_group_rel(g_message_id); 



CREATE TABLE post_new_msg(
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  person_id BIGINT,
  group_id BIGINT,
  new_g_message_id BIGINT
);


CREATE INDEX person_id_idx ON post_new_msg(person_id);
CREATE INDEX group_id_idx ON post_new_msg(group_id);


CREATE TABLE user_post_new_msg(
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT,
  person_id BIGINT,
  group_id BIGINT,
  u_new_g_message_id BIGINT

);

CREATE INDEX user_id_idx ON user_post_new_msg(user_id);
CREATE INDEX person_id_idx ON user_post_new_msg(person_id);
CREATE INDEX group_id_idx ON user_post_new_msg(group_id);


ALTER TABLE user_post_new_msg drop PRIMARY KEY;

ALTER TABLE user_post_new_msg ADD PRIMARY KEY (user_id,g_message_id);

'''


# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


(STARTING,START_OVER,SELECTING,  ADDING,
PROMOTING,DELETEING, NAME_INPUT,INPUT_DESC,
LOGO_IMG,DESC_IMG,GET_CHANNEL_MSG,BIO,END,
DEL_INPUT_SELECT,DEL_CONFIRM,DEL_CONFIRM_DONE,V14,V15,
PROMO_INPUT_SELECT,PROMO_CONFIRM,PROMO_MONTH,PROMO_POWER,V20,
TEXT_WITH_BUTTON_DESC,BUTTON_TEXT,BUTTON_URL,V24,V25,
) = map(chr, range(0, 28)) #生成一些状态码,为什么不直接用int,因为会引发一些冲突

BOT_TOKEN="6013452846:AAGCQpPjij-rHL1K1obhcaRTRbQDbFb_rEM"
CHANNEL_ID=-1001382928142
GROUP_ID=-1001865849787
ADMIN_ID=[1280532381,5748943638]
AES_KEY = b'823yhw8hw9u3j387'  # 16字节的密钥
AES_iv =  b'2379s8je8wjow93j'  # 16字节的初始化向量

channel_post_temp_store=set()


# 获取 MySQL 连接
def get_connection():
    try:
        conn = pool.get_connection()
        return conn
    except Error as e:
        print(e)
        return None



# 加密函数
def aes_encrypt(key, iv, data):
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_data = cipher.encrypt(pad(data.encode(), AES.block_size))
    encrypted_text= base64.b64encode(encrypted_data).decode()
    encoded_text = base64.urlsafe_b64encode(encrypted_text.encode()).decode()
    return encoded_text

# 解密函数
def aes_decrypt(key, iv, data):
    data = base64.urlsafe_b64decode(data.encode()).decode()
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = cipher.decrypt(base64.b64decode(data))
    return unpad(decrypted_data, AES.block_size).decode()


#实现一个CountDownLatch
class CountDownLatch:
    def __init__(self, count):
        self.count = count
        self.event = threading.Event()

    def count_down(self):
        self.count -= 1
        if self.count == 0:
            self.event.set()

    def wait(self, timeout=None):
        print('开始等待')
        self.event.wait(timeout)
        print('等待结束')


 # Top level conversation callbacks
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """进来时直接展示那一堆按键."""

    user = update.message.from_user
    logger.info(user)
    if user.id not in ADMIN_ID:
        await update.message.reply_text(text='非法操作')
        return ConversationHandler.END


    logger.info("Start of %s:", user.first_name)
    text = (
        
        "你好,我是新建资料机器人,请选择功能\n"
        "你也可以输入 /cancel 退出\n"

    )
    buttons = [
        [
            InlineKeyboardButton(text="增加人物", callback_data=str(ADDING)),
        ],
        [
            InlineKeyboardButton(text="删除资料", callback_data=str(DELETEING)),
        ],
         [
            InlineKeyboardButton(text="设置推广", callback_data=str(PROMOTING)),
        ],
        [
            InlineKeyboardButton(text="发送带链接按键推文", callback_data=str(TEXT_WITH_BUTTON_DESC)),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(text=text, reply_markup=keyboard,parse_mode=telegram.constants.ParseMode.HTML)

    return SELECTING



#输入新建名称：为什么这里要单独列出来,因为之前的回调是不穿massage过来的,而是从回调传过来
async def input_name_desc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    #这个anser好像只要之前用了回调这里就要应答一下
    #请注意这个回调是不带用户信息的,如果在这里调用 user = update.message.from_user 会得到空值
    query = update.callback_query
    await query.answer()
    # text = (
    #     "OK,请继续"    
    # )
    await   update.callback_query.delete_message()
    #local_store['pre_chat_id'] =this_msg.chat_id
    #local_store['pre_massage_id'] =this_msg.message_id
    #清空之前的数据
    context.user_data.clear()
     
    text = (
        "请输入新建的名字\n"
        "你也可以输入 /cancel 退出"
    )
    #await update.message.reply_text(text=text) # 这样写是不行的,因为是在回调中,并不是顺序的消息发送中
    #或者用context.bot来发信息,不过这样发信息需要指定chatid和msgid
    await update.callback_query.message.reply_text(text=text)
    

    return INPUT_DESC


#输入新建名称
async def input_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    text = (
        "好的,名字是" + update.message.text + ",接下来, 请上传头像相片\n"
                                      "你也可以输入 /cancel 退出"
    )
    context.user_data['name']=update.message.text
    # await  context.bot.edit_message_text(
    #     chat_id= local_store['pre_chat_id'],
    #     message_id= local_store['pre_massage_id'],
    #     text=text)
    await update.message.reply_text(text=text)
    return LOGO_IMG

 


#选头像
async def choose_logo_img(update, context):
    #在不是回调时才能用update.message
    user = update.message.from_user
    #这里是下载最后一张图片当成头像
    await update.message.reply_text('请稍等,正将图片上传到telegraph')
    logo = await update.message.photo[-1].get_file() #update.message.photo[0]是像素最小那张
    logo_byte =await logo.download_as_bytearray()
    try:
        logo_url=upload_to_telegraph(logo_byte)

        await update.message.reply_text('好的! 已收到{}提交的头像,链接是{}\n'.format(user.first_name,logo_url)+
                                '接下来请提交一定数量的图片\n'
                                '也可输入 /cancel 退出,或者 /skip 跳过')
        context.user_data['logo_url']=logo_url
    except Exception :
        context.user_data['logo_url']=None
        logger.exception(Exception)
    context.user_data['photos']=[]
    return DESC_IMG

#跳过选头像
async def skip_logo_img(update, context):    
    await update.message.reply_text(
        '已跳过提交头像图片\n'
        '接下来请提交一定数量的图片\n'
        '也可输入 /cancel 退出,或者 /skip 跳过'
        )
    context.user_data['photos']=[]
    return DESC_IMG


#选介绍图像
async def choose_desc_img(update, context):

    user = update.message.from_user
    photo = update.message.photo[-1]
    context.user_data['photos'].append(photo)
  
    await update.message.reply_text('好的! 已收到{}提交的图像\n'.format(user.first_name)+
                              ',接下来请提交文字简介\n'
                              '也可输入 /cancel 退出,或者 /skip 跳过')

    return BIO



#跳过选介绍图像
async def skip_desc_img(update, context):
   
    await update.message.reply_text(
        
        '已跳过选择介绍图片\n'
        '接下来请提交文字简介\n'
        '也可输入 /cancel 退出,或者 /skip 跳过'
        
        )

    return BIO


 
#输入简介
async def bio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info(" %s create name of : %s", user.first_name, update.message.text)
    context.user_data['text']=update.message.text

    #这里要做一个回单 
    # 创建一个InlineKeyboardMarkup对象，包含两个按钮
    # keyboard = [[InlineKeyboardButton("按钮1", callback_data='button1'),
    #              InlineKeyboardButton("按钮2", callback_data='button2')]]
    # reply_markup = InlineKeyboardMarkup(keyboard)

    text="<b>"+context.user_data['name']+'</b>\n\n'+context.user_data['text']

    msg=await post_in_channel(context.user_data['photos'],text,context.bot)
    context.user_data['channel_id']=msg.chat_id
    context.user_data['c_message_id']=msg.message_id
     #为什么要这一部，因为每次进入流程都清了context.user_data,所以构建了一个全局的set来缓存一下postid
    channel_post_temp_store.add(msg.message_id)
    try:
        save_db_new_person(update , context )
    except:
        await update.message.reply_text(text='数据库落盘错误') 
        return  ConversationHandler.END
    text = (
        "OK,你可以输入 /start 继续选择你要做的事情\n"
    )
    await update.message.reply_text(text=text) 
    #context.user_data.clear()
    return  ConversationHandler.END



#跳过输入简介
async def skip_bio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = (
        "跳过输入介绍\n"
    )
    await update.message.reply_text(text=text)


    text="<b>"+context.user_data['name']+'</b>\n\n'+context.user_data['text']

    msg=await post_in_channel(context.user_data['photos'],text,context.bot)
    #为什么要编辑？因为在匿名评测那里要加上之前信息的id
    context.user_data['channel_id']=msg.chat_id
    context.user_data['c_message_id']=msg.message_id
    #为什么要这一部，因为每次进入流程都清了context.user_data,所以构建了一个全局的set来缓存一下postid
    channel_post_temp_store.add(msg.message_id)

    try:
        save_db_new_person(update , context )
    except:
        await update.message.reply_text(text='数据库落盘错误') 
        return  ConversationHandler.END
    
    text = (
        "OK,你可以输入 /start 继续选择你要做的事情\n"
    )
    await update.message.reply_text(text=text) 
    #context.user_data.clear()
    return  ConversationHandler.END
 

def save_db_new_person(update: Update, context: ContextTypes.DEFAULT_TYPE):          
    # 定义一个查询，如果有数据则更新，否则插入
    query = ("SELECT COUNT(*) FROM person WHERE name = %s")
    update_query = ('''
 UPDATE person SET logo_url=%s,channel_id=%s,c_message_id=%s,vote_count=%s,create_date=%s WHERE name = %s   
    ''')
    insert_query = ('''
INSERT INTO person (name,logo_url,channel_id,c_message_id,vote_count,create_date)
VALUES (%s, %s,%s,%s,%s,%s)   
    ''')
    # 执行查询
    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(query, (context.user_data['name'],))
        count = cursor.fetchone()[0]
  
        if count > 0:
            # 如果有数据，执行更新操作
            cursor.execute(update_query, (
            context.user_data['logo_url'],
            context.user_data['channel_id'],
            context.user_data['c_message_id'],
            0,datetime.now(),
            context.user_data['name']
            ))
           # print(cursor.rowcount, "行受影响，数据已更新")
        else:
            # 如果没有数据，执行插入操作
            cursor.execute(insert_query, (
            context.user_data['name'],
            context.user_data['logo_url'],
            context.user_data['channel_id'],
            context.user_data['c_message_id'],
            0,datetime.now()   
            ))

        conn.commit()
 
    except Error as e:
        print(e)      
    finally:
        if conn:
            conn.close() 


#获取转发到群组的消息
async def getForwardMsg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
         
        #这里的context是一个群聊的上下文，和私聊机器人的context是不一样的，所以这里的user_data是空的
       
        message = update.message
        #logger.info('update.message=',update.message)
        # 如果消息是由频道转发的
        if message and message.forward_from_chat:
            # 获取频道或群组的ID
            from_chat_id = message.forward_from_chat.id
            from_msg_id=message.forward_from_message_id
            #if from_chat_id ==CHANNEL_ID :
            #    await message.unpin() #不置顶所有频道转发的消息
            # 转发的msgid要在缓存的channel_post_temp_store中
            #print ('from_msg_id=',from_msg_id)
            #print ('channel_post_temp_store=',channel_post_temp_store)
            if from_chat_id ==CHANNEL_ID and message.caption is not None and from_msg_id in channel_post_temp_store:             
                save_db_chat_group_rel(
                    from_chat_id,
                    message.forward_from_message_id,
                    message.chat_id,
                    message.message_id )
                #await message.reply_text(text="占座")
                #为什么要编辑？因为在匿名评测那里要加上之前信息的id

                report_args= 'report_'+str(message.forward_from_message_id)+'_' +str(message.message_id)
                report_args= aes_encrypt(AES_KEY, AES_iv, report_args) 

                meme_args= 'meme_'+str(message.forward_from_message_id)+'_' +str(message.message_id)
                meme_args= aes_encrypt(AES_KEY, AES_iv, meme_args) 

                pin_msg=await context.bot.edit_message_caption(
                    chat_id=from_chat_id,
                    message_id=message.forward_from_message_id ,
                    caption=message.caption+(
        '\n\n📙收藏目录 t.me/pcratebot/pcl'+            
        '\n\n ǀ ʜᴀᴠᴇ ᴀ ɴɪᴄᴇ ᴅᴀʏ'+
        '\n\n<b><a href="https://t.me/pc_reporter_bot?start='+report_args+'">✏️ 写体验报告</a></b>'+
        ' | '+
        '<b><a href="https://t.me/not_kown_bot?start='+meme_args+'">🙈 写匿名问答</a></b>\n'+
        '\n'),parse_mode=telegram.constants.ParseMode.HTML)
                #把缓存的postid去掉
                channel_post_temp_store.remove(from_msg_id)
                #await updateNewMsgForce(message)

#获取新的帖子评论
async def getNewMsg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    #print(update.message)     
    await updateNewMsgByThreadId(update.message)


#更新一个帖子的最大msgid                           
async def updateNewMsgByThreadId(massage):
     
    #print(massage)
    #print(massage.message_thread_id)
    #message_thread_id不为空
    if massage.message_thread_id:
        query = ("SELECT COUNT(*) FROM post_new_msg WHERE  group_id= %s and g_message_id = %s")
        update_query = ('''
    UPDATE post_new_msg SET new_g_message_id=%s  WHERE  group_id= %s and g_message_id = %s   
        ''')
        insert_query = ('''
    INSERT INTO post_new_msg (group_id,g_message_id,new_g_message_id )
    VALUES (%s, %s,%s)   
        ''')
        # 执行查询
        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (GROUP_ID,massage.message_thread_id))
            count = cursor.fetchone()[0]
            #print("count",count)    
            if count > 0:
                # 如果有数据，执行更新操作
                cursor.execute(update_query, (
                 massage.id,GROUP_ID,massage.message_thread_id            
                ))
            # print(cursor.rowcount, "行受影响，数据已更新")
            else:
                # 如果没有数据，执行插入操作
                cursor.execute(insert_query, (
                 GROUP_ID,massage.message_thread_id, massage.id
                ))

            conn.commit()
    
        except Error as e:
            print(e)      
        finally:
            if conn:
                conn.close() 


#更新一个帖子的最大msgid ,适用于第一帖   ,但是如果没一贴都加，就会让新用户看见所有帖子都显示蓝点    
#新帖子不用加蓝点 2023-05-20             
async def updateNewMsgForce(massage):
     
    #print(massage)
    #print(massage.message_thread_id)
    #message_thread_id不为空
 
        insert_query = ('''
    INSERT INTO post_new_msg (group_id,g_message_id,new_g_message_id )
    VALUES (%s, %s,%s)   
        ''')
        # 执行查询
        conn = None

        try:
            conn = get_connection()
            cursor = conn.cursor()
           
            cursor.execute(insert_query, (
                GROUP_ID, massage.id, massage.id
            ))

            conn.commit()
    
        except Error as e:
            print(e)      
        finally:
            if conn:
                conn.close() 



def save_db_chat_group_rel(channel_id,c_message_id,group_id,g_message_id ):          
    # 定义一个查询，如果有数据则更新，否则插入
    
    insert_query = ('''
INSERT INTO channel_group_rel ( channel_id,c_message_id,group_id,g_message_id)
VALUES (%s, %s,%s,%s)   
    ''')

    conn = None

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(insert_query, (
            channel_id,
            c_message_id,
            group_id,
            g_message_id
            ))
        
        conn.commit()

    except Error as e:
        print(e)      
    finally:
        if conn:
            conn.close()     
 

def upload_to_telegraph(file_byte):
    """
    上传文件到Telegraph,并返回上传后的链接
    """
    url = 'https://telegra.ph/upload'
    files = {'file': ('file', file_byte)}
    response = requests.post(url, files=files)
    response_json = response.json()
    if response_json[0]:
        return response_json[0]['src']
    else:
        raise Exception('Failed to upload file')
    
 
async def post_in_channel(photos,text,bot):
    # 在指定的频道中发帖，并带上按钮
    #logger.info(photos)
    media = []
    for file in photos:
        media.append(InputMediaPhoto(media=file))
    msgs=await bot.send_media_group(chat_id=CHANNEL_ID, media=media, caption=text,parse_mode=telegram.constants.ParseMode.HTML)  
    for msg in msgs:
      #返回包含文字信息的那条信息
      #logger.info(msg)
      return msg
 #-------------------删除------------------------


 

#输入新建名称：为什么这里要单独列出来,因为之前的回调是不穿massage过来的,而是从回调传过来
async def delete_desc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    #这个anser好像只要之前用了回调这里就要应答一下
    #请注意这个回调是不带用户信息的,如果在这里调用 user = update.message.from_user 会得到空值
    query = update.callback_query
    await query.answer()
    # text = (
    #     "OK,请继续"    
    # )
    await   update.callback_query.delete_message()
    #local_store['pre_chat_id'] =this_msg.chat_id
    #local_store['pre_massage_id'] =this_msg.message_id
    #清空之前的数据
    context.user_data.clear()
    context.user_data['del_list']={}
    text = (
        "请输入姓名的关键字查找\n"
        "你也可以输入 /cancel 退出"
    )
    #await update.message.reply_text(text=text) # 这样写是不行的,因为是在回调中,并不是顺序的消息发送中
    #或者用context.bot来发信息,不过这样发信息需要指定chatid和msgid
    await update.callback_query.message.reply_text(text=text)
    

    return DEL_INPUT_SELECT
    


 # Top level conversation callbacks
async def del_select(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """进来时直接展示那一堆按键."""
 
    text = (
        "以下是根据关键字查找到的前5个名字,请选择一个来删除\n"
        "你也可以输入 /cancel 退出\n"
    )

    input_text=update.message.text
    buttons = []
    
    insert_query = ('''
    select id,name from person where name like %s limit 5  
    ''')

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(insert_query, ('%'+input_text+'%',))
        for row in cursor:
           context.user_data['del_list'][str(row[0])]=row[1]
           buttons.append(
                [ InlineKeyboardButton(text=row[1], callback_data=row[0]) ]
           )

    except Error as e:
        print(e)      
    finally:
        if conn:
            conn.close()     
    
    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(text=text, reply_markup=keyboard,parse_mode=telegram.constants.ParseMode.HTML)

    return DEL_CONFIRM



async def del_comfirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    #这个anser好像只要之前用了回调这里就要应答一下
    #请注意这个回调是不带用户信息的,如果在这里调用 user = update.message.from_user 会得到空值
    query = update.callback_query
    await query.answer()
    # text = (
    #     "OK,请继续"    
    # )
    id= update.callback_query.data
    name=context.user_data['del_list'][str(id)]

    await   update.callback_query.delete_message()
    #local_store['pre_chat_id'] =this_msg.chat_id
    #local_store['pre_massage_id'] =this_msg.message_id
    #清空之前的数据
      
    text = (
        "您确定删除 "+name+" 吗?\n"
        "你也可以输入 /cancel 退出"
    )

    buttons= [ 
              [InlineKeyboardButton(text='确定', callback_data=id) ,
              InlineKeyboardButton(text='取消', callback_data=-1) ,
              ]
              ]
   
    keyboard = InlineKeyboardMarkup(buttons)
    await query.message.reply_text(text=text, reply_markup=keyboard,parse_mode=telegram.constants.ParseMode.HTML)


    return DEL_CONFIRM_DONE
    



async def del_comfirm_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    #这个anser好像只要之前用了回调这里就要应答一下
    #请注意这个回调是不带用户信息的,如果在这里调用 user = update.message.from_user 会得到空值
    query = update.callback_query
    await query.answer()
    # text = (
    #     "OK,请继续"    
    # )
    id= update.callback_query.data
    name=context.user_data['del_list'][str(id)]

    await   update.callback_query.delete_message()
    
    insert_query = ('''
    delete from person where id = %s
    ''')

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(insert_query, (id,))
        conn.commit()

    except Error as e:
        print(e)      
    finally:
        if conn:
            conn.close()  
      
    text = (
        "已删除 "+name+" 的资料\n"
        "你也可以输入 /start 继续选择其他功能"
    )

    
    await query.message.reply_text(text=text, parse_mode=telegram.constants.ParseMode.HTML)


    return ConversationHandler.END
        
#-----------------------推广--------------------------------------------



async def promote_desc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    #这个anser好像只要之前用了回调这里就要应答一下
    #请注意这个回调是不带用户信息的,如果在这里调用 user = update.message.from_user 会得到空值
    query = update.callback_query
    await query.answer()
    # text = (
    #     "OK,请继续"    
    # )
    await   update.callback_query.delete_message()
    #local_store['pre_chat_id'] =this_msg.chat_id
    #local_store['pre_massage_id'] =this_msg.message_id
    #清空之前的数据
    context.user_data.clear()
    context.user_data['promote_list']={}
    text = (
        "请输入关键字查找需要置顶的名字\n"
        "你也可以输入 /cancel 退出"
    )
    #await update.message.reply_text(text=text) # 这样写是不行的,因为是在回调中,并不是顺序的消息发送中
    #或者用context.bot来发信息,不过这样发信息需要指定chatid和msgid
    await update.callback_query.message.reply_text(text=text)
    

    return PROMO_INPUT_SELECT




 # Top level conversation callbacks
async def promote_select(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """进来时直接展示那一堆按键."""
 
    text = (
        "以下是根据关键字查找到的前5个名字,请选择一个来推广\n"
        "你也可以输入 /cancel 退出\n"
    )

    input_text=update.message.text
    buttons = []
    
    insert_query = ('''
    select id,name from person where name like %s limit 5  
    ''')

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(insert_query, ('%'+input_text+'%',))
        for row in cursor:
           context.user_data['promote_list'][str(row[0])]=row[1]
           buttons.append(
                [ InlineKeyboardButton(text=row[1], callback_data=row[0]) ]
           )

    except Error as e:
        print(e)      
    finally:
        if conn:
            conn.close()     
    
    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(text=text, reply_markup=keyboard,parse_mode=telegram.constants.ParseMode.HTML)

    return PROMO_MONTH




async def pro_comfirm_month(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    #这个anser好像只要之前用了回调这里就要应答一下
    #请注意这个回调是不带用户信息的,如果在这里调用 user = update.message.from_user 会得到空值
    query = update.callback_query
    await query.answer()
    # text = (
    #     "OK,请继续"    
    # )
    id= update.callback_query.data
    name=context.user_data['promote_list'][str(id)]
    context.user_data['promote_id']=id
    context.user_data['promote_name']=name

    await   update.callback_query.delete_message()
    #local_store['pre_chat_id'] =this_msg.chat_id
    #local_store['pre_massage_id'] =this_msg.message_id
    #清空之前的数据
      
    text = (
        "您要为 "+name+" 推广几个月?\n"
        "你也可以输入 /cancel 退出"
    )

    buttons= [ 
              [InlineKeyboardButton(text='1', callback_data=1) ,
              InlineKeyboardButton(text='2', callback_data=2) ,
                InlineKeyboardButton(text='3', callback_data=3) ,
                  InlineKeyboardButton(text='4', callback_data=4 )
              ],
               [InlineKeyboardButton(text='5', callback_data=5) ,
              InlineKeyboardButton(text='6', callback_data=6) ,
                InlineKeyboardButton(text='7', callback_data=7) ,
                  InlineKeyboardButton(text='8', callback_data=8 )
              ],
               [InlineKeyboardButton(text='9', callback_data=9) ,
              InlineKeyboardButton(text='10', callback_data=10) ,
                InlineKeyboardButton(text='11', callback_data=11) ,
                  InlineKeyboardButton(text='12', callback_data=12 )
              ]
              ]
   
    keyboard = InlineKeyboardMarkup(buttons)
    await query.message.reply_text(text=text, reply_markup=keyboard,parse_mode=telegram.constants.ParseMode.HTML)


    return PROMO_POWER




async def pro_comfirm_power(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    #这个anser好像只要之前用了回调这里就要应答一下
    #请注意这个回调是不带用户信息的,如果在这里调用 user = update.message.from_user 会得到空值
    query = update.callback_query
    await query.answer()

    context.user_data['promote_month']=query.data


    await   update.callback_query.delete_message()
    #local_store['pre_chat_id'] =this_msg.chat_id
    #local_store['pre_massage_id'] =this_msg.message_id
    #清空之前的数据
      
    text = (
        "您要为 "+context.user_data['promote_name']+" 设置多大的置顶权重? 1-100，权重越大越靠前\n"
        "你也可以输入 /cancel 退出"
    )

    await query.message.reply_text(text=text,parse_mode=telegram.constants.ParseMode.HTML)
    return PROMO_CONFIRM
    



 # Top level conversation callbacks
async def promote_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """进来时直接展示那一堆按键."""
   

    power=update.message.text

    
    now = datetime.now()
    months_later = now + relativedelta(months=int(context.user_data['promote_month']))
     
    insert_query = ('''
    UPDATE person SET promo_flag=%s,promo_start_date=%s,promo_end_date=%s,promo_power=%s WHERE id =%s

    ''')
    
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(insert_query, (1,now,months_later,power,context.user_data['promote_id']))
        conn.commit()

    except Error as e:
        print(e)      
    finally:
        if conn:
            conn.close()     
    
    text = (
        "已设置 "+context.user_data['promote_name']+" 的资料，时间结束后将自动下架\n"
        "你也可以输入 /start 继续选择其他功能"
    )
    await update.message.reply_text(text=text,parse_mode=telegram.constants.ParseMode.HTML)

    return ConversationHandler.END

#-----------------------带链接按键的推文----------------------





async def text_with_url_button_desc(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    #这个anser好像只要之前用了回调这里就要应答一下
    #请注意这个回调是不带用户信息的,如果在这里调用 user = update.message.from_user 会得到空值
    query = update.callback_query
    await query.answer()
    # text = (
    #     "OK,请继续"    
    # )
    await   update.callback_query.delete_message()
    #local_store['pre_chat_id'] =this_msg.chat_id
    #local_store['pre_massage_id'] =this_msg.message_id
    #清空之前的数据
    context.user_data.clear()
    text = (
        "请输入贴文\n"
        "你也可以输入 /cancel 退出"
    )
    #await update.message.reply_text(text=text) # 这样写是不行的,因为是在回调中,并不是顺序的消息发送中
    #或者用context.bot来发信息,不过这样发信息需要指定chatid和msgid
    await update.callback_query.message.reply_text(text=text)
    

    return BUTTON_TEXT




 # Top level conversation callbacks
async def text_with_url_button_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """进来时直接展示那一堆按键."""
   

    text=update.message.text

    context.user_data['text_button'] =text
    
    text = (
        "请输入按键链接\n"
        "你也可以输入 /cancel 退出"
    )
    await update.message.reply_text(text=text,parse_mode=telegram.constants.ParseMode.HTML)

    return BUTTON_URL


 # Top level conversation callbacks
async def text_with_url_button_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """进来时直接展示那一堆按键."""
   

    this_url=update.message.text

    keyboard = [[InlineKeyboardButton("爱城榜单", url=this_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await  context.bot.send_message(chat_id=CHANNEL_ID, text=context.user_data['text_button'], 
                             reply_markup=reply_markup,parse_mode=telegram.constants.ParseMode.HTML)
    await update.message.reply_text(text='消息已发布到频道\nOK,你可以输入 /start 继续选择你要做的事情',parse_mode=telegram.constants.ParseMode.HTML)
    return ConversationHandler.END





async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data.clear()
    text = (
        "OK,你可以输入 /start 继续选择你要做的事情\n"
    )
    await update.message.reply_text(text=text)
    return ConversationHandler.END

#不允许别的群添加机器人
async def leaveChat(update: Update, context:  ContextTypes.DEFAULT_TYPE) -> int:
    #print(update.message)
    chat_id=update.message.chat_id
    if chat_id!=GROUP_ID and chat_id!=CHANNEL_ID:
       await context.bot.leave_chat(chat_id)



# #TODO
# async def notice_plus_count(context: ContextTypes.DEFAULT_TYPE):
#      # 定义一个查询，如果有数据则更新，否则插入
#     query = ('''SELECT id ,NAME,channel_id,c_message_id, 
# (SELECT bb.g_message_id FROM channel_group_rel bb 
#  WHERE bb.c_message_id=aa.c_message_id) g_message_id, 
# show_count_in_group FROM person aa WHERE aa.show_count_in_group >0''')
    
#     update_query = ('''UPDATE person SET show_count_in_group=show_count_in_group-%s WHERE id = %s''')
    
#     # 执行查询
#     conn = None

#     try:
#         conn = get_connection()
#         cursor = conn.cursor()
#         cursor.execute(query, (context.user_data['name'],))
#         count = cursor.fetchone()[0]
  
#         if count > 0:
#             # 如果有数据，执行更新操作
#             cursor.execute(update_query, (
#             context.user_data['logo_url'],
#             context.user_data['channel_id'],
#             context.user_data['c_message_id'],
#             0,datetime.now(),
#             context.user_data['name']
#             ))
#            # print(cursor.rowcount, "行受影响，数据已更新")
#         else:
#             # 如果没有数据，执行插入操作
#             cursor.execute(insert_query, (
#             context.user_data['name'],
#             context.user_data['logo_url'],
#             context.user_data['channel_id'],
#             context.user_data['c_message_id'],
#             0,datetime.now()   
#             ))

#         conn.commit()
 
#     except Error as e:
#         print(e)      
#     finally:
#         if conn:
#             conn.close() 

#     pass



#轮播

#这个之前发帖记录就不用数据库存了，存程序里，如果漏了就手动删除一下
pre_brocast_c_msg_id=None

random_sql='''
SELECT aa.name, aa.logo_url,aa.c_message_id, (SELECT bb.g_message_id FROM channel_group_rel bb WHERE bb.c_message_id=aa.c_message_id LIMIT 1) g_message_id
FROM person aa ORDER BY RAND() LIMIT 1'''


async def roll_brocast (context: ContextTypes.DEFAULT_TYPE):

    #print('执行轮播')
    await roll_brocast_next(context)


async def roll_brocast_next(context: ContextTypes.DEFAULT_TYPE):
    #删除原来的，并不是严格的
    global pre_brocast_c_msg_id

    if pre_brocast_c_msg_id is not None:
        await context.bot.delete_message(chat_id=CHANNEL_ID,message_id=pre_brocast_c_msg_id) 

    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(random_sql)
        for row in cursor:
            name=row[0]
            logo_url=row[1]
            c_message_id=row[2]
            g_message_id=row[3]
            file_name=deal_img(logo_url)

            if file_name is None :
               return

            report_args= 'report_'+str(c_message_id)+'_' +str(g_message_id)
            report_args= aes_encrypt(AES_KEY, AES_iv, report_args) 

            meme_args= 'meme_'+str(c_message_id)+'_' +str(g_message_id)
            meme_args= aes_encrypt(AES_KEY, AES_iv, meme_args) 

              
            text=f'''
<b>☀️爱城日❤️日轮播 {name}</b>
📣频道链接 t.me/NanningAic/{c_message_id}
📙收藏目录 t.me/pcratebot/pcl
<b><a href="https://t.me/pc_reporter_bot?start={report_args}">✏️ 写体验报告</a></b> | <b><a href="https://t.me/not_kown_bot?start={meme_args}">🙈 写匿名问答</a></b>
'''
 
            button=[

                [ InlineKeyboardButton(text='🗨️讨论 >', url=f'https://t.me/NanningAic/{c_message_id}?comment=1') ]

            ]
                    
            
            keyboard = InlineKeyboardMarkup(button)
            curent_msg=await context.bot.send_photo(
						chat_id=CHANNEL_ID,
						photo=file_name,
						caption=text,
                        reply_markup=keyboard,
						parse_mode=constants.ParseMode.HTML
					)
            
            #记录一下要删除
            pre_brocast_c_msg_id=curent_msg.message_id

            for file_path in [file_name]:
                if os.path.exists(file_path):
                    # 删除文件
                    try:
                        os.remove(file_path)
                    except:
                        logger.info(f'{file_path}删除失败')		
    except Error as e:
        print(e)      
    finally:
        if conn:
            conn.close()     
    
   

    pass

def deal_img(file_name):
    print(file_name)
    # 文件的 URL
    file_url = f"https://telegra.ph{file_name}"

    # 发起 GET 请求获取文件
    response = requests.get(file_url)

    # 检查响应状态码是否为 200（表示成功）
    if response.status_code == 200:
        # 提取文件名
        file_name = file_url.split("/")[-1]

        # 保存文件
        with open(file_name, "wb") as file:
            file.write(response.content)
        return file_name
    else:
        print("下载失败，响应状态码非 200")
        return None
    
    #---------处理一下，截成正方形，暂时不用




    

def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TOKEN).build() 
    #状态转换
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            
            SELECTING:[#这里有三个按键的逻辑
                 CallbackQueryHandler(input_name_desc, pattern="^" + str(ADDING) + "$"),
                 CallbackQueryHandler(delete_desc, pattern="^" + str(DELETEING) + "$"),
                 CallbackQueryHandler(promote_desc, pattern="^" + str(PROMOTING) + "$"),
                CallbackQueryHandler(text_with_url_button_desc, pattern="^" + str(TEXT_WITH_BUTTON_DESC) + "$"),
               
            ],
            INPUT_DESC:[MessageHandler(filters.TEXT & ~filters.COMMAND, input_name)],
            LOGO_IMG:[MessageHandler(filters.PHOTO, choose_logo_img),CommandHandler("skip", skip_logo_img)],
            DESC_IMG:[MessageHandler(filters.PHOTO, choose_desc_img),CommandHandler("skip", skip_desc_img)],
            #这里可能会收到多个相片
            BIO: [MessageHandler(filters.PHOTO, choose_desc_img),
                  MessageHandler(filters.TEXT & ~filters.COMMAND, bio),
                  CommandHandler("cancel", cancel),
                  CommandHandler("skip", skip_bio ),
                  ],
            #GET_CHANNEL_MSG:[MessageHandler(filters.ChatType.GROUPS, getForwardMsg)],

            #------------------------delete------------------------------------
            #DEL_INPUT_DESC,DEL_CONFIRM,DEL_CONFIRM_DONE,
            DEL_INPUT_SELECT:[  MessageHandler(filters.TEXT & ~filters.COMMAND, del_select)],
            DEL_CONFIRM:[ CallbackQueryHandler(del_comfirm, pattern="^\d+$")],
            DEL_CONFIRM_DONE:[ CallbackQueryHandler(del_comfirm_done, pattern="^\d+$")],

            #-------------------------promo-----------------------------------
            PROMO_INPUT_SELECT:[  MessageHandler(filters.TEXT & ~filters.COMMAND, promote_select)],
            PROMO_MONTH:[ CallbackQueryHandler(pro_comfirm_month, pattern="^\d+$")],
            PROMO_POWER:[ CallbackQueryHandler(pro_comfirm_power, pattern="^\d+$")],
            PROMO_CONFIRM:[ MessageHandler(filters.TEXT & ~filters.COMMAND, promote_confirm)],

            #-------------------------text_button-----------------------------------
            #TEXT_WITH_BUTTON_DESC,BUTTON_TEXT,BUTTON_URL,V24,V25,
            BUTTON_TEXT:[  MessageHandler(filters.TEXT & ~filters.COMMAND, text_with_url_button_text)],
            BUTTON_URL:[  MessageHandler(filters.TEXT & ~filters.COMMAND, text_with_url_button_url)],
            
            END:[]
           },
    fallbacks=[CommandHandler("cancel", cancel)],
     )


    application.add_handler(conv_handler)
    #这里再声明一次start的调用,要不用户中途点start不会有出发
    #application.add_handler(MessageHandler(filters.Command(['start']), start))
    #这个回调加在其他地方有可能收不到频道转发的第一条消息，只能加在这里
    #如果过有多个重复的filter筛选出了相同的多个回调，回调只会触发一次

    application.add_handler(
        MessageHandler(
        filters.ChatType.GROUPS &filters.ForwardedFrom(chat_id=CHANNEL_ID) , 
        callback=getForwardMsg
        )    
    )

    application.add_handler(
        MessageHandler(
        filters.ALL , 
        callback=getNewMsg
        )    
    )


    application.add_handler(
        MessageHandler(
        filters=filters.StatusUpdate.NEW_CHAT_MEMBERS,
        callback=leaveChat
        )
    )

   

    application.job_queue.run_daily(callback= roll_brocast,time= time2(hour=19,minute=54,second=0,tzinfo=pytz.timezone('Asia/Shanghai')),)
   

    # Run the bot until the user presses Ctrl-C
    while True:
        try:
            application.run_polling()
        except Exception:
            logger.info("连接错误")
            time.sleep(5)



if __name__ == "__main__":
    main()




