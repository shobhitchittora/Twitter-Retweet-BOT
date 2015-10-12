from termcolor import colored
import tweepy,sys,json,time
import pylru

blacklist = ['I entered to #win','I entered', 'I just entered','I won' , 'I am entering','I\'ve entered','Enter to #win','Enter for your chance','simply click','I\'d love to #win']
whitelist = ['RT &amp; follow','FOLLOW+RETWEET','RT','#RT + #Follow','RT&amp;F', 'Follow &amp; RT','F&amp;RT','Retweet &amp; F','Retweet &amp; Follow', 'RT &amp; Follow','RT + F','#FOLLOW #AND #RETWEET','#F #AND #RT']
follow_term = ['RT &amp; follow','FOLLOW+RETWEET','F + RT','#follow','#RT + #Follow','RT&amp;F', 'Follow &amp; RT','F&amp;RT','Retweet &amp; F','Retweet &amp; Follow', 'RT &amp; Follow','RT + F','#FOLLOW #AND #RETWEET','#F #AND #RT','Follow Me','follow me','Follow me','Follow us']

class TwitterAPI:
    def __init__(self): 
        consumer_key = '' #Enter your cosumer key 
        consumer_secret = '' #Enter your consumer secret
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        access_token = ''  # Enter your access token
        access_token_secret = ''  #Enter your access secret
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

    def tweet(self, message):
        self.api.update_status(status=message)

    def retweet(self, id):
    	self.api.retweet(id)

    def get_status(self , id):
    	return self.api.get_status(id)

    def create_friendship(self,id):
    	self.api.create_friendship(id=id);

    def show_friendship(self,target):
    	return self.api.show_friendship(target_id=target)

    def me(self):
    	return self.api.me()

twitter = TwitterAPI()
file=open('./data.txt','a')
cache = pylru.lrucache(size=50)
cache.clear()

def pass_filter(status):
	line = status.text.encode('utf8')
	if line[0]!='@':
		if any(x not in line for x in blacklist) and any(x in line for x in whitelist):
			return True
	return False

def if_follow_req(status):
	id = status.user.id_str
	#myself = twitter.me()
	if any(x in status.text.encode('utf8') for x in follow_term):
		lst = twitter.show_friendship(id)
		#print colored(str(lst[1].followed_by) ,'red' )
		return not lst[1].followed_by
	else:
		return False

class MyStreamListner(tweepy.StreamListener):
	'''
	def on_data(self,data):
		decoded = json.loads(data)
		print data

		#print '@%s: %s' % (decoded['user']['screen_name'], decoded['text'].encode('ascii', 'ignore'))
        print ''
		#print '-----------------------------------------------------------------------'
	
	'''
	def on_status(self,status):
		if not hasattr(status, 'retweeted_status'):
			print colored("Original Tweet",'green')
			print "Id :" + status.id_str;
			if (not status.retweeted) and (status.id_str not in cache):
				try:
					if pass_filter(status):
						twitter.retweet(id=status.id_str);
						cache[status.id_str] = True;
						print colored("Retweet Successful!" ,'green')
						if if_follow_req(status):
							print colored('Follow req','yellow')
							u_id = status.user.id
							print colored('user' + str(u_id),'blue')
							twitter.create_friendship(u_id)
							print colored('Followed the User!','green')
						else: print colored('No follow required','yellow')
						file.write("\n"+str(time.asctime( time.localtime(time.time()))) + "\n" + status.text.encode('utf8') +"\n") 
					else:
						print colored('Filtered','red')
				except tweepy.error.TweepError as err:
					print err
			else: print colored('Cache Hit','blue')		
				
		else:
			print colored("Not Original",'green')
			print "Parent Id :" + status.retweeted_status.id_str
			id = status.retweeted_status.id_str
			parent_status = twitter.get_status(id =id)
			if (not parent_status.retweeted) and (id not in cache):
				try:
					if pass_filter(status) and status.retweeted_status.retweet_count > 25:
						print "RT count:" + str(status.retweeted_status.retweet_count)
						twitter.retweet(id = id)
						cache[id] = True;
						print colored("Retweet Successful!" ,'green')
						if if_follow_req(parent_status):
							print colored('Follow req','yellow')
							u_id = parent_status.user.id
							print colored(u_id,'blue')
							twitter.create_friendship(u_id)
							print colored('Followed the User!','green')
						else: print colored('No follow required','yellow')
						file.write("\n"+str(time.asctime( time.localtime(time.time()))) + "\n" + status.text.encode('utf8') +"\n") 
					else:
						print colored('Filtered','red')
				except tweepy.error.TweepError as err:
					print err
			else: print colored('Cache Hit','blue')
					

					
		print status.text.encode('utf8')
		print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
		

	def on_error(self,status_code):
		if status_code == 420:
			return False;
try:
	if __name__ == "__main__":
		#twitter = TwitterAPI()
		#twitter.tweet("I'm posting a tweet,yet again!")
		myStreamListner = MyStreamListner()
		myStream = tweepy.Stream(auth=twitter.api.auth, listener=myStreamListner)

		#myStream.filter(track=['#CSGOgiveaway','#CSGOSkins','#CSGOgiveaway #CSGO','#csgo #CSGOgiveaway'])
		myStream.filter(track=['#giveaway','#Giveaway'])
except KeyboardInterrupt:
	sys.exit()
