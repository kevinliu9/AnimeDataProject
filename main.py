import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
#class to represent the anime itself
class Anime(object):
    #constructor to initialize an anime with its name
    def __init__(self, animeName):
      self.name = animeName
      self.totalScore = 0
      self.scoreList = list()
      self.attributeList = list()
    
    #accessor and modifier to set specific info of an anime into a list
    #Best Girl, Best Guy, Best Quote, and Best Scene are categories w/ specific info
    def setAttribute(self, attribute):
      self.attributeList.append(attribute)
    def getAttribute(self, index):
        return self.attributeList[index]
    
    def getAllAttributes(self):
        return self.attributeList
        
    #accessor and modifier methods for calculation and presentation of total score
    def getScore(self, index):
      return self.scoreList[index]
    def getScoreList(self):
      return self.scoreList
    def addScore(self, score):
      self.scoreList.append(score)
      self.totalScore = self.totalScore + score
    def getTotalScore(self):
      return self.totalScore

    def updateRanking(self, ranking):
      self.rank = ranking
    def getRanking(self):
      return self.rank

    def getName(self):
      return self.name
    #function to override operator<
    def __lt__(self, other):
      return (self.getTotalScore() < other.getTotalScore()) or\
      (self.getTotalScore() == other.getTotalScore() and\
       self.getName() < other.getName()) 

#function to take a string in the format (Anime, Specific information)
#will return a tuple that splits the string into its name and important information
def substring(string):
    animeName = string[:string.find('(')].strip()
    animeAttribute = string[string.find('(') + 1:string.find(')')].strip()
    return (animeName, animeAttribute)
     
