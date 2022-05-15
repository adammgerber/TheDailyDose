import urllib.request
from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import re
import spacy
import pandas as pd
import re
from deep_translator import GoogleTranslator
import genanki

url = 'https://www.dw.com/ru/vojna-ukraina-rossija-11-maja-2/a-61758257'

html = urllib.request.urlopen(url)

htmlParse = BeautifulSoup(html, 'html.parser')

#NLP machine learning library for picking out POS/lemma
nlp = spacy.load('ru_core_news_lg')
nlp.max_length = 2000000

total_words = []

for para in htmlParse.find_all("p"):
    p = para.get_text()
    #get rid of non-alpha characters
    regex = re.compile('[^a-zA-Z\ЁёА-я\-ÀàÂâÆæÇçÈèÉéÊêËëÎîÏïÔôŒœÙùÛûÜü]')
    s= re.sub(regex, ' ', p)


    document= nlp(s)

    #ADD WORDS TO LIST IF PART OF SPEECH IS A VERB/NOUN/ADJ
    verbs = [token.lemma_ for token in document if token.pos_ == 'VERB']
    nouns = [token.lemma_ for token in document if token.pos_ == 'NOUN']
    adjs = [token.lemma_ for token in document if token.pos_ == 'ADJ']

    words = verbs + nouns+ adjs
    total_words+= words



#remove all empty lists within the list
total_verbs = [x for x in total_words if x]

#convert list to dataframe
df = pd.DataFrame(total_verbs, columns=['Russian'])

#add an 'English' column to the dataframe with translations of original Russian words
df['English'] = df['Russian'].apply(GoogleTranslator(source='auto', target='en').translate)


##### ANKI CARDS ######


style = """
.card {
 font-family: times;
 font-size: 30px;
 text-align: center;
 color: black;
 background-color: white;
}

.card1 { background-color:Lavender }
"""



model_id = 12
deck_id = 5
my_model = genanki.Model(
  model_id,
  'Vocab',
  fields=[
    {'name': 'Russian'},
    {'name': 'English'},
  ],
  templates=[
    {
      'name': 'Card 1',
      'qfmt': '{{Russian}}',
      'afmt': '{{FrontSide}}<hr id="answer">{{English}}',
    }
  ], css = style
)

my_deck = genanki.Deck(deck_id, "Vocab")
for index, row in df.iterrows():
        card = genanki.Note(model = my_model,
        fields = [
                row['Russian'],row['English']
                ])
        my_deck.add_note(card)


genanki.Package(my_deck).write_to_file('DailyDoseRussian.apkg')

