# -*- coding: utf-8 -*-
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update,constants,InputMediaPhoto,InputMediaVideo
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext,Application,ConversationHandler,MessageHandler,filters
import time
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import base64
import mysql.connector
import asyncio
import datetime
from mysql.connector import Error


(V1,V2,V3,V4,V5,
 V6,V7,V8,V9,V10,
 V11,V12,V13,V14,V15,
 V16,V17,V18,V19,V20,
 V21,V22,V23,V24,V25,
 V26,V27,V28,V29,V30,
 V31,V32,V33,V34,V35,
 V36,V37,V38,V39,V40,
 VALUE_FACE_INPUT,VALUE_BODY_INPUT,VALUE_HORNY_INPUT,WAIT_ROOM_DESC,ROOM_SUBMIT,
 CHOOSE_IF_ANONYMOUS,NAMED,ANONYMOUS,CONTACT_INPUT,PRICE_INPUT,
 R1,R2,R3,R4,R5,
 R6,R7,R8,R9,R10,
 ROOM1,ROOM2,ROOM3,ROOM4,ROOM5,
 SERVICES_SUBMIT,WAIT_CHECK_BOX,DETAIL_INFO,WAIT_MEDIA,IF_SEND,
 SEND,REJECT,NOTICE_IMG,CREATE_PRE,
 MEME,MEME2,P3,P4,P5) = map(chr, range(0,79)) #生成一些状态码,为什么不直接用int,因为会引发一些冲突

# 定义多选按钮的标签和对应的值
OPTIONS = {V1:'莞式',V2:'快餐',V3:'中介',V4:'熟女',V5:'御姐',
           V6:'萝莉',V7: '女友',V8:'反差',V9:'虐恋',V10:'扮演',
           V11:'丰满',V12:'匀称',V13:'苗条',V14:'丰乳',V15:'贫乳',
           V16:'乳汁',V17:'肥臀',V18:'细腰',V19:'足交', V20:'做爱',
           V21:'接吻',V22:'口交',V23:'口爆',V24:'颜射', V25:'吞精',
           V26:'可扣',V27:'六九',V28:'可舔',V29:'乘骑', V30:'共浴',
           V31:'毒龙',V32:'无套',V33: '肛交',V34:'潮吹', V35:'多人',
           V36:'露出',V37:'健谈' ,V38:'摄影',V39:'主动',V40:'包夜'           
            }

ROOM_OPTIONS={
            ROOM1:'站街',ROOM2:'酒店',ROOM3:'带房',ROOM4:'温馨小窝',ROOM5:'高端住宅'

}
 

    


CHANNEL_ID=-1001382928142
GROUP_ID=-1001865849787
ODIT_GROUP_ID=-1001926762058

LEGAL_GROUP=[GROUP_ID,CHANNEL_ID,ODIT_GROUP_ID]

ADMIN_ID=[1280532381,5748943638]

AES_KEY = b'823yhw8hw9u3j387'  # 16字节的密钥
AES_iv =  b'2379s8je8wjow93j'  # 16字节的初始化向量

GROUP_URL="https://t.me/nanningAi/"

dbconfig = {
    'host': 'localhost',
    'database': 'pc_db',
    'user': 'root',
    'password': '!123456xyZ'
}
pool = mysql.connector.pooling.MySQLConnectionPool(pool_name='mypool', pool_size=3, **dbconfig)

user_time_limit={}
#用来缓存在频道中出击报告的postid
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

def number_to_emoji(num):
    emoji_dict = {
        "0": "0️⃣","1": "1️⃣", "2": "2️⃣",
        "3": "3️⃣", "4": "4️⃣","5": "5️⃣",
        "6": "6️⃣","7": "7️⃣","8": "8️⃣",
        "9": "9️⃣", "10": "🔟"
    }

    return emoji_dict[str(num)]


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
    
    #print(update.message)
    #logger.info(context.args)

    if  update.message.chat_id<0 :
        await update.message.reply_text(text="不能以群组身份发言")
        return ConversationHandler.END
        
    if  timeLimit(update.message.chat_id) :
        await update.message.reply_text(text="请间隔一分钟以后再发言")
        return ConversationHandler.END


    context.user_data.clear()
    
    if context.args:
        context.user_data['crypto_str']=context.args[0]
        #print(context.args[0])
        try:
            prams_str=aes_decrypt(AES_KEY, AES_iv, str(context.args[0]))
        except:
            await update.message.reply_text(text="参数非法")
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
     

