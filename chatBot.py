import telebot
from telebot import types
import time
import csv
import requests
#import aiml

TOKEN = ''
url = "http://localhost:5000/parse"

knownUsers = []
userStep = {}

commands = {
              'start': 'Get used to the bot',
              'help': 'Gives you information about the available commands',
              'cancel': 'Cancel conversation with Bot',
              'info': 'help for using bot',
              'getTrafficInfo':'Get Traffic Information'

}

optionSelect = types.ReplyKeyboardMarkup(one_time_keyboard=True)  # create the image selection keyboard
optionSelect.add('Traffic Speed','Incidents','Travel Time')

hideBoard = types.ReplyKeyboardHide()

def get_user_step(uid):
    if uid in userStep:
        return userStep[uid]
    else:
        knownUsers.append(uid)
        userStep[uid] = 0
        print "New user detected, who hasn't used \"/start\" yet"
        return 0


# only used for console output now
def listener(messages):
    """
    When new messages arrive TeleBot will call this function.
    """
    for m in messages:
        if m.content_type == 'text':
            # print the sent message to the console
            print str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text


bot = telebot.TeleBot(TOKEN)
bot.set_update_listener(listener)  # register listener



@bot.message_handler(commands=['start'])
def command_start(m):
    cid = m.chat.id
    if cid not in knownUsers:  # if user hasn't used the "/start" command yet:
        knownUsers.append(cid)  # save user id, so you could brodcast messages to all users of this bot later
        userStep[cid] = 0  # save user id and his current "command level", so he can use the "/getImage" command
        bot.send_message(cid, "Hello, stranger, I don't Know you, let me add you")
        time.sleep(3)
        bot.send_message(cid, "Done, Hello Welcome " + m.chat.first_name )
        command_help(m)  # show the new user the help page
    else:
        bot.send_message(cid, "I already know you, no need for me to scan you again!")

# handle the "/cancel" command
@bot.message_handler(commands=['cancel'])
def command_cancel(m):
    cid = m.chat.id
    bot.send_message(cid, m.chat.first_name + " ,You canceled the conversation,Bye! I hope we can talk again some day." )


# help page
@bot.message_handler(commands=['help'])
def command_help(m):
    cid = m.chat.id
    help_text = "The following commands are available: \n"
    for key in commands:  # generate help text out of the commands dictionary defined at the top
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    bot.send_message(cid, help_text)  # send the generated help page


# help page
@bot.message_handler(commands=['info'])
def info_help(m):
    cid = m.chat.id
    info_text = "Directions of Use: \n 1. Always start with start command at the very first interaction \n 2. Write Destination name and Road name starting with Capital letter, source is fixed to Den Haag \n 3. Traffic flow is number of vehicles that pass a certain point in a certain period of time \n 4. Traffic speed is average speed of vehicles that pass a point in a unit time \n 5. The traffic information is updated per minute, so I provide you the latest information and hope to help you in managing your journey! "
    bot.send_message(cid, info_text)  # send the generated help page

@bot.message_handler(commands=['getTrafficInfo'])
def command_suggest(m):
    cid = m.chat.id
    bot.send_message(cid, "What do you want as traffic information?", reply_markup=optionSelect)  # show the keyboard
    userStep[cid] = 1  # set the user to the next step (expecting a reply in the listener now)

@bot.message_handler(func=lambda message: get_user_step(message.chat.id) == 1)
def msg_option_select(m):
    cid = m.chat.id
    text = m.text

    bot.send_chat_action(cid, 'typing')

    if text == "Traffic Speed":
        bot.send_message(cid, "Please enter your destination", reply_markup=hideBoard)
        userStep[cid] = 0  # reset the users step back to 0
    elif text == "Travel Time":
        bot.send_message(cid, "Please enter your destination", reply_markup=hideBoard)
        userStep[cid] = 0
    elif text == "Incidents":
        bot.send_message(cid,"check this link-")
        bot.send_message(cid,"http://www.planetradiocity.com/international/", reply_markup=hideBoard)
        userStep[cid] = 0
    else:
        bot.send_message(cid, "Please try again")



