# -*- coding: utf-8 -*-
from telegram import  Update,constants,InputMediaPhoto,InputMediaVideo
from telegram.ext import  (CommandHandler, CallbackContext,
                          Application,ConversationHandler, MessageHandler, filters)
import time
import logging
import datetime
import asyncio
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import mysql.connector
import traceback
from mysql.connector import Error


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


dbconfig = {
    'host': 'localhost',
    'database': 'pc_db',
    'user': 'root',
    'password': '!123456xyZ'
}
pool = mysql.connector.pooling.MySQLConnectionPool(pool_name='mypool', pool_size=3, **dbconfig)



# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

(MEME,END,MEME2,V4,V5,
 V6,V7,V8,V9,V10,
 V11,V12,V13,V14,V15,
 V16,V17,V18,V19,V20,
 V21,V22,V23,V24,V25,
 V26,V27,V28,V29,V30,
 V31,V32,V33,V34,V35,
 V36,V37,V38,V39,V40,
 V41,V42,V43,V44,V45,
 SUBMIT,WAIT) = map(chr, range(0,47)) #生成一些状态码,为什么不直接用int,因为会引发一些冲突

CHANNEL_ID=-1001382928142
GROUP_ID=-1001865849787
ODIT_GROUP_ID=-1001926762058
LEGAL_GROUP=[GROUP_ID,CHANNEL_ID,ODIT_GROUP_ID]

ADMIN_ID=[1280532381,5748943638]
AES_KEY = b'823yhw8hw9u3j387'  # 16字节的密钥
AES_iv =  b'2379s8je8wjow93j'  # 16字节的初始化向量

GROUP_URL="https://t.me/nanningAi/"


#加一个时间限制,限制一分钟发言
user_time_limit={}

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


def timeLimit(user_id):
    now = datetime.datetime.now()
    # 计算时间差异
    if user_id not in user_time_limit:
        return False
    input_time=user_time_limit[user_id]

    diff = now - input_time
    # 判断时间差异是否大于1分钟
    if diff.total_seconds() > 60:
        return False
    else:
        return True


async def start(update: Update, context: CallbackContext) -> int:
    
    #logger.info(update.message.text)
    #logger.info(context.args)
    context.user_data.clear()
   
    if context.args:
        
        if  update.message.chat_id<0 :
            await update.message.reply_text(text="不能以群组身份发言")
            return ConversationHandler.END
        
        if  timeLimit(update.message.chat_id) :
            await update.message.reply_text(text="请间隔一分钟以后再发言")
            return ConversationHandler.END

        context.user_data['crypto_str']=context.args[0]
        #print(context.args[0])
        try:
            prams_str=aes_decrypt(AES_KEY, AES_iv, str(context.args[0]))
        except:
            text = (
            "参数非法"
            )
            await update.message.reply_text(text=text)
            return ConversationHandler.END
        
        pramList=prams_str.split('_')
        function_name=pramList[0]   
        prams=()
        for i in range(1,len(pramList)):
            prams+=(pramList[i],)
        # 创建类实例
        function = globals()[function_name]
        context.user_data[function_name]=prams
        return await function(update , context )
    else:
        await update.message.reply_text(text="请您从频道或群聊中点击匿名评论按键")
        return ConversationHandler.END
     
 

async def meme(update: Update, context: CallbackContext) -> int:

    prams=context.user_data['meme']
    if len(prams)==2:
        c_msg_id=int(prams[0])

        query = ("SELECT name FROM person WHERE c_message_id = %s")
        
        name='未知名'

        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(query, (c_msg_id,))
            for result in cursor:
                name=result[0]
                break
        except Error as e:
            print(e)      
        finally:
            if conn:
                conn.close()         

        text = (
        "关于 "+name+" 的问与答:\n\n")
    else:
         text = (
        "对匿名消息"+context.user_data['crypto_str']+" 的问与答:\n\n")

    text=text+(
        #"<b>勿涉及除服务内容外的隐私\n\n</b>"
        "可输入图片,视频和文字:\n\n(您在流程中可输入 /cancel 退出流程)"
        )
    
    await update.message.reply_text(text=text,parse_mode=constants.ParseMode.HTML)
    return MEME

