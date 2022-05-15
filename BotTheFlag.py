from functools import total_ordering
from http import client
from pydoc import cli
from re import T
from xml.etree.ElementTree import tostring
import configparser
import tweepy
import time
import flag
import operator

CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_KEY = ''
ACCESS_SECRET = ''
BEARER_TOKEN = ''

auth=tweepy.OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY,ACCESS_SECRET)
api=tweepy.API(auth)
config = configparser.ConfigParser()
config.read("config.ini")
client = tweepy.Client(bearer_token=BEARER_TOKEN,
                           consumer_key=CONSUMER_KEY,
                           consumer_secret=CONSUMER_SECRET,
                           access_token=ACCESS_KEY,
                           access_token_secret=ACCESS_SECRET)

def split(word): #split the word into a list of character
    return [char for char in word]

def get_all_index(list,word): #return the index of all the word in the list
    indices = []
    for index in range(len(list)):
        if list[index] == word:
            indices.append(index)
    return indices

def is_flag_emoji(c): #return true if c is a flag emoji
    return "\U0001F1E6\U0001F1E8" <= c <= "\U0001F1FF\U0001F1FC" or c in ["\U0001F3F4\U000e0067\U000e0062\U000e0065\U000e006e\U000e0067\U000e007f", "\U0001F3F4\U000e0067\U000e0062\U000e0073\U000e0063\U000e0074\U000e007f", "\U0001F3F4\U000e0067\U000e0062\U000e0077\U000e006c\U000e0073\U000e007f"]

def get_mention_id(api,since_id):
    try:
        mentions=api.mentions_timeline(count=10,since_id=since_id)       
    except:
        mentions=[]
        print("Too many Request timeline")
    reply_ids=[]
    usernames=[]
    mentions_id=[]
    not_analyse=[]
    text=[]
    for i in range(len(mentions)):
        if mentions[i].in_reply_to_status_id is not None:
            print(mentions[i])
            if "analyse ce tweet" in mentions[i].text or "analyses ce tweet" in mentions[i].text:
                reply_ids.append(mentions[i].in_reply_to_status_id)
                usernames.append(mentions[i].user.screen_name)
                mentions_id.append(mentions[i].id)
            else:
                not_analyse.append(mentions[i].id)
                since_id=max(not_analyse)+1
                print(since_id)
            
    if len(mentions)>0:
        if mentions_id:
            print(mentions_id)
            since_id=max(mentions_id)+1
    return mentions_id,usernames,reply_ids,since_id 

def get_likers_flags(api,tweet_id) :
    paginator=0
    paginator1=1
    total_users=[]
    too_many=0
    try:
        while paginator!=paginator1 and len(total_users)<2700:
            if paginator==0:
                users=client.get_liking_users(id=tweet_id)
            else:
                users=client.get_liking_users(id=tweet_id,pagination_token=paginator,user_fields='description')
            paginator=users[3]['next_token']
            total_users=total_users+users[0]
            
            print(users)
    except:
        print("Too many Request")
        too_many=1
    
    flags=[]

    try:   
        nbr_likes=len(total_users)
        print("Nbr likes : "+str(nbr_likes))
    

        for i in range(len(total_users)):
            caracters=total_users[i].name.split()
            print(caracters)
            for c in range(len(caracters)):
                if not flag.dflagize(caracters[c])==flag.flagize(caracters[c]):
                    if len(caracters[c])==2:
                        if caracters[c]==flag.flagize(":CP:") or caracters[c]==flag.flagize(":MF:"):
                            flags.append(flag.flagize(":FR:"))
                        else:
                            flags.append(caracters[c])
                    else:
                        a=flag.dflagize(caracters[c])
                        a=split(a)
                        print(a)
                        index=get_all_index(a,":")
                        print(index)
                        for j in index:
                            try:
                                if a[j]==a[j+3]:
                                    if a[j+1]=='C' and a[j+2]=='P':
                                        a[j+1]='F'
                                        a[j+2]='R'
                                        print("".join(a[j:j+4]))
                                        print(flag.flagize("".join(a[j:j+4])))
                                    if a[j+1]=='M' and a[j+2]=='F':
                                        a[j+1]='F'
                                        a[j+2]='R'
                                        print("".join(a[j:j+4]))
                                        print(flag.flagize("".join(a[j:j+4])))
                                    if a[j+1]=='U' and a[j+2]=='M':
                                        a[j+1]='U'
                                        a[j+2]='S'
                                        print("".join(a[j:j+4]))
                                        print(flag.flagize("".join(a[j:j+4])))
                                    if is_flag_emoji(flag.flagize("".join(a[j:j+4]))):
                                        flags.append(flag.flagize("".join(a[j:j+4])))
                            except:
                                continue
    except:
        nbr_likes=0
        print("except nbr_likes")               
                    
    drapeau=[]
    nbr_drapeau=[]
    try:
        for i in range(len(flags)):
            if not flags[i] in drapeau:
                drapeau.append(flags[i])
                nbr_drapeau.append(flags.count(flags[i]))
    except:
        pass
    enumerate_drapeau = enumerate(nbr_drapeau)
    sorted_drapeau = sorted(enumerate_drapeau, key=operator.itemgetter(1)) #sort the list of drapeau by number of likes
    sorted_indices = [index for index, element in sorted_drapeau] #get the indices of the sorted drapeau
    drapeau_sort=[]
    nbr_drapeau_sort=[]
    for i in reversed(sorted_indices):
        drapeau_sort.append(drapeau[i])
        nbr_drapeau_sort.append(nbr_drapeau[i])
    return drapeau_sort,nbr_drapeau_sort,nbr_likes,too_many
            

 