#if user sends a location
@bot.message_handler(func=lambda message:True, content_types=['location'])
def location_access(m):
    lati= str(float(m.location.latitude))
    longi= str(float(m.location.longitude))
    bot.send_message(m.chat.id,"You have sent a location! Do you want me to provide the traffic speed there?")


@bot.message_handler(regexp='((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)')
def command_url(m):
    bot.send_message(parse_mode='HTML',chat_id=m.chat.id, text='<i> I should not open that url, should I? </i>')


@bot.message_handler(func=lambda message: True, content_types=['text'])
def read_result(m):
    text=m.text
    print text
    chatid=m.chat.id
    currentTime = currentTime = int(time.strftime('%H:%M').split(':')[0])

    querystring = {"q": text}
    headers = {
        'cache-control': "no-cache",
        'postman-token': "4be25fa3-72c0-80e8-eda1-a73b03ad596a"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    resp = response.json()
    intent = response.json()['intent']
    confi = response.json()['confidence']
    txt = response.json()['text']
    print intent, confi,txt
    search = list()
    search1 = list()

    if intent == 'greet':
        if 'hi' in text or 'Hi' in text or 'Hey' in text or 'hey' in text or 'Hello' in text or 'hello' in text:
            if currentTime < 12:
                bot.send_message(m.chat.id, "Hello!Good Morning!")
            if currentTime >= 12 and currentTime < 17 :
                bot.send_message(m.chat.id, "Hello!Good Afternoon!")
            if currentTime >= 17:
                bot.send_message(m.chat.id, "Hello!Good Evening!")
        else:
            bot.send_message(m.chat.id,"How can I help you?")

    elif intent == 'info_speed' and confi>=0.30:
        #bot.send_message(m.chat.id, "I will let you know in a second!")
        for each in resp['entities']:
            search = each['entity']
            search1 = each['value']
            print search, search1

            if 'congestion' in text or 'Congestion'in text or 'flow' in text or 'Flow' in text:
                print "its flow/congestion"
                traffic_flow(text,search,search1,chatid)
            else:
                print "its speed"
                traffic_speed(text,search,search1,chatid)


    elif intent == 'affirm':
        print "affirm"

        #AIML block
        #kernel = aiml.Kernel()
        #kernel.learn("basic_chat.xml")
        #kernel.respond("load aiml b")
        #while True:
        #msg=kernel.respond(text)
        #print kernel.respond(msg)
        if 'yes' in text or 'Yes' in text or 'Yep' in text or 'yep' in text or 'Yeah' in text or 'yeah' in text:
            bot.send_message(m.chat.id,"I am traffic bot!,ask me more")
        elif 'ok' in text or 'Ok' in text or 'OK' in text:
            bot.send_message(m.chat.id,"What information do you want, please check help command!")
        elif 'great' in text or 'good' in text or 'Thanks' in text or "thanks" in text or  'Thank you' in text or 'thank you' in text:
            bot.send_message(m.chat.id,"You are always welcome.")
        elif 'no' in text or 'No' in text or 'NO' in text:
            bot.send_message(m.chat.id,"I am sorry, please try again!")
        else:
            bot.send_message(m.chat.id,"Its always nice to talk to you!")


    elif intent == 'goodbye':
        if 'bye' in text or 'Bye' in text:
            if currentTime < 12:
                bot.send_message(m.chat.id, "Bye Bye! Have a nice ay!")
            if currentTime >= 12 and currentTime < 17 :
                bot.send_message(m.chat.id, "Bye Bye! Have a nice day!")
            if currentTime >= 17:
                bot.send_message(m.chat.id, "Bye Bye! Have a nice evening")
        else:
            bot.send_message(m.chat.id,"Bye Bye!")

    else:
        bot.send_message(m.chat.id, "I am not sure what are you talking about, can you please repeat?")

def traffic_flow(text,search,search1,chatid):
    print "in func traffic_flow"
    if 'destination' in search:
        f = open('converted.csv',
                 'rU')
        csv_f = csv.reader(f)

        # matching intent searched in database
        for row in csv_f:
            if search1 in row[5]:
                print "found!"
                print row[3]
                str = row[3]
        f.seek(0)

        if 'Delft' in search1:
            print "Your path is A12-A4-A13"
            bot.send_message(chatid, "The path is A12-A4-A13")
            for row in csv_f:
                if 'RWS01_MONIBAS_0121hrr0046ra' in row[1] and 'TrafficFlow' in row[2]:
                    flow1 = row[3]
                    if float(flow1) >= 250:
                        flowrate1 = 'fast'
                    if float(flow1) > 100 and float(flow1) < 250:
                        flowrate1 = 'medium'
                    if float(flow1) <= 100:
                        flowrate1 = 'slow'
                    print "speed on A12 is " + flow1
                    bot.send_message(chatid,"Traffic flow on A12 is " + flow1 + " which is " + flowrate1 + " traffic")
            f.seek(0)
            for row in csv_f:
                if 'RWS01_MONIBAS_0040vwx0481ra' in row[1] and 'TrafficFlow' in row[2]:
                    flow2 = row[3]
                    if float(flow2) >= 250:
                        flowrate2 = 'fast'
                    if float(flow2) > 100 and float(flow2) < 250:
                        flowrate2 = 'medium'
                    if float(flow2) <= 100:
                        flowrate2 = 'slow'
                    print "speed on A4 is " + flow2
                    bot.send_message(chatid,"Traffic flow on A4 is " + flow2 + " which is " + flowrate2 + " traffic")
            f.seek(0)
            for row in csv_f:
                if 'RWS01_MONIBAS_0131hrr0064ra' in row[1] and 'TrafficFlow' in row[2]:
                    flow3 = row[3]
                    if float(flow3) >= 250:
                        flowrate3 = 'fast'
                    if float(flow3) > 100 and float(flow3) < 250:
                        flowrate3 = 'medium'
                    if float(flow3) <= 100.0:
                        flowrate3 = 'slow'
                    print "speed on A13 is " + flow3
                    bot.send_message(chatid,"Traffic flow A13 is " + flow3 + " which is " + flowrate3 + " traffic")


        if 'Rotterdam' in search1:
            print "Your path is A12-A4-A13-S112"
            bot.send_message(chatid, "The path is A12-A4-A13-S112")
            for row in csv_f:
                if 'RWS01_MONIBAS_0121hrr0046ra' in row[1] and 'TrafficFlow' in row[2]:
                    flow1 = row[3]
                    if float(flow1) >= 250:
                        flowrate1 = 'fast'
                    if float(flow1) > 100 and float(flow1) < 250:
                        flowrate1 = 'medium'
                    if float(flow1) <= 100:
                        flowrate1 = 'slow'
                    print "speed on A12 is " + flow1
                    bot.send_message(chatid,"Traffic flow A12 is " + flow1 + " which is " + flowrate1 + " traffic")
            f.seek(0)
            for row in csv_f:
                if 'RWS01_MONIBAS_0040vwx0481ra' in row[1] and 'TrafficFlow' in row[2]:
                    flow2 = row[3]
                    if float(flow2) >= 250:
                        flowrate2 = 'fast'
                    if float(flow2) > 100 and float(flow2) < 250:
                        flowrate2 = 'medium'
                    if float(flow2) <= 100:
                        flowrate2 = 'slow'
                    print "speed on A4 is " + flow2
                    bot.send_message(chatid,"Traffic flow on A4 is " + flow2 + " which is " + flowrate2 + " traffic")
            f.seek(0)
            for row in csv_f:
                if 'RWS01_MONIBAS_0131hrr0185ra' in row[1] and 'TrafficFlow' in row[2]:
                    flow3 = row[3]
                    if float(flow3) >= 250:
                        flowrate3 = 'fast'
                    if float(flow3) > 100 and float(flow3) < 250:
                        flowrate3 = 'medium'
                    if float(flow3) <= 100:
                        flowrate3 = 'slow'
                    print "speed on A13 is " + flow3
                    bot.send_message(chatid,"Traffic flow on A13 is " + flow3 + " which is " + flowrate3 + " traffic")

        if 'Amsterdam' in search1:
            print "Your path is A12-A4-A10-S112"
            bot.send_message(chatid, "The path is A12-A4-A10-S112")
            for row in csv_f:
                if 'RWS01_MONIBAS_0121hrr0046ra' in row[1] and 'TrafficFlow' in row[2]:
                    flow1 = row[3]
                    if float(flow1) >= 250:
                        flowrate1 = 'fast'
                    if float(flow1) > 100 and float(flow1) < 250:
                        flowrate1 = 'medium'
                    if float(flow1) <= 100:
                        flowrate1 = 'slow'
                    print "speed on A12 is " + flow1
                    bot.send_message(chatid,"Traffic flow on A12 is " + flow1 + " which is " + flowrate1 + " traffic")
            f.seek(0)
            for row in csv_f:
                if 'RWS01_MONIBAS_0041hrl0225ra' in row[1] and 'TrafficFlow' in row[2]:
                    flow2 = row[3]
                    if float(flow2) >= 250:
                        flowrate2 = 'fast'
                    if float(flow2) > 100 and float(flow2) < 250:
                        flowrate2 = 'medium'
                    if float(flow2) <= 100:
                        flowrate2 = 'slow'
                    print "speed on A4 is " + flow2
                    bot.send_message(chatid,"Traffic flow on A4 is " + flow2 + " which is " + flowrate2 + " traffic")
            f.seek(0)
            for row in csv_f:
                if 'RWS01_MONIBAS_0101hrl0144ra' in row[1] and 'TrafficFlow' in row[2]:
                    flow3 = row[3]
                    if float(flow3) >= 250:
                        flowrate3 = 'fast'
                    if float(flow3) > 100 and float(flow3) < 250:
                        flowrate3 = 'medium'
                    if float(flow3) <= 100:
                        flowrate3 = 'slow'
                    print "speed on A13 is " + flow3
                    bot.send_message(chatid,"Traffic flow on A10 is " + flow3 + " which is " + flowrate3 + " traffic")

    elif 'road' in search:
        print search1
        f = open('converted.csv',
                 'rU')
        csv_f = csv.reader(f)
        for row in csv_f:
            if search1 in row[6] and 'TrafficFlow' in row[2]:
                print row[3]
                flow = row[3]
                if float(flow) >= 250:
                    flowrate = 'fast'
                if float(flow) > 100 and float(flow) < 250:
                    flowrate = 'medium'
                if float(flow) <= 100:
                    flowrate = 'slow'
                str1 = row[6]
                bot.send_message(chatid, "Traffic flow on " + str1 + " is " + flow + " towards " + row[5] + " which is " + flowrate + " traffic")
                # else:
                # bot.send_message(m.chat.id, "Sorry I do not have this information")
        f.seek(0)
    else:
        bot.send_message(chatid, "Sorry, I do not have information about what you asked!")

def traffic_speed(text,search,search1,chatid):
    if 'destination' in search:
        f = open('converted.csv', 'rU')
        csv_f = csv.reader(f)

        # matching intent searched in database
        for row in csv_f:
            if search1 in row[5]:
                print row[3]
                str = row[3]
        f.seek(0)

        if 'Delft' in search1:
            print "Your path is A12-A4-A13"
            bot.send_message(chatid, "A fastest path A12-A4-A13")
            for row in csv_f:
                if 'RWS01_MONIBAS_0121hrr0046ra' in row[1] and 'TrafficSpeed' in row[2]:
                    speed1 = row[3]
                    print "speed on A12 is " + speed1 + ","
                    bot.send_message(chatid, "speed on A12 is " + speed1)
            f.seek(0)
            for row in csv_f:
                if 'RWS01_MONIBAS_0040vwx0481ra' in row[1] and 'TrafficSpeed' in row[2]:
                    speed2 = row[3]
                    print "speed on A4 is " + speed2 + ","
                    bot.send_message(chatid, "speed on A4 is " + speed2)
            f.seek(0)
            for row in csv_f:
                if 'RWS01_MONIBAS_0131hrr0064ra' in row[1] and 'TrafficSpeed' in row[2]:
                    speed3 = row[3]
                    print "speed on A13 is " + speed3
                    bot.send_message(chatid, "speed on A13 is " + speed3)

        if 'Rotterdam' in search1:
            print "Your path is A12-A4-A13-S112"
            bot.send_message(chatid, "A fastest path A12-A4-A13-S112")
            for row in csv_f:
                if 'RWS01_MONIBAS_0121hrr0046ra' in row[1] and 'TrafficSpeed' in row[2]:
                    speed1 = row[3]
                    print "speed on A12 is " + speed1 + ","
                    bot.send_message(chatid, "speed on A12 is " + speed1)
            f.seek(0)
            for row in csv_f:
                if 'RWS01_MONIBAS_0040vwx0481ra' in row[1] and 'TrafficSpeed' in row[2]:
                    speed2 = row[3]
                    print "speed on A4 is " + speed2 + ","
                    bot.send_message(chatid, "speed on A4 is " + speed2)
            f.seek(0)
            for row in csv_f:
                if 'RWS01_MONIBAS_0131hrr0185ra' in row[1] and 'TrafficSpeed' in row[2]:
                    speed3 = row[3]
                    print "speed on A13 is " + speed3
                    bot.send_message(chatid, "speed on A13 is " + speed3)

        if 'Amsterdam' in search1:
            print "Your path is A12-A4-A10-S112"
            bot.send_message(chatid, "A fastest path A12-A4-A10-S112")
            for row in csv_f:
                if 'RWS01_MONIBAS_0121hrr0046ra' in row[1] and 'TrafficSpeed' in row[2]:
                    speed1 = row[3]
                    print "speed on A12 is " + speed1 + ","
                    bot.send_message(chatid, "speed on A12 is" + speed1)
            f.seek(0)
            for row in csv_f:
                if 'RWS01_MONIBAS_0041hrl0225ra' in row[1] and 'TrafficSpeed' in row[2]:
                    speed2 = row[3]
                    print "speed on A4 is " + speed2 + ","
                    bot.send_message(chatid, "speed on A4 is " + speed2)
            f.seek(0)
            for row in csv_f:
                if 'RWS01_MONIBAS_0101hrl0144ra' in row[1] and 'TrafficSpeed' in row[2]:
                    speed3 = row[3]
                    print "speed on A10 is " + speed3
                    bot.send_message(chatid, "speed on A10 is " + speed3)

    elif 'road' in search:
        print search1
        f = open('converted.csv', 'rU')
        csv_f = csv.reader(f)
        for row in csv_f:
            if search1 in row[6] and 'TrafficSpeed' in row[2]:
                print row[3]
                str = row[3]
                str1 = row[6]
                bot.send_message(chatid, "Speed on " + str1 + " is " + str + " towards " + row[5])
        f.seek(0)
    else:
        bot.send_message(chatid,"Sorry, I do not have information about what you asked!")
    #return

while True:
    try:
        bot.polling(none_stop=True)


    except Exception as e:
        time.sleep(15)
