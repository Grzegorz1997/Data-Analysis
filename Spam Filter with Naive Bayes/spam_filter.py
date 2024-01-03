import pandas as pd
import re
import numpy as np
import os

BASE_DIR = os.path.dirname(__file__)
DATA_FILE_PATH = rf"{BASE_DIR}\Data\SMSSpamCollection.csv"

class BayesSpamFilter():
    def __init__(self, file_path:str):
        self.path = file_path
        self.df = pd.read_csv("Data\SMSSpamCollection.csv",sep='\t',header=None,names=['Label', 'SMS'])
        self.output_path = input("Please enter output path in xlsx format")
        
    def divide_dataframe(self):
        self.df["Label"].replace("ham","non-spam",inplace=True)
        randomized_df = self.df.sample(frac=1,random_state=1)
        training_index = round(randomized_df.shape[0] * 0.8)
        
        self.test_df = randomized_df[training_index:].reset_index(drop=True)
        self.training_df = randomized_df[:training_index].reset_index(drop=True)
        self.training_df["SMS list"] = self.training_df["SMS"].replace("\W"," ",regex=True).str.lower().str.split()

    def create_vocabulary(self):
        self.vocabulary =[]
        for row in self.training_df["SMS list"]:
            for element in row:
                self.vocabulary.append(element)
                
        self.vocabulary = list(set(self.vocabulary))
        self.word_counts_per_sms = {unique_word: [0] * len(self.training_df['SMS list']) for unique_word in self.vocabulary}

        for index, sms in enumerate(self.training_df['SMS list']):
            for word in sms:
                self.word_counts_per_sms[word][index] += 1
        self.num_of_vocabulary_words = len(self.vocabulary)
        word_df = pd.DataFrame(self.word_counts_per_sms)
        self.merged_df = pd.concat([self.training_df, word_df], axis=1)

    def create_parameters_dict(self,label:str) -> dict:
        parameters = {}
        labeled_df = self.merged_df[self.merged_df["Label"] == label]
        num_of_words = sum((len(row) for row in labeled_df["SMS list"]))
        probability = len(labeled_df) / len(self.merged_df)
        parameters = {unique_word:0 for unique_word in self.vocabulary}
        laplace_smoothing = 1

        for word in self.vocabulary:
            word_count = labeled_df[word].sum()
            word_probability = (word_count + laplace_smoothing) / (num_of_words + laplace_smoothing * self.num_of_vocabulary_words)
            parameters[word] = word_probability
        return parameters,probability



    def new_message_classification(self,message:str):
        spam_parameters,spam_probability = self.create_parameters_dict("spam")
        no_spam_parameters,no_spam_probability = self.create_parameters_dict("non-spam")
        message = re.sub('\W', ' ', message)
        message = message.lower()
        message = message.split()
        
        p_spam_given_message = spam_probability
        p_no_spam_given_message = no_spam_probability

        for word in message:
            if word in spam_parameters:
                p_spam_given_message *= spam_parameters[word]
            else:
                pass
            if word in no_spam_parameters:
                p_no_spam_given_message *= no_spam_parameters[word]
            else:
                pass
        if p_no_spam_given_message > p_spam_given_message:
            return "non-spam"
        elif p_spam_given_message > p_no_spam_given_message:
            return "spam"
        else:
            return "human assistance"
    
    def perform_spam_filter(self):
        self.test_df['Naive Bayes prediction'] = self.test_df['SMS'].apply(self.new_message_classification)
        self.test_df["Verification"] = np.where(self.test_df["Label"] == self.test_df["Naive Bayes prediction"],1,0)
        self.bayes_accuracy = sum(self.test_df["Verification"] / len(self.test_df))

    def main(self):
        self.divide_dataframe()
        self.create_vocabulary()
        self.create_parameters_dict()
        self.perform_spam_filter()
        print(f"Naive Bayes accuracy for tested dataset is equal to: {str(round(self.bayes_accuracy* 100,2))} %")
        self.test_df.to_excel(self.output_path)
        
if __name__ == "__main__":
    BayesSpamFilter().main()
    print("Done")