def main():
    reply_ids=[]
    usernames=[]
    flags=[]
    nbr_flags=[]
    mentions_id=[]
    nbr_likes=0
    config.read("config.ini")
    since_id=int(config["GENERAL"]['since_id'])
    text=""
    
    while True:
        reply_ids=[]
        usernames=[]
        too_many=0
        mentions_id,usernames,reply_ids,max_since_id=get_mention_id(api,since_id) 
        if reply_ids:
            print('reply_ids=')
            print(reply_ids)
        if max_since_id>since_id:
            since_id=max(max_since_id,since_id)
            for i in range(len(reply_ids)):
                flags,nbr_flags,nbr_likes,too_many=get_likers_flags(api,reply_ids[i])
                text=""
                if nbr_likes>0:
                    if not flags:
                        response="Aucun drapeau dans "+str(nbr_likes)+" noms ayant likés"
                    else:  
                        for j in range(len(flags)):
                           text=text+flags[j]+" :"+ str(nbr_flags[j])+","
                        text=text[:-1]  
                        response="Nbr de drapeaux dans "+str(nbr_likes)+" noms ayant likés:\n"+text
                        if len(response)>=280:
                            response=response[:279]
                        
                    print(text)
                    try:
                        api.update_status(status=response,in_reply_to_status_id=mentions_id[i],auto_populate_reply_metadata=True)
                        client.like(mentions_id[i])
                    except:
                        print("tweet error")
                        api.update_status(status="Api trop sollicité par les restrictions Twitter, essayez plus tard",in_reply_to_status_id=mentions_id[i],auto_populate_reply_metadata=True)
                    since_id=since_id+1
                    print("since id="+str(since_id))
                else:
                    if too_many==1:
                        print("Too many request")
                        try:
                            api.update_status(status="@"+usernames[i]+" Bot trop solicité, Réessayez dans 10-15min",in_reply_to_status_id=mentions_id[i],auto_populate_reply_metadata=True)
                        except:
                            print("tweet error")
                    else:
                        print("pas de likes")
                        try:
                            api.update_status(status="@"+usernames[i]+" il n'y a pas de likes",in_reply_to_status_id=mentions_id[i],auto_populate_reply_metadata=True)
                        except:
                            print("tweet error")
        else:
            print("max_id<since_id= "+str(max_since_id))
        config.set("GENERAL",'since_id',str(since_id))
        with open("config.ini", 'w') as configfile:
            config.write(configfile)
        time.sleep(30) 
    

if __name__ == "__main__":
    main()
