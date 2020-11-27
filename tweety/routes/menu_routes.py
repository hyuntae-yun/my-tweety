from flask import Flask, render_template, request,redirect,Blueprint
from embedding_as_service_client import EmbeddingClient
import os
from dotenv import load_dotenv
from tweety.models import db,User,Tweet
import tweepy #=> pip install tweepy
import pickle
from sklearn.linear_model import LogisticRegression

MODEL_PATH ="./tweety.pkl"

def train_model(X,y):
    classifier = LogisticRegression()
    classifier.fit(X, y)
    return classifier

def save_model(model):
    with open(MODEL_PATH,"wb") as file:
        pickle.dump(model,file)

def load_model():
    with open(MODEL_PATH,"rb") as file:
        loaded_model = pickle.load(file)
    return loaded_model



menu_routes = Blueprint('menu_routes', __name__)


load_dotenv()
API_KEY=os.getenv('TWITTER_API_KEY')
API_KEY_SECRET=os.getenv('TWITTER_API_KEY_SECRET')
ACCESS_TOKEN=os.getenv('TWITTER_ACCESS_TOKEN')
ACCESS_TOKEN_SECRET=os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
#tweety와 연결
auth=tweepy.OAuthHandler(API_KEY,API_KEY_SECRET)
auth.set_access_token(ACCESS_TOKEN,ACCESS_TOKEN_SECRET)
api=tweepy.API(auth)

DATAPATH = os.path.join(os.path.dirname(__file__), "models",
                          "tweety_all.pkl")

en = EmbeddingClient(host='54.180.124.154', port=8989)


# User 목록을 보여준다.
@menu_routes.route('/users', methods=['GET', 'POST'])
def users(user_name=None,data=None):
    data=User.query.all()
    return render_template('user.html',user_name=user_name,data=data)

# User을 저장한다.
@menu_routes.route('/<user_name>/add',methods=['GET','POST'])
def add(user_name=None):
    
    if user_name == None :
        return redirect("/")
    if request.method =='POST':
        user = api.get_user(screen_name=user_name)
        n_user = User(id=user.id,username=user_name,screenname=user.name , followers_count=user.followers_count)
        db.session.add(n_user)
        db.session.commit()
        tweet_list=[]
        
        public_tweets=api.user_timeline(id=n_user.id,include_rts=False, exclude_replies=True,tweet_mode="extended", count=300)
        for twt in public_tweets:
            new_tweet=Tweet(id=twt.id ,text=twt.full_text,user_id=n_user.id,embedding=en.encode(texts=[twt.full_text])[0])
            db.session.add(new_tweet)
            db.session.commit()
        return redirect("/")
        
    return render_template('add.html',username=user_name)

#User의 tweeter 목록을 보여준다.
@menu_routes.route('/<user_name>/get',methods=['GET','POST'])
def get(user_name):
    if request.method =='GET':
        d_user=User.query.filter_by( username=user_name).first()
        data=Tweet.query.filter_by(user_id=d_user.id).all()
        return render_template('get.html',username=user_name,data=data)
    return render_template('get.html',username=user_name,data=data)

#User을 삭제한다.
@menu_routes.route('/<user_name>/delete',methods=['GET','POST'])
def delete(user_name):
    if request.method =='POST':
        d_user=User.query.filter_by( username=user_name).first()
        data=Tweet.query.filter_by(user_id=d_user.id).all()
        for da in data:
            db.session.delete(da)
        db.session.delete(d_user)
        db.session.commit()
        return redirect("/")
    return render_template('delete.html',username=user_name)


@menu_routes.route('/update',methods=['GET','POST'])
def update(username=None,change_val=None,data=None):
    if request.method=='GET':
        data = User.query.all()
        return render_template('update.html',username=None,change_val=None,data=data)
    if request.method=='POST':
        if request.form['uname']!="" or request.form['uname']!=None:
            username=request.form['uname']
        if request.form['change_val']!="" or request.form['change_val']!=None:
            change_val=request.form['change_val']
        val=int(request.form.get('column'))
        print(username)
        print(change_val)
        print(val)
        if val == 1:
            user = User.query.filter_by(username=username).update({'username' :change_val})
            db.session.commit()
        elif val == 3 :
            user = User.query.filter_by(username=username).update({'followers_count' : int(change_val)})
            db.session.commit()
        elif val == 2 :
            user = User.query.filter_by(username=username).update({'screenname' :change_val})
            db.session.commit()
        data = User.query.all()
        return render_template('update.html',username=username,change_val=change_val,data=data)

def append_to_with_label(to_arr, from_arr, label_arr, label): # X <-tweets y<-tweets.em  
    for item in from_arr:
        to_arr.append(item)
        label_arr.append(label)


@menu_routes.route('/compare',methods=['GET','POST'])
def compare(words=None,data=None,pred_result=None):
    data = User.query.all()
    X=[]
    y=[]
    if request.method=='POST': 
        user1=int(request.form.get('user_id1'))
        user2=int(request.form.get('user_id2'))
        words=request.form['word']
        ut1=Tweet.query.filter_by(user_id=data[user1-1].id).all()
        ut2=Tweet.query.filter_by(user_id=data[user2-1].id).all()
        for item in ut1:
            X.append(item.embedding)
            y.append(data[user1-1].username)
        for item in ut2:
            X.append(item.embedding)
            y.append(data[user2-1].username)
        if user1 == user2 :
            pred_result='Cannot compare same user'
        else:
            if os.path.isfile(MODEL_PATH):
                classifier =pickle.load(open('tweety.pkl','rb'))                
            else:
                classifier=train_model(X,y)
                pickle.dump(classifier,open('tweety.pkl','wb'))

            pred_val = en.encode(texts=[words])
            pred_result = classifier.predict(pred_val)[0]
            pred_reslt1 = data[user2-1].username

            if data[user2-1].username == pred_result :
                pred_reslt1=data[user1-1].username

            pred_result=""" {} will  use the word '{}' more than {}.""".format(pred_result,words,pred_reslt1)
        return render_template('compare.html',words=words,data=data,pred_result=pred_result)
    return render_template('compare.html',words=None,data=data,pred_result=None)
    