#-----------------------------------------------匿名回复功能-----------------------------------------------------------



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
        "对报告消息"+context.user_data['crypto_str']+" 的问与答:\n\n")

    text=text+(
        #"<b>勿涉及除服务内容外的隐私\n\n</b>"
        "可输入图片,视频和文字:\n\n(或输入 /cancel 退出流程)"
        )
    
    await update.message.reply_text(text=text,parse_mode=constants.ParseMode.HTML)
    return MEME




async def echo_text_meme(update: Update, context: CallbackContext) -> int:
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
                        '<b><a href="https://t.me/pc_reporter_bot?start='
                        +args+'">匿名问答</a></b>'
                        
            
        ),parse_mode=constants.ParseMode.HTML
        )

        #--------------------limit--------------

        user_time_limit[update.message.chat_id]=datetime.datetime.now()      
        #--------------------------odit-------------------------------
        try:
            await context.bot.forward_message(chat_id=ODIT_GROUP_ID,
                                                        from_chat_id=update.effective_chat.id,
                                                        message_id=update.message.message_id)
        except:
            print('记录失败点2')

        context.user_data.clear()
        text = (
            "操作已完成,请您返回群组查看消息"
        )

        #----------------记录新消息-----------------------------------
        await updateNewMsgByThreadId(new_msg)  

        await update.message.reply_text(text=text)
        return ConversationHandler.END

    except :
        return await error(update, context)
    #return await end(update, context)

async def echo_media_meme(update: Update, context: CallbackContext) -> int:
   
    msg = update.message
    #print(msg)

    if msg.media_group_id is None:
        return await single_send_media_meme(update, context)
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

       # await  delay_send_media_group(update, context)
    #--------------------limit--------------

    user_time_limit[update.message.chat_id]=datetime.datetime.now()
    #--------------------------odit-------------------------------
    try:
        await context.bot.forward_message(chat_id=ODIT_GROUP_ID,
                                                    from_chat_id=update.effective_chat.id,
                                                    message_id=update.message.message_id)
    except:
        print('记录失败点2')


async def single_send_media_meme(update: Update, context: CallbackContext) -> int:
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
                        
    new_msgs=await context.bot.send_media_group_meme(
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
            '<b><a href="https://t.me/pc_reporter_bot?start='
            +args+'">匿名问答</a></b>'
            ),parse_mode=constants.ParseMode.HTML) 
    
    context.user_data.clear()
    text = (
        "操作已完成,请您返回群组查看消息"
    )
    await update.message.reply_text(text=text)
    return ConversationHandler.END

                         

async def delay_send_media_group_meme(update: Update, context: CallbackContext) -> int:
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
                    message_id='<i>'+new_msg.message_id ,
                    caption=caption_text+(
                    '</i>\n\n'+
                    '<b><a href="https://t.me/pc_reporter_bot?start='
                    +args+'">匿名问答</a></b>'
                    ),parse_mode=constants.ParseMode.HTML)

    context.user_data.clear()
    text = (
        "操作已完成,请您返回群组查看消息"
    )
    await update.message.reply_text(text=text)
    return ConversationHandler.END




async def error(update: Update, context: CallbackContext) -> int:
    context.user_data.clear()
    text = (
        "代码出错了\n"
    )
    await update.message.reply_text(text=text)
    return ConversationHandler.END


#----------------------------------------------报告功能-----------------------------------------------------------------

