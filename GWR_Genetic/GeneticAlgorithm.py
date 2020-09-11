import numpy as np
import time
from sklearn.model_selection import cross_val_score, KFold
from sklearn.metrics import accuracy_score, r2_score
from sklearn.decomposition import PCA
from random import *
import matplotlib.pyplot as plt

class FeatureSelectionGeneticAlgorithm():
    # Initialize state, setting up:
    #    + mutation rate - Number controlling the chance of mutation (between 0 - 1)
    #    + iterations - Controls the number of generations the algorithm will create 
    #    + pool_size - Population that the algorithm will consider in each generations
    def __init__(self, mutation_rate = 0.05, iterations = 100, pool_size = 50):
        self.mutation_rate = mutation_rate
        self.iterations = iterations
        self.pool_size = pool_size
        self.pool = np.array([])
        self.iterations_results = {}
        self.r2_li = []
        self.r2_adj = []
        self.kf = KFold(n_splits = 5)

    def fit(self, model, _type, X, y, cv = True, pca = False):
        # model = sci-kit learn regression/classification model
        # X = X input data
        # y = Y output data corresponding to X
        # cv = True/False for cross-validation
        # pca = True/False for principal component analysis

        self.__init__(self.mutation_rate, self.iterations, self.pool_size)

        is_array = False
        # Catching whether or not the user will be using a numpy array or pandas dataframe
        try:
            X = np.array(X)
            is_array = True
        except:
            pass
        # Create a random pool of solutions using numpy array filled with 1s and 0s to the length of how many features are selected
        #Uncomment this block to allow the pool to be made up with a finite number of 1s set by counter
        ###BLOCK START
        num_array = []
        for i in range(0, self.pool_size):
            count = 0;
            #arry = np.zeros(X.shape[1])
            arry = [0]*X.shape[1]
            counter = randint(3,5)
            for j in range(0, len(arry)):
                rand_num = randint(0,1)
                arry[j] = rand_num
                if rand_num == 1:
                    count +=1
                if count == counter:
                    break
            num_array.append(arry)
        self.pool = np.array(num_array)
        ###BLOCK END
        #Uncomment this to allow the pool to have 
        #self.pool = np.random.randint(0,2,(self.pool_size, X.shape[1]))
        

        for iteration in range(1,self.iterations+1):
            s_t = time.time()
            scores = list()
            fitness = list()
            # For each chromosome it scans to see which features should be selected by looking at the genes. It uses those to generate a adjusted dataset with the features seleceted as columns
            for chromosome in self.pool:
                chosen_idx = [idx for gene, idx in zip(chromosome, range(X.shape[1])) if gene == 1]
            
                if is_array == True:
                    adj_X = X[:, chosen_idx]
                else:
                    adj_X = X.iloc[:, chosen_idx]
                    pca == False
                # If Principal Component Analysis (PCA) is used then it will apply it to all the columns of the adujsted dataset. Then selected the number of features that should be transformed ensuring at least 99% of variance is captured in the transformation
                # (Makes sure that a lot of information is not lost when attempting to reduce the effects of dimensionality)
                if pca == True:
                    adj_X = PCA(n_components = np.where(np.cumsum(PCA(n_components=adj_X.shape[1]).fit(adj_X).explained_variance_ratio_)>0.99)[0][0]+1).fit_transform(adj_X)
                # Program will then score the model fitted to the adjusted dataset
                #
                # This part may be re-written to work with our GWR program. Use adjusted R-squared or try to penalize 
                #
                # Cross Validation (cv) (using K-Fold cross-validation with K = 5) will make sure that the dataset does not overfit (The average of the 5 scores will be returned 
                #    For regression models, they will base the score off the r-square value 
                if _type == 'regression':
                    if cv == True:
                        r2 = np.mean(cross_val_score(model, adj_X, y, scoring='r2', cv=self.kf))
                        #Calculating R2 adjusted for score
                        score = 1-(((1-r2)*(y.shape[0]-1))/(y.shape[0]-len(chosen_idx)-1))
                        self.r2_li.append(r2)
                        self.r2_adj.append(score)
                    else:
                        r2 = r2_score(y, model.fit(adj_X,y).predict(adj_X))
                        self.r2_li.append(r2)
                        score = 1-(((1-r2)*(y.shape[0]-1))/(y.shape[0]-len(chosen_idx)-1))
                        self.r2_adj.append(score)
                        
                #    For classification models, the score is based off the accuracy
                elif _type == 'classification':
                    if cv == True:
                        score = np.mean(cross_val_score(model, adj_X, y, scoring='accuracy', cv=self.kf))
                    else:
                        score = accuracy_score(y, model.fit(adj_X,y).predict(adj_X))

                scores.append(score)
            #if(sum(scores) == 0):
            #    fitness = [0 for x in scores]
            #else:
            fitness = [x/sum(scores) for x in scores]
            fitness, self.pool, scores = (list(t) for t in zip(*sorted(zip(fitness, [list(l) for l in list(self.pool)], scores), reverse=True)))
            # Store the results in a dictionary
            self.iterations_results['{}'.format(iteration)] = dict()
            self.iterations_results['{}'.format(iteration)]['fitness'] = fitness
            self.iterations_results['{}'.format(iteration)]['pool'] = self.pool
            self.iterations_results['{}'.format(iteration)]['scores'] = scores
            self.pool = np.array(self.pool)

            # Reproducing the best solutions to use in the new pool
            if iteration != self.iterations+1:
                new_pool = []
                # Gets rid of the bottom half of solutions that scored badly then reproduces with the best solutions from the pool
                for chromosome in self.pool[1:int((len(self.pool)/2)+1)]:
                    random_split_point = np.random.randint(1, len(chromosome))
                    # New generations are created by randomly selecting a point along the pair of chromosomes and swapping the genes beyond that point 
                    next_gen1 = np.concatenate((self.pool[0][:random_split_point], chromosome[random_split_point:]), axis = 0)
                    next_gen2 = np.concatenate((chromosome[:random_split_point], self.pool[0][random_split_point:]), axis = 0)
                    # Following reproduction the genes have a random chance of being mutated (switching from 0 to 1 or 1 to 0)
                    for idx, gene in enumerate(next_gen1):
                        if np.random.random() < self.mutation_rate:
                            next_gen1[idx] = 1 if gene == 0 else 0
                    for idx, gene in enumerate(next_gen2):
                        if np.random.random() < self.mutation_rate:
                            next_gen2[idx] = 1 if gene == 0 else 0
                    # New pool is genearted to be scored again
                    new_pool.append(next_gen1)
                    new_pool.append(next_gen2)
                self.pool = new_pool
            else:
                continue
            if iteration % 10 == 0:
                e_t = time.time()
                print('Iteration {} Complete [Time taken for last iteration: {} Seconds]'.format(iteration, round(e_t-s_t,2)))

    # Functions to display the infromation from the algorithm
    def results(self, X):
        names = list()
        for idx, gene in enumerate(self.pool[0]): 
            if gene == 1:
                names.append(X.columns.values[idx])
        # Returns the optimal solution from the pool of solutions as a tuple. First part of tuple is array of gene sequence and second is list of indexes that should selected to reflect gene sequence (gene/feature = 1)
        return (self.pool[0], [idx for idx, gene in enumerate(self.pool[0]) if gene == 1]), names

    def plot_progress(self):
        avs = [np.mean(self.iterations_results[str(x)]['scores']) for x in range(1,101)]
        avs0 = [np.mean(self.iterations_results[str(x)]['scores'][0]) for x in range(1,101)]
        plt.plot(avs, label='Pool Average Score')
        plt.plot(avs0, label='Best Solution Score')
        plt.ylabel('R-square')
        plt.xlabel('Generation')
        plt.title('Genetic Algorithm Score')
        plt.legend()
        plt.show()
    
    def plot_r2(self):
        #avs = [np.mean(self.r2_li) for x in range(1, 101)]
        #avs0 = [np.mean(self.r2_adj) for x in range(1, 101)]
        plt.plot(self.r2_li, label="R2")
        plt.plot(self.r2_adj, label="R2Adj")
        plt.legend()
        plt.show()