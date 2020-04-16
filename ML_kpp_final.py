#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr  8 23:09:13 2020

@author: elvinagovendasamy
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  7 16:18:44 2020

@author: elvinagovendasamy
"""

import pandas as pd
import numpy as np
import random
import math
import matplotlib.pyplot as plt
from sklearn import datasets
import numpy.random as npr
from copy import deepcopy
from sklearn.cluster import KMeans
import seaborn as sns
from scipy import spatial
from time import time
from sklearn.base import TransformerMixin



def distance_squared(x,y):
    return spatial.distance.cdist(x,y,'sqeuclidean')

def kpp_init(k,X):
    #print(X.shape)
    sample,features=X.shape
    
    """On choisit un nombre d'essaie en ce basant sur les textes/ recherches internet"""
    """ATTENTION: L'utilisation des essaies ne sont pas représentés dans la preuve mathématique mais mentionné dans le texte, nous pourrons l'ajouter comme moyen d'amélioration additionnel"""
    number_trials=2+int(np.log(k)) 
    # Reference:
        # https://github.com/scikit-learn/scikit-learn/pull/99/commits/35ad5ea9ec6dccad6a257a36efba0073f9d83ba2?diff=unified&w=1
        # Conclusion de : https://theory.stanford.edu/~sergei/papers/kMeansPP-soda.pdf
        
    """On crée le premier centre, obtenu aléatoirement de nos observations """
    centers=np.empty((k,features))
    rand=npr.randint(0,sample)
    # le premier centre
    centers[0]=X.iloc[rand,:]
    
    """On obtient les distances de ce premier centre"""
    dist=distance_squared(np.atleast_2d(centers[0]), X)
    #Verification de la premiere distance:  print(np.sum(centres[0]-X.iloc[0,:])**2))
    dist_total=np.sum(dist)
    dist_cumul=np.cumsum(dist)
    
    """ On choisi les prochains centres (k-1 restants) en utilisant la probabilité proportionelle à la distance euclidienne au carré"""
    for c in range(1,k):
        # Nous créons 'number_trials'(ici 3) nombres de probabilité, la somme n'étant pas égale à 1.
        random_proba=npr.random(number_trials)
        random_value=random_proba*dist_total
        # On trouve l'indice des observations correspondant au random_value
        candidate_ids=np.searchsorted(dist_cumul,random_value)
        
        # Calculer la distance entre ces candidats et les observations
        dist_candidate=distance_squared(np.atleast_2d(X.iloc[candidate_ids,:]),X)
        #Verification de la premiere distance: print(np.sum((X.iloc[54,:]-X.iloc[0,:])**2))
        
        # Choisir le meilleur candidat parmis les 'number_trials' essaies
        # Choisir la distance minimale entre: 
                # la distance(1er centre et X), et
                # la distance(k-1 centres restants, pour chaque essaie, et X)
        
        best_candidate=None
        best_total_dist=None
        best_dist=None
        
        dist=np.minimum(dist_candidate[0],dist)
        """ MANQUE ACTUALISATION """
        
        
        for essaie in range(1,number_trials):
            new_dist=np.minimum(dist_candidate[essaie],dist)
            new_total_dist=np.sum(new_dist)
            
        # On garde la plus petite distance et le candidat qui y correspond
            if (best_candidate is None) or (new_total_dist<best_total_dist):
                best_candidate=candidate_ids[essaie]
                best_total_dist=new_total_dist
                best_dist=new_dist
                
        # On stock les centres et les distances minimum
        centers[c]=X.iloc[best_candidate]
        
        dist_total=best_total_dist
        dist=best_dist
    #print(centers)   
    return centers
            

def kpp_init_notrials(k,X):
    """On crée le premier centre, obtenu aléatoirement de nos observations """
    
    sample,features=X.shape

    centers=np.empty((k,features))
    rand=npr.randint(0,sample)
    # le premier centre
    centers[0]=X.iloc[rand,:]
    
    """On obtient les distances de ce premier centre"""
    dist=distance_squared(np.atleast_2d(centers[0]), X)
    #Verification de la premiere distance:  print(np.sum(centres[0]-X.iloc[0,:])**2))
    dist_total=np.sum(dist)
    dist_cumul=np.cumsum(dist)
    
    """ On choisi les prochains centres (k-1 restants) en utilisant la probabilité proportionelle à la distance euclidienne au carré"""
    for c in range(1,k):
        random_proba=npr.random() # pas d'essaie dans ce cas, nous n'avons qu'une seule probabilité aléatoire
        random_value=random_proba*dist_total
        # On trouve l'indice de l'observation correspondant au random_value
        candidate_id=np.searchsorted(dist_cumul,random_value)
        
        # Calculer la distance entre le candidat et les observations
        dist_candidate=distance_squared(np.atleast_2d(X.iloc[candidate_id,:]),X)
        
        # On calcule la distance minimale entre la distance du candidat et la distance du premier centre
        new_dist=np.minimum(dist_candidate,dist)
        new_total_dist=np.sum(new_dist)
        
        
        # On stock les centres et les distances minimum
        centers[c]=X.iloc[candidate_id]
        
        dist_total=new_total_dist
        dist=new_dist
    return centers
            


