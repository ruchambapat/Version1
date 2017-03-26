import telebot
from telebot import types
import time
import csv
import requests
import sys
import geocoder

sys.setrecursionlimit(100000)
#print limit
#import aiml


#Tokens
# old token RMB bot: 233174191:AAFgwu11WhSh1xvBIVaWlW84VHibS_aO5Hw
# token rmbak bot: 346717713:AAEYGT22JiJ9x0ORkULtrieyWQGwhWc23cA
TOKEN = '313305206:AAGl_YjPd512zqfnx5J58D7FqNWstElLtiY'
url = "http://localhost:5000/parse"
#gmaps = googlemaps.Client(key='AIzaSyDqItGt0yCKJK8dFYkzxzTHe_C6ZFLnPAI')


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
optionSelect.add('Traffic Flow','Incidents','Travel Time')

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

    if text == "Traffic Flow":
        bot.send_message(cid, "Please enter your destination/road", reply_markup=hideBoard)
        global msgid
        global chtext
        msgid=m.message_id
        chtext=m.text
        print msgid,chtext
        userStep[cid] = 0  # reset the users step back to 0
    elif text == "Incidents":
        bot.send_message(cid, "Send your location", reply_markup=hideBoard)
        global messageid
        global chat_text
        chat_text=m.text
        messageid= m.message_id
        print messageid
        print chat_text
        userStep[cid] = 0
    elif text == "Travel Time":
        bot.send_message(cid,"check this link-")
        bot.send_message(cid,"http://www.planetradiocity.com/international/", reply_markup=hideBoard)
        userStep[cid] = 0
    else:
        bot.send_message(cid, "Please try again")

#if user sends a location
@bot.message_handler(func=lambda message:True, content_types=['location'])
def location_access(m):
    print "in location"
    chatid= m.chat.id
    mid= m.message_id
    print mid
    yes= mid-2
    print yes
    print "printed yes"
    lati = m.location.latitude
    longi = m.location.longitude
    print lati, longi
    # bot.send_message(chatid, "You are at :Let me provide you the traffic flow at ")
    geo = geocoder.google([lati, longi], method='reverse')
    city = geo.city
    print city

    if yes == messageid:
        print "in if"
        print "they are same"
        # lati = str(float(m.location.latitude))
        # longi = str(float(m.location.longitude))
        send_incident_info(city, chatid)
    else:
        print "in else"
        bot.send_message(chatid, "You are at "+ city+ " Let me provide you the traffic flow at " + city )
        traffic_flow_location(city, chatid)
        send_incident_info(city, chatid)



@bot.message_handler(regexp='((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)')
def command_url(m):
    bot.send_message(parse_mode='HTML',chat_id=m.chat.id, text='<i> I should not open that url, should I? </i>')