async def echo_text(update: Update, context: CallbackContext) -> int:
    prams=context.user_data['meme']
    if len(prams)==2:
        c_msg_id=int(prams[0])
        g_msg_id=int(prams[1])
    else:
        g_msg_id=int(prams[0])
       
    try:
        text=update.message.text
        #print(text)
        #print(GROUP_ID)
        #print(g_msg_id)
        new_msg=await context.bot.sendMessage(chat_id=GROUP_ID,text=text,reply_to_message_id=g_msg_id,parse_mode=constants.ParseMode.HTML)

        args= 'meme_'+str(new_msg.message_id)
        args= aes_encrypt(AES_KEY, AES_iv, args) 

        await context.bot.edit_message_text(
                        chat_id=new_msg.chat_id,
                        message_id=new_msg.message_id ,
                        text='<i>'+new_msg.text+(
                        '</i>\n\n'+
                        '<b><a href="https://t.me/not_kown_bot?start='
                        +args+'">匿名问答</a></b>'
                        
            
        ),parse_mode=constants.ParseMode.HTML
        )

    

        #--------------------limit--------------

        user_time_limit[update.message.chat_id]=datetime.datetime.now()

        #--------------------odit---------------
        try:
            await context.bot.forward_message(chat_id=ODIT_GROUP_ID,
                                                    from_chat_id=update.effective_chat.id,
                                                    message_id=update.message.message_id)
        except:
            logger.info('记录失败点2')

        context.user_data.clear()
        text = (
            "操作已完成,请您返回群组查看消息"
        )
        await update.message.reply_text(text=text)

        #--------------------更新一个最新ID--------------
        await updateNewMsgByThreadId(new_msg)

        return ConversationHandler.END

    except :
        traceback.print_exc()
        return await error(update, context)
    #return await end(update, context)



#更新一个帖子的最大msgid                           
async def updateNewMsgByThreadId(massage):

    #print(massage)
 
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


async def echo_media(update: Update, context: CallbackContext) -> int:
   
    msg = update.message
    #print(msg)

    if msg.media_group_id is None:
        return await single_send_media(update, context)
    elif  'media_group_id' not in context.user_data:
        context.user_data['media_group_id']=msg.media_group_id
        context.user_data['medias']=[]
        context.user_data['delay_send']=False
    elif context.user_data['media_group_id'] != msg.media_group_id:
        return
    else:
        pass

    if  'caption' not in context.user_data:
        if  update.message.caption:   
            context.user_data['caption']=update.message.caption
    
    if update.message.photo:
        context.user_data['medias'].append({'type':'photo',  'v': update.message.photo[-1].file_id})

    if update.message.video:
        context.user_data['medias'].append({'type':'vedio','v': update.message.video.file_id})


    if context.user_data['delay_send']==False:
        context.user_data['delay_send']=True
        task = asyncio.create_task(delay_send_media_group(update, context))
    
    #--------------------------limit------------------------------
    user_time_limit[update.message.chat_id]=datetime.datetime.now()
    #--------------------------odit-------------------------------
    try:
        await context.bot.forward_message(chat_id=ODIT_GROUP_ID,
                                                    from_chat_id=update.effective_chat.id,
                                                    message_id=update.message.message_id)
    except:
        logger.info('记录失败点2')
    # await  delay_send_media_group(update, context)


async def single_send_media(update: Update, context: CallbackContext) -> int:
    prams=context.user_data['meme']
    if len(prams)==2:
        c_msg_id=int(prams[0])
        g_msg_id=int(prams[1])
    else:
        g_msg_id=int(prams[0])
    
    if update.message.photo:
        medias = [InputMediaPhoto(media=update.message.photo[-1].file_id)]
    elif update.message.video:
        medias = [InputMediaVideo(media=update.message.video.file_id)]
                        
    new_msgs=await context.bot.send_media_group(
        chat_id=GROUP_ID,
        caption=update.message.caption,
        media=medias,
        reply_to_message_id=g_msg_id,
        parse_mode=constants.ParseMode.HTML)
    
    new_msg=new_msgs[0]

    if new_msg.caption:
        caption_text=new_msg.caption
    else:
        caption_text=''
    
    args= 'meme_'+str(new_msg.message_id)
    args= aes_encrypt(AES_KEY, AES_iv, args) 

    await context.bot.edit_message_caption(
            chat_id=new_msg.chat_id,
            message_id=new_msg.message_id ,
            caption='<i>'+caption_text+(
            '</i>\n\n'+
            '<b><a href="https://t.me/not_kown_bot?start='
            +args+'">匿名问答</a></b>'
            ),parse_mode=constants.ParseMode.HTML) 
    

    
    context.user_data.clear()
    text = (
        "操作已完成,请您返回群组查看消息"
    )
    await update.message.reply_text(text=text)
    return ConversationHandler.END

                         