def random_init(k,X):
    
    sample,features=X.shape[0],X.shape[1]
    
    centers=np.empty((k,features))
    """ ENREGISTRER LES RANDS POUR PAS REPETER LES CENTRES """
    for i in range(k):
        rand=npr.randint(0,sample)
        centers[i]=X.iloc[rand]
    
    return centers
        


def lloyd(k,X,e,centers):          
    
    """
    k: clusters
    X: datapoints, in the form of a dataframe
    e: by default 10**(-10)
    initial_centers: determined by one of the initialisation algorithms
    """
    sample,features=X.shape
    
    
    error=e+1 # On initialise l'erreur: nombre aléatoire > 0
    SSE=[]
    sse=0
    sum_distance=0
    # Assignation des centres
    while error>e:
        distances=np.empty((sample,k))
        #sse=np.empty((sample,k))
        clusters=np.empty(features)

        for i in range(k):
            distances[:,i]=distance_squared(np.atleast_2d(centers[i]),X)

        #Verification de la premiere distance: 
#        print('verification:',np.sum((centers[0]-X.iloc[0,:])**2))
#        print(distances)
            
        # Les clusters sont formés à partir des candidats ayant les distances minimales
        clusters=np.argmin(distances,axis=1)

        # Mise a jour des centres
        new_centers=deepcopy(centers)
        for i in range(k):
            new_centers[i,:]=np.mean(X.iloc[clusters==i],axis=0)

        error=np.linalg.norm(centers-new_centers)
        
        centers=deepcopy(new_centers)
        
        """ prendre les points DANS le cluster """
        #sse=distance_squared(np.atleast_2d(centers),X)

        for i in range(k):
            sum_distance+=np.sum(sse)

    return [centers,clusters,sum_distance]
   
def kmean_sklearn(k,X):
    k_means = KMeans(n_clusters=k)
    k_means.fit(X)
    
    centers = k_means.cluster_centers_
    labels=k_means.fit_predict(X)
    inertia=k_means.inertia_
    
    return [centers,labels,inertia]
    

def plot_data_all(k,X,e):
    
    init_kpp=kpp_init(k,X)
    init_random=random_init(k,X)
    init_kpp_notrials=kpp_init_notrials(k,X)
    
    #init_all=["init_kpp","init_random","init_kpp_notrials"]

    clusters_kpp=lloyd(k,X,e,init_kpp)[1]
    clusters_random=lloyd(k,X,e,init_random)[1]
    clusters_kpp_notrials=lloyd(k,X,e,init_kpp_notrials)[1]
    clusters_sklearn=kmean_sklearn(k,X)[1]
    

    centers_kpp=lloyd(k,X,e,init_kpp)[0]
    centers_random=lloyd(k,X,e,init_random)[0]
    centers_kpp_notrials=lloyd(k,X,e,init_kpp_notrials)[0]
    centers_sklearn=kmean_sklearn(k,X)[0]
    
    
    # plotting 
    fig, ax = plt.subplots(2, 2,figsize=(5, 5))
    
    ax[0,0].scatter(X.iloc[:,1],X.iloc[:,3],c=clusters_kpp,s=7,cmap='viridis')
    ax[1,0].scatter(X.iloc[:,1],X.iloc[:,3],c=clusters_random,s=7,cmap='viridis')
    ax[0,1].scatter(X.iloc[:,1],X.iloc[:,3],c=clusters_kpp_notrials,s=7,cmap='viridis')
    ax[1,1].scatter(X.iloc[:,1],X.iloc[:,3],c=clusters_sklearn,s=7,cmap='viridis')

    ax[0,0].scatter(centers_kpp[:,1], centers_kpp[:,3], s=20, c='red', marker="o")
    ax[1,0].scatter(centers_random[:,1], centers_random[:,3], s=55, c='red', marker="X")
    ax[0,1].scatter(centers_kpp_notrials[:,1], centers_kpp_notrials[:,3], s=55, c='red', marker="*")
    ax[1,1].scatter(centers_sklearn[:,1], centers_sklearn[:,3], s=55, c='orange', marker="o")
    
    # Sous-titre
    ax[0,0].set_xlabel('K means ++ AVEC essaie', labelpad = 5)
    ax[1,0].set_xlabel('Initialisation aléatoire', labelpad = 5)
    ax[0,1].set_xlabel('K means ++ SANS essaie', labelpad = 5)
    ax[1,1].set_xlabel('Sklearn', labelpad = 5)
    
    plt.show()
    
    
    
    