#main method
if __name__ == "__main__":
    #use the panda library to open up the tab separated value dataset
    animeData = pd.read_csv("Anime List.tsv", sep = '\t')
    headers = animeData.iloc[0]

    #Creates a DataFrame object that eliminates unnecessary rows
    adjusted_anime_data  = pd.DataFrame(animeData.values[1:24], columns=headers)

    #Drop columns that are completely blank space
    adjusted_anime_data.columns = adjusted_anime_data.columns.fillna('to_drop_c')
    adjusted_anime_data.drop('to_drop_c', axis = 1, inplace = True)
    adjusted_anime_data = adjusted_anime_data.iloc[1:]

    #Create an anime dictionary, (key, value) = (Anime name, Anime class object)
    anime_dict = dict()

    #General frame of the dataset:
    #There are 22 animes ranked best to worst on 8 categories
    #Program reads in the data and assign the scores based on position in the dataset
    #Total scores will be internally summed in the class object and used for comparison
    
    #scoreCounter starts from the number of rows, 22
    scoreCounter = adjusted_anime_data.shape[0] 
    for col in adjusted_anime_data.columns: #loop through each column/category
      for anime in adjusted_anime_data[col]: #loop through anime in the category

        #an anime contains important info if there are ordered parentheses inside
        if(anime.find('(') != -1 and anime.find(')') != -1 and\
           anime.find('(') < anime.find(')')):

          #if the anime is already in the dictionary, do nothing
          #else add in the entry accordingly
          if (substring(anime)[0] in anime_dict.keys()):
              pass
          else:
              anime_dict[substring(anime)[0]] = Anime(substring(anime)[0])

          #Special cases: Unavailable specific information leads to a score of 0
          #Otherwise, add in the corresponding score for the anime
          if(substring(anime)[1] == "Unavailable" or substring(anime)[1] == "???"):
            anime_dict[substring(anime)[0]].addScore(0)
          else:
            anime_dict[substring(anime)[0]].addScore(scoreCounter)

          #add in the specific information to the anime object
          anime_dict[substring(anime)[0]].setAttribute(substring(anime)[1])

        #else if there is no specific information, follow same algorithm described above
        else:
          if anime in anime_dict.keys():
              pass
          else:
              anime_dict[anime] = Anime(anime)

          #update anime's score
          anime_dict[anime].addScore(scoreCounter)

        #score counter decreases by 1 for every element traversing downwards
        scoreCounter = scoreCounter - 1

      #reset the score counter after every column traversal
      scoreCounter = adjusted_anime_data.shape[0]
   
    #create the list of ranked anime 
    sorted_anime_list = list()
    for anime in anime_dict:
      sorted_anime_list.append(anime_dict[anime])
    #sort according to the algorithm used overriding _lt_ operator
    sorted_anime_list.sort(reverse=True)
    #assign rankings to all the animes as one of their private member variables
    rank = 1
    for anime in sorted_anime_list:
      anime.updateRanking(rank)
      rank = rank + 1
    #create a dictionary for all the total scores for all animes
    anime_scores = {"Anime Names": [anime.getName() for anime in sorted_anime_list],\
     "Scores": [anime.getTotalScore() for anime in sorted_anime_list]}
    #create a DataFrame containing all the animes and their scores
    df = pd.DataFrame(anime_scores)
    df.index = [i for i in range(1, df.shape[0] + 1)]
    
    #anime_score_breakdown is another dictionary for all the scores of all animes
    anime_score_breakdown =\
     {"Anime Names": [anime.getName() for anime in sorted_anime_list],\
      "Score List": [anime.getScoreList() for anime in sorted_anime_list]}
    #create another DataFrame to lay out all the total scores for each anime
    anime_score_breakdown_df = pd.DataFrame(anime_score_breakdown)
    anime_score_breakdown_df["Ranking"] = [i for i in range(1, df.shape[0] + 1)]
    anime_score_breakdown_df.set_index("Ranking", inplace=True)
    #lay out all the data inside the score breakdown DataFrame
    counter = 0
    for col in adjusted_anime_data.columns:
      anime_score_breakdown_df[col] =\
      [anime.getScoreList()[counter] for anime in sorted_anime_list]
      counter = counter + 1
    anime_score_breakdown_df.drop(['Score List'], axis = 1, inplace = True)
    #redefine df so it now includes the rankings and total score
    df = df.join(anime_score_breakdown_df, rsuffix='_other') 
    df.drop(['Anime Names_other'], axis = 1, inplace = True)
    df["Ranking"] = df.index
    df.set_index("Ranking", inplace = True)
    #create first figure, set axes 
    fig = plt.figure(1)
    ax = fig.add_axes([0,0,1,1])
    #anime names will be on the x axis, total score -> y axis
    anime_names = list(df["Anime Names"])
    total_scores = list(df["Scores"])
    #set the bars to yellow and bar edges to black
    ax.bar(anime_names,total_scores, color='y', edgecolor = 'Black')
    #set graph aesthetics
    ax.set_ylabel('Total Score', fontsize=20)
    ax.set_xlabel('Anime Name', fontsize=20)
    ax.set_title('Animes watched and total scores', fontsize=32)
    plt.setp(ax.get_xticklabels(), rotation=45, horizontalalignment='right') 
    ax.set_facecolor((0, 0, 0))
    #sList defines the total scores for each rank
    sList = df['Scores']
    #create the printout of the statistical data on the next plot
    txt = "Min Score: " + str(np.array(sList).min().round(2)) + "\n"
    txt = txt + "First Quartile: " + str(round(np.percentile(sList, 25), 2)) + "\n"
    txt = txt + "Median: " + str(round(sList.median(), 2)) + "\n"
    txt = txt + "Third Quartile: " + str(round(np.percentile(sList, 75), 2)) + "\n"
    txt = txt + "Max Score: " + str(np.array(sList).max().round(2)) + "\n"
    txt = txt + "Mean: " + str(np.array(sList).mean().round(2)) + "\n"
    txt = txt + "Standard Deviation: " + str(np.array(sList).std().round(2))
    fig2 = plt.figure(2) #create second figure, set axes
    ax2 = fig2.add_axes([0,0,1,1])
    #set aesthetics of the graph
    ax2.set_xlabel('Total Score', fontsize=20)
    ax2.set_title('Box plot demonstrating distribution of total scores',\
                  fontsize=32)
    #create the boxplot
    bPlot = plt.boxplot(df["Scores"], vert=False, patch_artist=True)
    #set aesthetics for all the boxes in the bar chart
    for box in bPlot['boxes']:
      box.set(color='black', linewidth=2)
      box.set(facecolor = 'yellow')
    fig2.text(.025, .7, txt, ha='left')
    ax2.set_facecolor((0.53, 0.81, 0.92))
    #show both graphs
    plt.show()
