#!/usr/bin/env python3
from pydoc import doc
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from numpy import linalg as LA
from sklearn import linear_model, preprocessing
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.decomposition import PCA

''' develop the best predictive model based on the chemical engineering dataset'''

__author__ = 'Jacob Hajjar, Michael-Ken Okolo, Vatsal Patel, Ayush Bhatnagar, Onkar Muttemwar'
__email__ = 'hajjarj@csu.fullerton.edu, michaelken.okolo1@csu.fullerton.edu, vatsal1224@csu.fullerton.edu, ' \
            'ayush.bhatnagar@csu.fullerton.edu, onkar.muttemwar@csu.fullerton.edu'
__maintainer__ = 'jacobhajjar, michaelkenokolo'


def main():
    """the main function"""
    data_frame = pd.read_csv("Data1.csv")
    x_data = data_frame[["T", "P", "TC", "SV"]].to_numpy()
    y_data = data_frame["Idx"].to_numpy()

    # Problem 1.
    # standardize data and estimate covariance matrix
    x_standardized_data = preprocessing.StandardScaler().fit_transform(x_data)
    cov_matrix = np.cov(x_data.T)
    print("Covariance Matrix: \n{}\n".format(cov_matrix))

    # calculate eigenvalues and eigenvector
    eig_val, eig_vec = LA.eig(cov_matrix)
    print("Eigenvalues: {} \nEigenvector: \n{}\n".format(eig_val, eig_vec))

    # find projection matrix
    proj_matrix = np.dot(x_standardized_data, eig_vec)
    print("Projection Matrix: \n{}".format(proj_matrix))

    # component matrix and explained variance
    print("\nComponent Matrix and Explained Variance:")
    total_var = np.sum(eig_val)
    for index in range(0, 4, 1):
        percent_var = (eig_val[index] / total_var) * 100
        print("%var of PC", (index + 1), "is " + "{:.3f}: {}".format(percent_var, eig_vec[..., index]))

    # printing out projection matrix.
    for index in range(0, 4, 1):
        if eig_val.all() > np.mean(total_var):
            print(proj_matrix[..., index])

    # Problem 2.
    # explained variance > 80%
    pca = PCA(n_components=4)
    x_trained_pca = pca.fit_transform(x_standardized_data)
    explained_var = pca.explained_variance_ratio_

    # print(x_trained_pca)
    # cumulative sum of all the eigenvalues.
    cum_sum_eigenvalues = np.cumsum(explained_var)
    print("\nExplained Variance: {}".format(explained_var))
    print("Cumulative Sum of Eigenvalues: {}".format(cum_sum_eigenvalues))

    # graph the relationship between number of pca's and explained variance ratio.
    cumVarExplained = []
    nb_components = []
    counter = 1
    for i in explained_var:
        cumVarExplained.append(explained_var[0:counter].sum())
        nb_components.append(counter)
        counter += 1
    print(cumVarExplained)
    plt.subplots(figsize=(8, 6))
    plt.plot(nb_components, cumVarExplained, 'bo-')
    plt.ylabel('Explained Variance Ratio')
    plt.xlabel('Number of Components')
    plt.ylim([0.0, 1.1])
    plt.xticks(np.arange(1, len(nb_components) + 1, 1.0))
    plt.yticks(np.arange(0.0, 1.1, 0.10))
    # plt.show()

    # Kaiser criteria
    # get the mean of the eigenvalues and check if each eigenvalue is greater than the mean
    kaiser_list = []
    eigen_mean = np.mean(eig_val)
    for i in range(0, 4, 1):
        if eigen_mean < eig_val[i]:
            kaiser_list.append(eig_val[i])
    print("Kaiser Criteria: {}".format(kaiser_list))

    # Correlation matrix > 0.5
    # corr_matrix = np.corrcoef(x_data.T, y_data)
    num_pc = pca.n_features_
    X_data_frame = data_frame.drop('Idx', axis=1)
    loadings = pca.components_.T * np.sqrt(pca.explained_variance_)

    pc_list = ["PC" + str(i) for i in list(range(1, num_pc + 1))]
    corr_matrix = pd.DataFrame(loadings, columns=pc_list, index=X_data_frame.columns.values)
    corr_matrix = corr_matrix.to_numpy()
    print("\nCorrelation Matrix: \n{}".format(corr_matrix))

    # Problem 3.
    # separate 80% of the data to training
    testing_separation_index = math.floor(len(x_data) * 0.8)
    x_training = x_data[:testing_separation_index]
    x_testing = x_data[testing_separation_index:]

    y_training = y_data[:testing_separation_index]
    y_testing = y_data[testing_separation_index:]

    # create pc scores for training data set
    pc1_training = []
    selected_pc = 0
    for data in x_training:
        pc1_val = 0
        for index in range(0, 4, 1):
            pc1_val += (eig_vec[index, selected_pc] * data[index])
        pc1_training.append([pc1_val])

    # perform least squares regression
    reg = linear_model.LinearRegression()
    reg.fit(np.array(pc1_training), y_training)

    # create pc scores for testing data set
    pc1_testing = []
    for data in x_testing:
        pc1_val = 0
        for index in range(0, 4, 1):
            pc1_val += (eig_vec[index, selected_pc] * data[index])
        pc1_testing.append([pc1_val])

    # predict new value
    print("\nPredict with testing data: {}, Real value: {}".format((pc1_training[500] * reg.coef_ + reg.intercept_),
                                                                   y_training[500]))

    # get the error for the prediction using PC1
    # predict the y values with PC1 for the training and testing data
    y_pc1_predicted_training = reg.predict(pc1_training)
    y_pc1_predicted_test = reg.predict(pc1_testing)

    # create model for predicting using all variables
    reg.fit(x_training, y_training)

    # predict training and testing error using the original data in linear regression
    y_predicted_test = reg.predict(x_testing)
    y_predicted_training = reg.predict(x_training)

    # get the error for training and testing data using PC1
    mean_error_training_pc1 = mean_squared_error(y_training, y_pc1_predicted_training)
    r2_training_pc1 = r2_score(y_training, y_pc1_predicted_training)

    mean_error_testing_pc1 = mean_squared_error(y_testing, y_pc1_predicted_test)
    r2_testing_pc1 = r2_score(y_testing, y_pc1_predicted_test)

    # get the error for training and testing data using original variables
    mean_error_training = mean_squared_error(y_training, y_predicted_training)
    r2_training = r2_score(y_training, y_predicted_training)

    mean_error_testing = mean_squared_error(y_testing, y_predicted_test)
    r2_testing = r2_score(y_testing, y_predicted_test)

    print("\nPredictions for PC1:")
    print("Root Mean Square (Training): {}, R2 (Training): {}".format(mean_error_training_pc1, r2_training_pc1))
    print("Root Mean Square (Testing) : {}, R2 (Testing) : {}".format(mean_error_testing_pc1, r2_testing_pc1))

    print("\nPredictions using Original Data:")
    print("Root Mean Square (Training): {}, R2 (Training): {}".format(mean_error_training, r2_training))
    print("Root Mean Square (Testing) : {}, R2 (Testing) : {}".format(mean_error_testing, r2_testing))


if __name__ == '__main__':
    main()