#def plot_each(k,X,e,centers):
#    
#    clusters=lloyd(k,X,e,centers)[1]
#    
#    # On affiche les observations, et les couleurs sont basées sur les clusters
#    plt.scatter(X.iloc[:,1],X.iloc[:,3],c=clusters,s=7,cmap='viridis')
#        
#    # On affiche les centres
#    plt.scatter(centers[:,1], centers[:,3], marker='*', c='black', s=50)
#    
#
#def plot_sklearn(k,X):
#    clusters=kmean_sklearn(k,X)
#    plt.scatter(X.iloc[:,1],X.iloc[:,3],c=clusters,s=7,cmap='viridis')
#    plt.scatter(clusters[:,1], clusters[:,3], marker='*', c='black', s=50)
#
#    


def elbow(X,e):
    SSE=[]
    k = np.arange(1,5)
    for i in range(1,5):
        centers=random_init(i,X)
        kmeans_inertia=lloyd(i,X,e,centers)[2]
        print(kmeans_inertia)
        SSE.append(kmeans_inertia)
    plt.plot(k, SSE, 'bx-')
#    plt.xlabel('k')
#    plt.ylabel('Somme_distance_carre')
#    plt.title('Méthode du coude')
    plt.show()
    
    
def elbow_sklearn(X):
    SSE=[]
    k=np.arange(1,5)
    for i in range(1,5):
        kmeans_inertia=kmean_sklearn(i,X)[2]
        print(kmeans_inertia)
        SSE.append(kmeans_inertia)
    plt.plot(k, SSE, 'bx-')
    plt.show()
    


class DataFrameImputer(TransformerMixin):

    def __init__(self):
        """Impute missing values.

        Columns of dtype object are imputed with the most frequent value 
        in column.

        Columns of other types are imputed with mean of column.
        """
        
    def fit(self, X, y=None):

        self.fill = pd.Series([X[c].value_counts().index[0]
            if X[c].dtype == np.dtype('O') else X[c].median() for c in X],
            index=X.columns)
        return self

    def transform(self, X, y=None):
        return X.fillna(self.fill)






#****************************************************

if __name__=="__main__":
    # Uploading ML dataset
    base=pd.read_csv('/Users/elvinagovendasamy/TER/BigML_Dataset.csv',sep=',')
    
    X=base.iloc[:,1:]
    Y=base.iloc[:,0]
    
    # Imputing based on mean for numeric, and most frequent for strings
    X = DataFrameImputer().fit_transform(X)
    X.fillna(X.mean())
    Y.fillna(Y.mean())




# =============================================================================
# Rouler les algorithmes
# =============================================================================
    
    # Nombre de clusters
    k=5
    # Terme d'erreur
    e=10**(-10)
    
    
    t0=time()
    
    
# En utilisant l'initialisation kpp, AVEC les essaies
    centers_initial_kpp=kpp_init(k,X)
    centers_kpp,centers_kpp_label,kmeans_inertia=lloyd(k,X,e,centers_initial_kpp)
    t1=time()
    print('En utilisant kmeans ++ avec essaie %f' %(t1-t0))    #   2.425
#

# En utilisant l'initialisation aléatoire
#    centers_initial_random=random_init(k,X)
#    centers_random=lloyd(k,X,e,centers_initial_random)[0]
#    t2=time()
#    centers_random_label=lloyd(k,X,e,centers_initial_random)[1]
#    kmeans_inertia=lloyd(k,X,e,centers_initial_random)[2]
##    print(kmeans_inertia)
#    print('En utilisant kmeans (random) %f' %(t2-t0))          #   6.05789


# En utilisant l'initialisation kpp, SANS les essaies
#    centers_initial_kpp_notrials=kpp_init_notrials(k,X)
#    centers_kpp_notrials=lloyd(k,X,e,centers_initial_kpp_notrials)[0]
#    t3=time()
#    centers_kpp_notrials_label=lloyd(k,X,e,centers_initial_kpp_notrials)[1]
#    print('En utilisant kmeans ++ sans essaie %f' %(t3-t0))     #   6.0813
    
# En utilisant lsklearn 

    #centers_sklearn=kmean_sklearn(k,X)[0]
    

# =============================================================================
# Visualisation: Nuage de points
# =============================================================================
    # Afficher tous les plots
    graph_all=plot_data_all(k,X,e)
    
    # Afficher chaque plot séparemment
#    graph_kpp=plot_each(k,X,e,centers_initial_kpp)
#    graph_random=plot_each(k,X,e,centers_initial_random)
#    graph_kpp_notrials=plot_each(k,X,e,centers_initial_kpp_notrials)
#    graph_sklearn=plot_sklearn(k,X) 
    
    
        
    #elbow_manual=elbow(X,e)
#    elbow_sk=elbow_sklearn(X)
    

    

