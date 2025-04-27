
# -*- coding: utf-8 -*-
"""

Original file is located at
    https://colab.research.google.com/drive/1T4ny2RJTwtGLz6BscA_os66R-oEnjpTh

#Text summarization

There are two methods of text summarization :

1.   Extractive summarization
2.   Abstractive summarization

##Extractive summarization
For the extractive summarization, first i use the graph bassed method (like : TextRank) and second i use the ML method (like : svm)

###1. Extractive text summarization using graph method

Requiered packages
"""

# !pip install spaCy
# !python -m spacy download en_core_web_lg
# !pip install pytextrank
# !pip install evaluate
# !pip install rouge_score

import spacy
import pytextrank
import nltk
import numpy as np
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer

nltk.download('punkt')
nltk.download('punkt_tab')

class Text_summarization:
    def __init__(self,text_without_summarization: str,number_sentence:int):
        self.text_without_summarization = text_without_summarization
        self.number_sentence = number_sentence

    async def summarizer_using_textrank_algorithm(self):
        try:
            """Load the language model and add to the pipe of textrank"""
            mlp = spacy.load('en_core_web_lg')
            mlp.add_pipe('textrank')

            """Summarization"""

            """upload the un-summarized text into the model"""
            first_step = mlp(self.text_without_summarization)

            """for storing the summarized text"""
            summarized_text = ""

            """summarization"""
            for i in first_step._.textrank.summary(limit_phrases=self.number_sentence, limit_sentences=self.number_sentence):
                summarized_text += str(i)

            # """Evaluation : using spacy"""
            #
            # """load the summarized and target text in the spacy"""
            # summarizer_text_model = mlp(summarized_text)
            # target_text_model = mlp(self.target_text)
            #
            # """finding similarities between the targeted text and summarized text"""
            # result = summarizer_text_model.similarity(target_text_model)

            return self.text_without_summarization, summarized_text
        except:
            return self.text_without_summarization, 'Try_again', 0


    """###Extractive summarization  using ML method
    
    Required liraries
    """

    # !pip install nltk
    # !pip install sklearn


    async def summarizer_using_SVM(self):
        try:
            mlp = spacy.load('en_core_web_lg')
            """Divide into individual sentence"""

            sent = nltk.sent_tokenize(self.text_without_summarization)

            """Feature extraction"""

            f = TfidfVectorizer()
            X = f.fit_transform(sent)

            """training data nd testing data"""

            Y = [1 if len(sentence) > 100 else 0 for i, sentence in enumerate(sent)]

            x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.2)

            """Modeling"""

            model = SVC(kernel='linear')
            model.fit(x_train, y_train)

            """predicting important scores of all sentence"""

            scores = model.decision_function(X)
            scores

            """Ranked sentence by score"""

            ranked_senteces = sorted(zip(scores, sent), reverse=True)

            """Select top ranked sentence and Summary function"""

            top_ranked_senteces = [sentence for score, sentence in ranked_senteces[:self.number_sentence]]
            summary = " ".join(top_ranked_senteces)

            # """Evaluation"""
            #
            # # load the summarized and target text in the spacy
            # s_text = mlp(summary)
            # t_text = mlp(self.target_text)
            #
            # # finding similarities between the targeted text and summarized text
            # accuracy = s_text.similarity(t_text)

            return self.text_without_summarization,summary
        except:
            return self.text_without_summarization, "Try again", 0

    async def summarizer_using_Happyface_transform(self):
        """##Abstractive summarization

        For the abstractive summarization, i use the hugging face tranforms.

        ####Required libraires
        """

        # !pip install transformers
        # !pip install pegasus

        from transformers import AutoTokenizer,AutoModelForSeq2SeqLM

        """###load the pretrained model"""

        model_name = "t5-base"
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

        """###Tokenization and encoding the input"""

        input = tokenizer(self.text_without_summarization,return_tensors='pt')
        input

        """###Generate the summary using the hugging face transform"""

        summary_ids = model.generate(**input,max_length=self.number_sentence)
        summary = tokenizer.decode(summary_ids[0],skip_special_tokens=True)
        return self.text_without_summarization,summary