async def report(update: Update, context: CallbackContext) -> int:
    context.user_data['services']={}
    context.user_data['room_desc']={}
    context.user_data['medias']=[]
    #统一加上logo
    context.user_data['medias'].append({'type':'photo',  'v': 'AgACAgUAAxkBAAIHkGSlZRgz_l0mynfU-KUssDNBUQQkAAJ1tDEbwvUZVedWo5KjXsPCAQADAgADeQADLwQ'})

    prams=context.user_data['report']
    if len(prams)==2:
        c_msg_id=int(prams[0])
        context.user_data['c_msg_id']=c_msg_id
        context.user_data['g_msg_id']=int(prams[1])
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

        context.user_data['nickname'] =  name 
        text = ("对 "+name+" 的体验报告:\n\n请选择署名/匿名发布报告:\n(您在流程中可输入 /cancel 退出流程)")
    else:
        await update.message.reply_text(text='参数非法',parse_mode=constants.ParseMode.HTML)
        return ConversationHandler.END

    context.user_data['post_name']=update.message.from_user.first_name
    #print(update.message.from_user.username)
    if update.message.from_user.username:                       
             context.user_data['post_name_url']= ('<a href="https://t.me/' +
             str(update.message.from_user.username)
             +'">'+
             str(update.message.from_user.first_name)+'</a>')

    keyboard = [
        [InlineKeyboardButton('署名', callback_data=NAMED),
        InlineKeyboardButton('匿名', callback_data=ANONYMOUS)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await  update.message.reply_text(text=text, reply_markup=reply_markup)
 
    return CHOOSE_IF_ANONYMOUS

#    'name','post_name','contacts','price','services','vlaue_face','room_desc','value_horny','full_desc'


async def choose_anonymous(update: Update, context: CallbackContext):
    query=update.callback_query
    await query.answer()
    data=query.data
    if data==ANONYMOUS:
        context.user_data['post_name']='匿名者'
        if 'post_name_url' in  context.user_data:
            del context.user_data['post_name_url']
    
    await query.message.delete()
    await query.message.reply_text(text='好的,亲爱的'+context.user_data['post_name']+':\n请您输入TA的联系方式')
    

    return CONTACT_INPUT


 
async def contact_input(update: Update, context: CallbackContext):
    text=update.message.text
    if text and text !='':
        context.user_data['contacts']=text
    await  update.message.reply_text(text=(
        '已收到联系方式\n请您输入TA的服务价格/次数(p)'
    ))
    return PRICE_INPUT


# 定义多选按钮的回调函数
async def price_input(update: Update, context: CallbackContext):

    text=update.message.text
    if text and text !='':
        context.user_data['prices']=text
    text='价格为:'+context.user_data['prices']+'\n接下来,请为TA的颜值打分'
    line1=[]
    line2=[]
    for i in range(0,5):
        line1.append(InlineKeyboardButton(str(i+1), callback_data=str(int(R1)+i+1)))
    for i in range(5,10):
        line2.append(InlineKeyboardButton(str(i+1), callback_data=str(int(R1)+i+1)))
    reply_markup = InlineKeyboardMarkup([line1,line2])
    await  update.message.reply_text(text=text, reply_markup=reply_markup) 

    return VALUE_FACE_INPUT


async def value_face_rate(update: Update, context: CallbackContext):

    query=update.callback_query
    await query.answer()
    data=query.data
    context.user_data['face_value']=str(int(data)-int(R1))
    
    text='颜值为'+context.user_data['face_value']+'分\n您主观认为TA的身材有多好,请打分'
    line1=[]
    line2=[]
    for i in range(0,5):
        line1.append(InlineKeyboardButton(str(i+1), callback_data=str(int(R1)+i+1)))
    for i in range(5,10):
        line2.append(InlineKeyboardButton(str(i+1), callback_data=str(int(R1)+i+1)))
    reply_markup = InlineKeyboardMarkup([line1,line2])
    await  query.message.edit_text(text=text, reply_markup=reply_markup)     
    
    return VALUE_BODY_INPUT



async def value_body_rate(update: Update, context: CallbackContext):

    query=update.callback_query
    await query.answer()
    data=query.data
    context.user_data['body_value']=str(int(data)-int(R1))

 
    text='身材为'+context.user_data['body_value']+'分\n您主观认为对TA有多少性欲,请打分'
    line1=[]
    line2=[]
    for i in range(0,5):
        line1.append(InlineKeyboardButton(str(i+1), callback_data=str(int(R1)+i+1)))
    for i in range(5,10):
        line2.append(InlineKeyboardButton(str(i+1), callback_data=str(int(R1)+i+1)))
    reply_markup = InlineKeyboardMarkup([line1,line2])
    await  query.message.edit_text(text=text, reply_markup=reply_markup)     
    
    return VALUE_HORNY_INPUT



# 定义多选按钮的回调函数
async def room_desc_input(update: Update, context: CallbackContext):

    query=update.callback_query
    await query.answer()
    data=query.data
    context.user_data['horny_value']=str(int(data)-int(R1))
    await  query.message.edit_text('已收到关于TA的颜值,身材等数值评分')    


    #print (update.message.text)
    # 创建多选按钮
  
     # 重新创建多选按钮
    keyboard_out = []
    keyboard = []
    #print(ROOM_OPTIONS)
    for value,text in ROOM_OPTIONS.items():
        # 根据当前选中的状态，设置按钮的文本和回调函数
        if text in  context.user_data['room_desc']:
            text =  '✅ '+text
            callback_data = value
        else:
            text =  '◻️ '+text
            callback_data = value
        keyboard.append(InlineKeyboardButton(text, callback_data=callback_data))
        if len(keyboard)==3:
           keyboard_out.append(keyboard)  
           keyboard = []

    keyboard_out.append(keyboard) 

    if len( context.user_data['room_desc'])==0:
        keyboard_out.append([InlineKeyboardButton('跳过', callback_data=ROOM_SUBMIT)])
    else:
        keyboard_out.append([InlineKeyboardButton('提交 🆗', callback_data=ROOM_SUBMIT)])
    
    # 将多选按钮添加到消息中，并发送给用户
    reply_markup = InlineKeyboardMarkup(keyboard_out)
    await  query.message.reply_text('请选择TA课室环境情况,可多选:', reply_markup=reply_markup)

    # 设置下一步的回调函数
    return WAIT_ROOM_DESC


# 定义多选按钮的回调函数
async def room_checkbox_callback(update: Update, context: CallbackContext):
    # 获取用户选择的值
    query = update.callback_query
    await query.answer()
    value = query.data
    text=ROOM_OPTIONS[value]
    # 切换多选按钮的状态（选中/未选中）
    if text in  context.user_data['room_desc']:
        del  context.user_data['room_desc'][text]
    else:
         context.user_data['room_desc'][text] = True

    # 重新创建多选按钮
    keyboard_out = []
    keyboard = []
    for value,text in ROOM_OPTIONS.items():
        # 根据当前选中的状态，设置按钮的文本和回调函数
        if text in  context.user_data['room_desc']:
            text =  '✅ '+text
            callback_data = value
        else:
            text =  '◻️ '+text
            callback_data = value
        keyboard.append(InlineKeyboardButton(text, callback_data=callback_data))
        if len(keyboard)==3:
           keyboard_out.append(keyboard)  
           keyboard = []

    keyboard_out.append(keyboard) 

    if len( context.user_data['room_desc'])==0:
        keyboard_out.append([InlineKeyboardButton('跳过', callback_data=ROOM_SUBMIT)])
    else:
        keyboard_out.append([InlineKeyboardButton('提交 🆗', callback_data=ROOM_SUBMIT)])
    
    # 更新消息中的多选按钮，并发送给用户
    reply_markup = InlineKeyboardMarkup(keyboard_out)
    await query.edit_message_text(text='请选择TA课室环境情况,可多选:', reply_markup=reply_markup)

    # 设置下一步的回调函数
    return WAIT_ROOM_DESC



# 定义提交按钮的回调函数
async def room_submit(update: Update, context: CallbackContext):
    # 获取用户选择的值，并打印到聊天记录中
    query = update.callback_query
    await query.answer()
    # #value = query.data
    # selected_values = context.user_data['room_desc'].keys()
    # print(selected_values)

    # text=''
    # for v in selected_values:
    #     text=text+('✅#'+str(v)+'   ')
    await query.edit_message_text("已收到课室环境情况")
    #继续执行
    return await services_check_input(update , context )
 

# 定义多选按钮的回调函数
async def services_check_input(update: Update, context: CallbackContext):
  
     # 重新创建多选按钮
    keyboard_out = []
    keyboard = []
    for value,text in OPTIONS.items():
        # 根据当前选中的状态，设置按钮的文本和回调函数
        if text in  context.user_data['services']:
            text =  '✅ '+text
            callback_data = value
        else:
            text =  '◻️ '+text
            callback_data = value
        keyboard.append(InlineKeyboardButton(text, callback_data=callback_data))
        if len(keyboard)==5:
           keyboard_out.append(keyboard)  
           keyboard = []
    if len( context.user_data['services'])==0:
        keyboard_out.append([InlineKeyboardButton('跳过', callback_data=SERVICES_SUBMIT)])
    else:
        keyboard_out.append([InlineKeyboardButton('提交 🆗', callback_data=SERVICES_SUBMIT)])
    
    # 将多选按钮添加到消息中，并发送给用户
    reply_markup = InlineKeyboardMarkup(keyboard_out)
    await  update.callback_query.message.reply_text('请选择TA的特点以及所提供服务内容:', reply_markup=reply_markup)

    # 设置下一步的回调函数
    return WAIT_CHECK_BOX

# 定义多选按钮的回调函数
async def services_checkbox_callback(update: Update, context: CallbackContext):
    # 获取用户选择的值
    query = update.callback_query
    await query.answer()
    value = query.data
    text=OPTIONS[value]
    # 切换多选按钮的状态（选中/未选中）
    if text in  context.user_data['services']:
        del  context.user_data['services'][text]
    else:
         context.user_data['services'][text] = True

    # 重新创建多选按钮
    keyboard_out = []
    keyboard = []
    for value,text in OPTIONS.items():
        # 根据当前选中的状态，设置按钮的文本和回调函数
        if text in  context.user_data['services']:
            text =  '✅ '+text
            callback_data = value
        else:
            text =  '◻️ '+text
            callback_data = value
        keyboard.append(InlineKeyboardButton(text, callback_data=callback_data))
        if len(keyboard)==5:
           keyboard_out.append(keyboard)  
           keyboard = []
    if len( context.user_data['services'])==0:
        keyboard_out.append([InlineKeyboardButton('跳过', callback_data=SERVICES_SUBMIT)])
    else:
        keyboard_out.append([InlineKeyboardButton('提交 🆗', callback_data=SERVICES_SUBMIT)])
    
    # 更新消息中的多选按钮，并发送给用户
    reply_markup = InlineKeyboardMarkup(keyboard_out)
    await query.edit_message_text(text='请选择TA的特点以及所提供服务内容:', reply_markup=reply_markup)

    # 设置下一步的回调函数
    return WAIT_CHECK_BOX

# 定义提交按钮的回调函数
async def services_submit(update: Update, context: CallbackContext):
    # 获取用户选择的值，并打印到聊天记录中
    query = update.callback_query
    await query.answer()
    #value = query.data
    #selected_values = context.user_data['services'].keys()
    #print(selected_values)
 
    await query.edit_message_text('已收到勾选的服务内容\n接下来提交或图像,视频,或简短的文字描述您的体验:')    
 
    return DETAIL_INFO
 


async def echo_text(update: Update, context: CallbackContext) -> int:
   
    if update.message.text:
        context.user_data['detail']=update.message.text
 
    text = (
        "已收到您的评论"
    )
    await update.message.reply_text(text=text)

    #--------------------limit--------------

    user_time_limit[update.message.chat_id]=datetime.datetime.now()
    #--------------------------odit-------------------------------
    try:
        await context.bot.forward_message(chat_id=ODIT_GROUP_ID,
                                                    from_chat_id=update.effective_chat.id,
                                                    message_id=update.message.message_id)
    except:
        print('记录失败点2')

    return await notice_ext(update, context)

 
async def echo_media(update: Update, context: CallbackContext) -> int:
   
        
    msg = update.message
    if 'notiec_create_pre' in context.user_data and context.user_data['notiec_create_pre']==True:
       await  context.user_data['notiec_create_pre_msg'].delete() #如果出现了预览提示则仍上传图片，删上一条预览提升消息
       context.user_data['notiec_create_pre'] =False
       del context.user_data['notiec_create_pre_msg']

    #print(msg)



    if msg.media_group_id is None:
        return await single_send_media(update, context)
    elif  'media_group_id' not in context.user_data:
        context.user_data['media_group_id']=msg.media_group_id
        context.user_data['delay_send']=False
    elif context.user_data['media_group_id'] != msg.media_group_id:
        return
    else:
        pass

    if  'detail' not in context.user_data:
        if  update.message.caption and update.message.caption != '':   
            context.user_data['detail']=update.message.caption
    
    if update.message.photo:
        context.user_data['medias'].append({'type':'photo',  'v': update.message.photo[-1].file_id})

    if update.message.video:
        context.user_data['medias'].append({'type':'vedio','v': update.message.video.file_id})


    if context.user_data['delay_send']==False:
        context.user_data['delay_send']=True
        task = asyncio.create_task(delay_send_media_group(update, context))


    #--------------------limit--------------

    user_time_limit[update.message.chat_id]=datetime.datetime.now()
    #--------------------------odit-------------------------------
    try:
        await context.bot.forward_message(chat_id=ODIT_GROUP_ID,
                                                    from_chat_id=update.effective_chat.id,
                                                    message_id=update.message.message_id)
    except:
        print('记录失败点2')

    return NOTICE_IMG
 

async def single_send_media(update: Update, context: CallbackContext) -> int:
     
    if update.message.photo:
        context.user_data['medias'].append({'type':'photo','v':update.message.photo[-1].file_id})
    elif update.message.video:
        context.user_data['medias'].append({'type':'video','v':update.message.video.file_id})

    if  'detail' not in context.user_data:
        if  update.message.caption and update.message.caption != '':   
            context.user_data['detail']=update.message.caption   

    text = (
        "已收到您的评论"
    )
    await update.message.reply_text(text=text)

    return await notice_ext(update, context)

                         

async def delay_send_media_group(update: Update, context: CallbackContext) -> int:
    text = (
        "已收到文件，请稍候..."
    )
    await update.message.reply_text(text=text)
    await asyncio.sleep(3)  # 等待3秒钟
  
    text = (
        "已收到您的评论"
    )
    await update.message.reply_text(text=text)

    if 'delay_send' in context.user_data:
        del context.user_data['delay_send']

    return await notice_ext(update, context)


async def notice_ext(update: Update, context: CallbackContext):

    if 'media_group_id' in context.user_data:
        del context.user_data['media_group_id']
    keyboard = [
         [InlineKeyboardButton('生成预览', callback_data=CREATE_PRE)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg=await  update.message.reply_text(text='如果您仍有其他图片和视频内容,可继续上传\n若无,可点击[生成预览]查看您的内容', reply_markup=reply_markup)
    context.user_data['notiec_create_pre']=True
    context.user_data['notiec_create_pre_msg']=msg
    return NOTICE_IMG




fields={
    'name':                     '👩‍🦰 ɴɪᴄᴋɴᴀᴍᴇ 昵称:',
    'post_name':                '👦 ᴡɪᴛʜɴᴇss 验证:',
    'contacts':                 '💌 ᴄᴏɴᴛᴀᴄᴛ 通讯:',
    'prices':                    '💵 ᴘʀɪᴄᴇs 价格:',
    'room_desc':                '🏠 ᴇɴᴠɪʀᴏɴᴍᴇɴᴛ 环境:',
    'services':                 '🎁 sᴇʀᴠɪᴄᴇs 服务:',
    'vlaue_face_figure_horny':  '💗 ʟᴏᴏᴋs 颜值/身材/骚值:',
    'full_desc':                '📝 ᴅᴇᴛᴀɪʟ 具体描述:'
}

async def pre_send(update: Update, context: CallbackContext) -> int:
    #print('pre_send')
    query =update.callback_query
    await query.answer()
    medias = []
    #都加上一个logo，已经存到telegram了

    for pair in  context.user_data['medias']:
        #print(pair)
        if pair['type']=='photo':
            medias.append(InputMediaPhoto(media=pair['v']))
        elif pair['type']=='vedio':
            medias.append(InputMediaVideo(media=pair['v']))
        else:pass
    text=fields['name']+ context.user_data['nickname']+'\n'
    if 'post_name_url' in context.user_data:
        text+=fields['post_name']+ context.user_data['post_name_url']+'\n'
    else:
        text+=fields['post_name']+ context.user_data['post_name']+'\n'
    text+=fields['contacts']+ context.user_data['contacts']+'\n'
    text+=fields['prices']+ context.user_data['prices']+'\n'
    if len(context.user_data['room_desc'])>0:
        selected_values = context.user_data['room_desc'].keys()
        value=''
        for v in selected_values:
            value=value+('#'+str(v)+' ')
        text+=fields['room_desc']+ value+'\n'
    if len(context.user_data['services'])>0:
        selected_values = context.user_data['services'].keys()
        value=''
        for v in selected_values:
            value=value+('#'+str(v)+' ')
        text+=fields['services']+ value+'\n'
    text+=fields['vlaue_face_figure_horny']+(
        number_to_emoji(context.user_data['face_value'])+'/ '+
        number_to_emoji(context.user_data['body_value'])+'/ '+
        number_to_emoji(context.user_data['horny_value'])
    )+'\n'
    if  'detail' in context.user_data and     context.user_data['detail']!='':
        text+=fields['full_desc']+'\n\n'+ context.user_data['detail']
    else:
        text+=fields['full_desc']+'\n\n无内容'

    if len(medias)==0:
        new_msg=await query.message.reply_text(text=text,parse_mode=constants.ParseMode.HTML)
    else:
        new_msgs=await query.message.reply_media_group(media=medias,caption=text,parse_mode=constants.ParseMode.HTML)
        new_msg=new_msgs[0]

    keyboard = [
        [InlineKeyboardButton('发布', callback_data=SEND),
        InlineKeyboardButton('放弃', callback_data=REJECT)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await  query.message.reply_text(text='如果您确认无误,请点击发布按键', reply_markup=reply_markup)

    return IF_SEND

async def send(update: Update, context: CallbackContext) -> int:
    query=update.callback_query
    query.answer()

    medias = []
    #都加上一个logo，已经存到telegram了

    for pair in  context.user_data['medias']:
        #print(pair)
        if pair['type']=='photo':
            medias.append(InputMediaPhoto(media=pair['v']))
        elif pair['type']=='vedio':
            medias.append(InputMediaVideo(media=pair['v']))
        else:pass
    text=fields['name']+ context.user_data['nickname']+'\n'
    if 'post_name_url' in context.user_data:
        text+=fields['post_name']+ context.user_data['post_name_url']+'\n'
    else:
        text+=fields['post_name']+ context.user_data['post_name']+'\n'
    text+=fields['contacts']+ context.user_data['contacts']+'\n'
    text+=fields['prices']+ context.user_data['prices']+'\n'
    if len(context.user_data['room_desc'])>0:
        selected_values = context.user_data['room_desc'].keys()
        value=''
        for v in selected_values:
            value=value+('#'+str(v)+' ')
        text+=fields['room_desc']+ value+'\n'
    if len(context.user_data['services'])>0:
        selected_values = context.user_data['services'].keys()
        value=''
        for v in selected_values:
            value=value+('#'+str(v)+' ')
        text+=fields['services']+ value+'\n'
    text+=fields['vlaue_face_figure_horny']+(
        number_to_emoji(context.user_data['face_value'])+'/ '+
        number_to_emoji(context.user_data['body_value'])+'/ '+
        number_to_emoji(context.user_data['horny_value'])
    )+'\n'
    if  'detail' in context.user_data and     context.user_data['detail']!='':
        text+=fields['full_desc']+'\n\n'+ context.user_data['detail']
    else:
        text+=fields['full_desc']+'\n\n无内容'
    
    if len(medias)==0:
        new_msg=await context.bot.sendMessage(
            chat_id=GROUP_ID,
            text=text,
            reply_to_message_id=context.user_data['g_msg_id'],
            parse_mode=constants.ParseMode.HTML)
    else:
        new_msgs=await context.bot.send_media_group(
        chat_id=GROUP_ID,
        caption=text,
        media=medias,
        reply_to_message_id=context.user_data['g_msg_id'],
        parse_mode=constants.ParseMode.HTML
        ) 
        new_msg=new_msgs[0]

    #print(new_msg)
    args= 'meme_'+str(new_msg.message_id)
    args= aes_encrypt(AES_KEY, AES_iv, args)  

    if len(medias)==0:
     new_msg2=   await context.bot.edit_message_text(
                            chat_id=new_msg.chat_id,
                            message_id=new_msg.message_id ,
                            text='<b>'+text+(
                            ' #体验报告\n\n'+
                            '<a href="https://t.me/pc_reporter_bot?start='
                            +args+'">🙈 匿名问答</a></b>'
                            ),parse_mode=constants.ParseMode.HTML
                            )
    else:
      new_msg2=  await context.bot.edit_message_caption(
                            chat_id=new_msg.chat_id,
                            message_id=new_msg.message_id ,
                            caption='<b>'+text+(
                            ' #体验报告\n\n'+
                            '<a href="https://t.me/pc_reporter_bot?start='
                            +args+'">🙈 匿名问答</a></b>'
                            ),parse_mode=constants.ParseMode.HTML
                            )
      
    #------------------------------发送到频道-----------------------------------
    #url="https://t.me/NanningAic/"+str(from_msg_id)+'?comment=1')
    msgs=await context.bot.send_media_group(chat_id=CHANNEL_ID,
                                    reply_to_message_id= context.user_data['c_msg_id'], 
                                    media=medias, 
                                    caption='<b>'+text+(
                            ' #体验报告\n\n'+
                            '<a href="https://t.me/pc_reporter_bot?start='
                            +args+'">🙈 匿名问答</a>  |  <a href="https://t.me/NanningAic/'
                            +str(context.user_data['c_msg_id'])+'?comment=1">💬 普通讨论</a></b>'
                            ),
                                    parse_mode=constants.ParseMode.HTML)  
     
    
    #可能会返回几条消息
    for msg in msgs:
        channel_post_temp_store.add(msg.message_id)


    #------------------------------更新到新信息标记--------------------------------
    await updateNewMsgByThreadId(new_msg2)    
        
    await  query.message.edit_text(text='已发布成功,请您返回频道或群聊查阅')

    context.user_data.clear()

    return ConversationHandler.END

 
 #-------------------删除------------------------




#获取转发到群组的消息
async def getForwardMsg(update: Update, context: CallbackContext) -> int:
         
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
            if from_chat_id ==CHANNEL_ID  and from_msg_id in channel_post_temp_store:                              
                # if   message.caption is not None:
                #     button = InlineKeyboardButton("💬 评论                  >", url="https://t.me/NanningAic/"+str(from_msg_id)+'?comment=1')
                #     # 创建一个 InlineKeyboardMarkup 对象，并将按钮添加到其中
                #     keyboard = InlineKeyboardMarkup([[button]])
                #     await context.bot.editMessageCaption(chat_id=message.chat_id,
                #                                           message_id=message.message_id, 
                #                                            caption=message.text
                #                                             reply_markup=keyboard)

                await  context.bot.deleteMessage(chat_id=message.chat_id, message_id=message.message_id)
                channel_post_temp_store.remove(from_msg_id)
                #await updateNewMsgForce(message)



#更新一个帖子的最大msgid                           
async def updateNewMsgByThreadId(massage):
 
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
        #群组中的发言不处理
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

async def cancel(update: Update, context: CallbackContext) -> int:
 
    text = (
        "OK,您可以继续从频道或群聊中点击[提交体验报告][匿名问答]链接进行操作\n"
    )
    try:
        await update.message.reply_text(text=text)
    except:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(text=text)

    context.user_data.clear()

    return ConversationHandler.END

#不允许别的群添加机器人
async def leaveChat(update: Update, context:  CallbackContext) -> int:
    #print(update.message)
    chat_id=update.message.chat_id
    if chat_id not in LEGAL_GROUP:
       await context.bot.leave_chat(chat_id)


# 定义主函数，创建和启动机器人
def main():
    # 创建机器人实例，并获取Updater
    
    application = Application.builder().token('5833930562:AAFiDSFLt1g6WG9BXcT_Z09UuO1OQkPDxPM').build() 
 
    # 主回调添加多选按钮的回调函数
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        # CHOOSE_IF_ANONYMOUS,NAMED,ANONYMOUS,CONTACT_INPUT,PRICE_INPUT,

        states={
            #---------------------------------------匿名者-------------------------------------------------------
            MEME:[ 
                #这句是意思是文本但非命令
                MessageHandler(filters.TEXT & ~filters.COMMAND, echo_text_meme),
                MessageHandler(filters.PHOTO|filters.VIDEO, echo_media_meme),
              ] ,

            #----------------------------------------报告者---------------------------------------------------------------------
            CHOOSE_IF_ANONYMOUS:[  CallbackQueryHandler(choose_anonymous, pattern="^("+str(NAMED)+'|'+str(ANONYMOUS)+")$"),],
            CONTACT_INPUT:[  MessageHandler(filters.TEXT & ~filters.COMMAND, contact_input),], 
            PRICE_INPUT:[  MessageHandler(filters.TEXT & ~filters.COMMAND, price_input),], 
            VALUE_FACE_INPUT:[ CallbackQueryHandler(value_face_rate, pattern="^\d+$"),], 
            VALUE_BODY_INPUT:[ CallbackQueryHandler(value_body_rate, pattern="^\d+$"),], 
            VALUE_HORNY_INPUT:[ CallbackQueryHandler(room_desc_input, pattern="^\d+$"),], 
            WAIT_ROOM_DESC:[ 
                CallbackQueryHandler(room_checkbox_callback, pattern="^(?!.*"+str(ROOM_SUBMIT)+").*$"),
                CallbackQueryHandler(room_submit, pattern="^"+str(ROOM_SUBMIT)+"$"),                                  
                ],
            WAIT_CHECK_BOX:[
                CallbackQueryHandler(services_checkbox_callback, pattern="^(?!.*"+str(SERVICES_SUBMIT)+").*$"),
                CallbackQueryHandler(services_submit, pattern="^"+str(SERVICES_SUBMIT)+"$"),              
               ],
            DETAIL_INFO: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, echo_text),
                MessageHandler(filters.PHOTO|filters.VIDEO, echo_media),
            ],
            NOTICE_IMG:[
                CallbackQueryHandler(pre_send, pattern="^"+str(CREATE_PRE)+"$"), 
                MessageHandler(filters.PHOTO|filters.VIDEO, echo_media),
            ],
            IF_SEND:[
                CallbackQueryHandler(send, pattern="^"+str(SEND)+"$"), 
                CallbackQueryHandler(cancel, pattern="^"+str(REJECT)+"$"), 
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
                MessageHandler(filters.TEXT & ~filters.COMMAND, echo_text_meme),
                MessageHandler(filters.PHOTO|filters.VIDEO, echo_media_meme),
            ] ,

            
           },
    fallbacks=[CommandHandler("cancel", cancel),CommandHandler("start", start)],
    )


#接入监听
    application.add_handler(conv_handler)
    application.add_handler(conv_handler_create_anymous)

    application.add_handler(
        MessageHandler(
        filters=filters.StatusUpdate.NEW_CHAT_MEMBERS,
        callback=leaveChat
        )
    )

    application.add_handler(
        MessageHandler(
        filters.ChatType.GROUPS &filters.ForwardedFrom(chat_id=CHANNEL_ID) , 
        callback=getForwardMsg
        )    
    )
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