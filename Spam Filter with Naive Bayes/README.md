## Project Description:

# In this project, I'm creating a spam filter for SMS messages using the multinomial Naive Bayes algorithm. Aim is to achieve over 80% accuracy in classifying new messages as spam or non-spam. I will train the algorithm on a dataset of 5,572 SMS messages already labeled by humans, available from the UCI Machine Learning Repository by Tiago A. Almeida and José María Gómez Hidalgo. Success will be determined by the filter's ability to accurately categorize incoming messages.
# - This script implements a Naive Bayes spam filter for classifying SMS messages as 'spam' or 'non-spam'.
# - It uses Laplace smoothing for probability calculations and trains on a provided dataset.
# - The accuracy of the Naive Bayes classifier is printed at the end of the execution.

## How to Run

1. **Prerequisites:**
   - Ensure that you have Python installed on your machine.
   - Install required libraries using the following command:
     ```bash
     pip install pandas numpy
     ```
2. **Clone the Repository:**
   - Clone or download this repository to your local machine.

3. **Run the Script:**
   - Execute the following command to run the script:
     ```bash
    python naive_bayes_spam_filter.py
     ```

**Note:** Adjust the file paths and names according to your setup. Ensure that the dataset file (`SMSSpamCollection.csv`) is in the same directory as the script.

## Additional Information

- The dataset is first randomized using the Pandas `sample` function with a random seed (`random_state=1`) for reproducibility.
- The accuracy of the Naive Bayes classifier is printed at the end of the execution.
Feel free to explore and modify the script based on your requirements.