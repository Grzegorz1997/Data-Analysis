import pandas as pd
import re
import numpy as np
import os

BASE_DIR = os.path.dirname(__file__)
DATA_FILE_PATH = rf"{BASE_DIR}\Data\SMSSpamCollection.csv"

class NaiveBayesSpamFilter():
    def __init__(self, file_path: str):
        """
        Initialize NaiveBayesSpamFilter object with the provided CSV file path.
        Parameters:
        - file_path: Path to the CSV file containing SMS data.
        """
        self.file_path = file_path
        self.df = pd.read_csv(self.file_path, sep='\t', header=None, names=['Label', 'SMS'])

    def divide_dataframe(self):
        """
        Divide the dataframe into training and test sets.
        The dataset is first randomized using the Pandas sample function with a random seed
        for reproducibility. The training set is then selected as 80% of the randomized dataset.
        """
        self.df["Label"].replace("ham", "non-spam", inplace=True)
        randomized_df = self.df.sample(frac=1, random_state=1)
        training_index = round(randomized_df.shape[0] * 0.8)
        
        self.test_df = randomized_df[training_index:].reset_index(drop=True)
        self.training_df = randomized_df[:training_index].reset_index(drop=True)
        self.training_df["SMS list"] = self.training_df["SMS"].replace("\W", " ", regex=True).str.lower().str.split()

    def create_vocabulary(self):
        """
        Create a vocabulary of unique words and compute word counts per SMS in the training set.
        """
        self.vocabulary = []
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

    def create_parameters_dict(self, label: str) -> tuple:
        """
        Create parameters dictionary and calculate probability for a given label.
        Parameters:
        - label: 'spam' or 'non-spam' for which parameters and probabilities are calculated.
        Returns parameters dictionary and probability for the specified label.
        """
        parameters = {}
        labeled_df = self.merged_df[self.merged_df["Label"] == label]
        num_of_words = sum((len(row) for row in labeled_df["SMS list"]))
        probability = len(labeled_df) / len(self.merged_df)
        parameters = {unique_word: 0 for unique_word in self.vocabulary}
        laplace_smoothing = 1

        for word in self.vocabulary:
            word_count = labeled_df[word].sum()
            word_probability = (word_count + laplace_smoothing) / (num_of_words + laplace_smoothing * self.num_of_vocabulary_words)
            parameters[word] = word_probability
        return parameters, probability

    def return_parameters_probabilities(self):
        """
        Return parameters and probabilities for both 'spam' and 'non-spam' labels.
        """
        self.spam_parameters, self.spam_probability = self.create_parameters_dict("spam")
        self.no_spam_parameters, self.no_spam_probability = self.create_parameters_dict("non-spam")
        
    def new_message_classification(self, message):
        """
        Classify a new message as 'spam' or 'non-spam'.

        Parameters:
        - message: The message to be classified.

        Returns:
        - The predicted class label ('spam', 'non-spam', or 'human assistance').
        """
        message = re.sub('\W', ' ', message)
        message = message.lower()
        message = message.split()

        p_spam_given_message = self.spam_probability
        p_no_spam_given_message = self.no_spam_probability

        for word in message:
            if word in self.spam_parameters:
                p_spam_given_message *= self.spam_parameters[word]
            if word in self.no_spam_parameters:
                p_no_spam_given_message *= self.no_spam_parameters[word]

        if p_no_spam_given_message > p_spam_given_message:
            return "non-spam"
        elif p_spam_given_message > p_no_spam_given_message:
            return "spam"
        else:
            return "human assistance"
        
    def perform_spam_filter(self):
        """
        Perform spam filtering on the test dataset and calculate Naive Bayes accuracy.
        """
        self.test_df['Naive Bayes prediction'] = self.test_df['SMS'].apply(self.new_message_classification)
        self.test_df["Verification"] = np.where(self.test_df["Label"] == self.test_df["Naive Bayes prediction"], 1, 0)
        self.bayes_accuracy = sum(self.test_df["Verification"] / len(self.test_df))

    def main(self):
        """
        Main function to execute the Naive Bayes spam filter analysis.
        """
        self.divide_dataframe()
        self.create_vocabulary()
        self.return_parameters_probabilities()
        self.perform_spam_filter()
        self.test_df.to_clipboard()
        print(f"Naive Bayes accuracy for the tested dataset is equal to: {str(round(self.bayes_accuracy * 100, 2))} %")

NaiveBayesSpamFilter(file_path=DATA_FILE_PATH).main()