@bot.message_handler(func=lambda message: True, content_types=['text'])
def read_result(m):
    destinations=['Delft','Rotterdam','Amsterdam','delft','amsterdam','rotterdam']
    global roads
    roads=['A4','A13','A12','A10']
    text=m.text
    chatid=m.chat.id
    print text
    if text in destinations:
        search='destination'
        search1=text
        traffic_flow(text, search, search1, chatid)
    elif text in roads:
        search='road'
        search1=text
        traffic_flow(text, search, search1, chatid)
    else:

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

            if not search:
                print "empty search"
                mark =0
                for d,r in zip(destinations,roads):
                    print "in lists"
                    if d in text:
                        print "in d"
                        search = 'destination'
                        search1 = d
                        if 'congestion' in text or 'Congestion'in text or 'flow' in text or 'Flow' in text:
                            traffic_flow(text, search, search1, chatid)
                            mark=1
                        else:
                            traffic_speed(text, search, search1, chatid)
                            mark=1
                    elif r in text:
                        print "in r"
                        search = 'road'
                        search1 = r
                        if 'congestion' in text or 'Congestion' in text or 'flow' in text or 'Flow' in text:
                            traffic_flow(text, search, search1, chatid)
                            mark=1
                        else:
                            traffic_speed(text, search, search1, chatid)
                            mark=1
                if mark == 1:
                    bot.send_message(chatid, "Ask me more!")
                else:
                    bot.send_message(chatid, "Sorry, I do not have information about what you asked!")


            elif 'congestion' in text or 'Congestion'in text or 'flow' in text or 'Flow' in text:
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
                    bot.send_message(m.chat.id, "Bye Bye! Have a nice day!")
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
        f = open('convertedtrafficinfo.csv','rU')
        csv_f = csv.reader(f)

        # matching intent searched in database
        for row in csv_f:
            if search1 in row[5]:
                #print "found!"
                print row[3]
                str = row[3]
        f.seek(0)

        if 'Delft' in search1 or 'Delft' in text or 'delft' in text:
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
                    #print "speed on A12 is " + flow1
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
                    #print "speed on A4 is " + flow2
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
                    #print "speed on A13 is " + flow3
                    bot.send_message(chatid,"Traffic flow A13 is " + flow3 + " which is " + flowrate3 + " traffic")


        elif 'Rotterdam' in search1 or 'Rotterdam' in text or 'rotterdam' in text:
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
                    #print "speed on A12 is " + flow1
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
                    #print "speed on A4 is " + flow2
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
                    #print "speed on A13 is " + flow3
                    bot.send_message(chatid,"Traffic flow on A13 is " + flow3 + " which is " + flowrate3 + " traffic")

        elif 'Amsterdam' in search1 or 'Amsterdam' in text or 'amsterdam' in 'text':
            print "Your path is s100-A12-A4-A10"
            bot.send_message(chatid, "The path is s100-A12-A4-A10")
            for row in csv_f:
                if 'RWS01_MONIBAS_0121hrr0046ra' in row[1] and 'TrafficFlow' in row[2]:
                    flow1 = row[3]
                    if float(flow1) >= 250:
                        flowrate1 = 'fast'
                    if float(flow1) > 100 and float(flow1) < 250:
                        flowrate1 = 'medium'
                    if float(flow1) <= 100:
                        flowrate1 = 'slow'
                    #print "speed on A12 is " + flow1
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
                    #print "speed on A4 is " + flow2
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
                    #print "speed on A13 is " + flow3
                    bot.send_message(chatid,"Traffic flow on A10 is " + flow3 + " which is " + flowrate3 + " traffic")
        else:
            bot.send_message(chatid, "I do not have information for the destination you asked!")

    elif 'road' in search:
        print "in road"
        print search1
        f = open('convertedtrafficinfo.csv','rU')
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
            else:
                bot.send_message(chatid, "I do not have information for the road you asked!")
                # else:
                # bot.send_message(m.chat.id, "Sorry I do not have this information")
        f.seek(0)
    else:
        print "could not find"
        bot.send_message(chatid, "Sorry, I do not have information about what you asked!")

def traffic_speed(text,search,search1,chatid):
    print "in func traffic speed"
    if 'destination' in search:
        f = open('convertedtrafficinfo.csv', 'rU')
        csv_f = csv.reader(f)

        # matching intent searched in database
        for row in csv_f:
            if search1 in row[5]:
                print row[3]
                str = row[3]
        f.seek(0)

        if 'Delft' in search1 or 'Delft' in text or 'delft' in text:
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

        elif 'Rotterdam' in search1 or 'Rotterdam' in text or 'rotterdam' in text:
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

        elif 'Amsterdam' in search1 or 'Amsterdam' in text or 'amsterdam' in text:
            print "Your path is s100-A12-A4-A10"
            bot.send_message(chatid, "A fastest path s100-A12-A4-A10")
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
        else:
            bot.send_message(chatid, "I do not have information for the destination you asked!")


    elif 'road' in search:
        print "in road"
        print search1
        f = open('convertedtrafficinfo.csv', 'rU')
        csv_f = csv.reader(f)
        for row in csv_f:
            if search1 in row[6] and 'TrafficSpeed' in row[2]:
                print row[3]
                str = row[3]
                str1 = row[6]
                bot.send_message(chatid, "Speed on " + str1 + " is " + str + " towards " + row[5])
            else:
                bot.send_message(chatid, "I do not have information for the road you asked!")
        f.seek(0)
    else:
        bot.send_message(chatid,"Sorry, I do not have information about what you asked!")
    #return