async def delay_send_media_group(update: Update, context: CallbackContext) -> int:
    text = (
        "已收到文件，请稍候..."
    )
    await update.message.reply_text(text=text)
    await asyncio.sleep(3)  # 等待3秒钟

    prams=context.user_data['meme']
    if len(prams)==2:
        c_msg_id=int(prams[0])
        g_msg_id=int(prams[1])
    else:
        g_msg_id=int(prams[0])


    medias = []

    for pair in  context.user_data['medias']:
        #print(pair)
        if pair['type']=='photo':
            medias.append(InputMediaPhoto(media=pair['v']))
        elif pair['type']=='vedio':
            medias.append(InputMediaVideo(media=pair['v']))
        else:pass

    if 'caption' in context.user_data:
        new_msgs=await context.bot.send_media_group(
            chat_id=GROUP_ID,
            caption=context.user_data['caption'],
            media=medias,
            reply_to_message_id=g_msg_id,
            parse_mode=constants.ParseMode.HTML)
    else:
        new_msgs=await context.bot.send_media_group(
            chat_id=GROUP_ID,
            media=medias,
            reply_to_message_id=g_msg_id,
            parse_mode=constants.ParseMode.HTML)

    new_msg=new_msgs[0]

    if new_msg.caption:
        caption_text=new_msg.caption
    else:
        caption_text=''
    
    args= 'meme_'+str(new_msg.message_id)
    args= aes_encrypt(AES_KEY, AES_iv, args) 

    await context.bot.edit_message_caption(
                    chat_id=new_msg.chat_id,
                    message_id=new_msg.message_id ,
                    caption='<i>'+caption_text+(
                    '</i>\n\n'+
                    '<b><a href="https://t.me/not_kown_bot?start='
                    +args+'">匿名问答</a></b>'
                    ),parse_mode=constants.ParseMode.HTML)

    context.user_data.clear()
    text = (
        "操作已完成,请您返回群组查看消息"
    )
    await update.message.reply_text(text=text)
    return ConversationHandler.END

#针对没有匿名链接的消息生成匿名信息


def extract_number_from_url(url):
    prefix = GROUP_URL  
    if url.startswith(prefix):
        suffix = url[len(prefix):]
        if suffix.isdigit():
            return int(suffix)
    return None

async def handle_forwarded_message(update: Update, context: CallbackContext) -> int:

    if  update.message.chat_id<0 :
        #群组中的发言处理
        return ConversationHandler.END

    message= update.message
    #print (message)
    g_msg_id=extract_number_from_url(message.text)
    if  g_msg_id is None:
        text='消息来源不合法,仅处理群组 @nanningAi 的消息,其他群组或私聊的消息无法匿名回复'
        await update.message.reply_text(text=text)
        return ConversationHandler.END
    

        
    if  timeLimit(update.message.chat_id) :
        await update.message.reply_text(text="请间隔一分钟以后再发言")
        return ConversationHandler.END
  
    context.user_data['meme']= [g_msg_id]
    text='请输入您要匿名回复的消息, 可输入图片,视频和文字:\n\n(或输入 /cancel 退出流程)' 
    await update.message.reply_text(text=text)
    return MEME2



async def error(update: Update, context: CallbackContext) -> int:
    context.user_data.clear()
    text = (
        "代码出错了\n"
    )
    await update.message.reply_text(text=text)
    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext) -> int:
    context.user_data.clear()
    text = (
        "OK,你可以输入 /start 继续选择你要做的事情\n"
    )
    await update.message.reply_text(text=text)
    return ConversationHandler.END

#不允许别的群添加机器人
async def leaveChat(update: Update, context: CallbackContext) -> int:
    #print(update.message)
    chat_id=update.message.chat_id
    if chat_id not in LEGAL_GROUP:
       await context.bot.leave_chat(chat_id)

# 定义主函数，创建和启动机器人
def main():
    # 创建机器人实例，并获取Updater
    
    application = Application.builder().token('6104087431:AAGXb-pbyDz_64kYpEb3aJ2yIF0k9Vaw4tc').build() 
  
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={         
            MEME:[ 
                #这句是意思是文本但非命令
                MessageHandler(filters.TEXT & ~filters.COMMAND, echo_text),
                MessageHandler(filters.PHOTO|filters.VIDEO, echo_media),
              ]         
           },
    fallbacks=[CommandHandler("cancel", cancel),CommandHandler("start", start)],
    )

    
    # 主回调添加多选按钮的回调函数
    conv_handler_create_anymous = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & ~filters.COMMAND, handle_forwarded_message)],

        states={
            MEME2:[ 
                #这句是意思是文本但非命令
                MessageHandler(filters.TEXT & (~filters.COMMAND)  & (~filters.FORWARDED), echo_text),
                MessageHandler(filters.PHOTO|filters.VIDEO, echo_media),
            ] ,

            
           },
    fallbacks=[CommandHandler("cancel", cancel),CommandHandler("start", start)],
    )
   
    application.add_handler(conv_handler)
    application.add_handler(conv_handler_create_anymous)
    application.add_handler(MessageHandler(filters=filters.StatusUpdate.NEW_CHAT_MEMBERS,callback=leaveChat))

 
       # Run the bot until the user presses Ctrl-C
    while True:
        try:
            application.run_polling()
        except Exception:
            print("连接错误")
            print(Exception)
            time.sleep(5)
 
if __name__ == '__main__':
    main()