from h2o_wave import Q, site, app, ui, main

import tweepy
import json
import operator
import itertools
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

config = {
    'access_token'  : '955862386388344832-7ZYvXCkpyFO6Pbhh93Od4O94E5ga1t4', 
    'access_token_secret' : 'OfRg3O4SnrOinda7VeOTjfIBfWe9uzmRJd5IBEsQOdvvl', 
    'api_key' : 'c3QdMOOWQFHTsI28Yu3HGjwkO', 
    'api_secret_key' : 'V1FwzrxBzr7aYQNeqQf4s6D1oBapwpIVNtSkceJOXtnLKemAOS'}

auth = tweepy.OAuthHandler(config['api_key'], config['api_secret_key']) 
auth.set_access_token(config['access_token'], config['access_token_secret'])

analyser = SentimentIntensityAnalyzer()

api = tweepy.API(auth)

api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

def texts(tag):
    tws = {}
    texts = []
    cc = 0
    # for tweet in api.search(q=tag, lang="en", rpp=100).items(MAX_TWEETS):
    for tweet in tweepy.Cursor(api.search, q=tag, lang="en", rpp=100).items(15):
        if (not tweet.retweeted) and cc < 25: # and ('RT @' not in tweet.text):
            texts.append(tweet.text)
            cc = cc+1
        else:
            break
    
    texts = list(set(texts))
    for t in texts:
        score = analyser.polarity_scores(t)
        sc = score.copy()
        sc.pop('compound', None)
        if sc['pos'] < sc['neg']:
            m = 'neg'
        else:
            m = 'pos'
        mm = {'neu': 'Neutral', 'pos': 'Postive', 'neg': 'Negative'}
        tws[t] = (mm[m], sc)
    return (tws, texts)


@app('/')
async def serve(q: Q):
    if not q.client.initalized:
        q.args.text = 'trump'
        q.args.search = True
        q.client.initalized = True

    q.page.add("search_tab", ui.form_card(box='1 1 9 1', items=[
        ui.textbox(name='text', 
        label='', 
        placeholder='#h2oai',
        value=q.args.text, multiline=False, trigger=False)] ) )

    q.page.add("search_click", ui.form_card(box='10 1 1 1', items=[
        # ui.Buttons(
            ui.button(name="search", label="search", primary=True) ] ) )
    
    if q.args.search:
        q.user.text = q.args.text
        values, text = texts(q.user.text)

        cc = 0

        boxes =[' '.join(i) for i in list(itertools.product(['2','4','6', '8', '10'], ['1','4', '7'] ))]
        for t in text:
            print(t)
            val = values[t]
            if val[0] == 'Negative':
                color = '$red'
            elif val[0] == 'Positive':
                color = '$blue'
            else:
                color='$green'

            j, i = boxes[cc].split(' ')
            q.page.add(f'example_{i}_{j}', ui.large_bar_stat_card(
                box=f'{i} {j} 3 2',
                title=f'Sentiment - {val[0]}',
                value='={{intl foo minimum_fraction_digits=2 maximum_fraction_digits=2}}',
                value_caption='Negative',
                aux_value='={{intl bar minimum_fraction_digits=2 maximum_fraction_digits=2}}',
                aux_value_caption='Positive',
                plot_color=color,
                progress=1,
                data=dict(foo=val[1]['neg'], bar=val[1]['pos']),
                caption=t,
            ))
            cc=cc+1

    await q.page.save()