def traffic_flow_location(city, chatid):
    #print "in function"
    f = open('convertedtrafficinfo.csv', 'rU')
    csv_f = csv.reader(f)

    # matching intent searched in database
    for row in csv_f:
        if city in row[5]:
            #print "found"
            print row[3]
            str = row[3]
    f.seek(0)

    if city == 'Delft':
        bot.send_message(chatid,"Highways connected towards Delft are A12 A4 A13")
        for row in csv_f:
            if 'RWS01_MONIBAS_0121hrr0046ra' in row[1] and 'TrafficFlow' in row[2]:
                flow1 = row[3]
                if float(flow1) >= 250:
                    flowrate1 = 'fast'
                if float(flow1) > 100 and float(flow1) < 250:
                    flowrate1 = 'medium'
                if float(flow1) <= 100:
                    flowrate1 = 'slow'
                #print "speed on A12 is " + flow1
                bot.send_message(chatid, "Traffic flow on A12 is " + flow1 + " which is " + flowrate1 + " traffic")
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
                #print "speed on A4 is " + flow2
                bot.send_message(chatid, "Traffic flow on A4 is " + flow2 + " which is " + flowrate2 + " traffic")
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
                #print "speed on A13 is " + flow3
                bot.send_message(chatid, "Traffic flow A13 is " + flow3 + " which is " + flowrate3 + " traffic")

    elif city == 'Rotterdam':
        bot.send_message(chatid, "Highways connected towards Rotterdam are A12 A4 A13 S112")
        for row in csv_f:
            if 'RWS01_MONIBAS_0121hrr0046ra' in row[1] and 'TrafficFlow' in row[2]:
                flow1 = row[3]
                if float(flow1) >= 250:
                    flowrate1 = 'fast'
                if float(flow1) > 100 and float(flow1) < 250:
                    flowrate1 = 'medium'
                if float(flow1) <= 100:
                    flowrate1 = 'slow'
                #print "speed on A12 is " + flow1
                bot.send_message(chatid, "Traffic flow A12 is " + flow1 + " which is " + flowrate1 + " traffic")
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
                #print "speed on A4 is " + flow2
                bot.send_message(chatid, "Traffic flow on A4 is " + flow2 + " which is " + flowrate2 + " traffic")
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
                #print "speed on A13 is " + flow3
                bot.send_message(chatid, "Traffic flow on A13 is " + flow3 + " which is " + flowrate3 + " traffic")

    elif city == 'Amsterdam':
        bot.send_message(chatid, "Highways connected towards Amsterdam are s100 A12 A4 A10 ")
        for row in csv_f:
            if 'RWS01_MONIBAS_0121hrr0046ra' in row[1] and 'TrafficFlow' in row[2]:
                flow1 = row[3]
                if float(flow1) >= 250:
                    flowrate1 = 'fast'
                if float(flow1) > 100 and float(flow1) < 250:
                    flowrate1 = 'medium'
                if float(flow1) <= 100:
                    flowrate1 = 'slow'
                #print "speed on A12 is " + flow1
                bot.send_message(chatid, "Traffic flow on A12 is " + flow1 + " which is " + flowrate1 + " traffic")
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
                #print "speed on A4 is " + flow2
                bot.send_message(chatid, "Traffic flow on A4 is " + flow2 + " which is " + flowrate2 + " traffic")
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
                #print "speed on A13 is " + flow3
                bot.send_message(chatid, "Traffic flow on A10 is " + flow3 + " which is " + flowrate3 + " traffic")
    else:
        bot.send_message(chatid,"Sorry I do not have traffic information for the location you sent!")

def send_incident_info(city,chatid):
    print "in inci"
    f = open('incidents.csv', 'rU')
    csv_f = csv.reader(f)
    flag =0
    print "file open"
    for row in csv_f:
        if city in row[5]:
            print "found"
            incident = row[4]
            time = row[1]
            subtime= time[12:17]
            print incident,subtime
            bot.send_message(chatid,"You are at "+ city+ " and "+ incident +" has happened in the city at time "+subtime)
            #bot.send_message(chatid,"Traffic flow may be slower due to this!")
            flag= 1
        else:
            print "not found"
    #f.seek(0)
    if flag == 1:
        bot.send_message(chatid, "Traffic flow may be slower due to this!")
    else:
        bot.send_message(chatid, "No incident has happened near you!")

while True:
    try:
        bot.polling(none_stop=True)

    except Exception as e:
        time.sleep(15)
