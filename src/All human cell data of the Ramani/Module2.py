import numpy as np
from sklearn import metrics
from sklearn.cluster import KMeans, SpectralClustering
from sklearn.decomposition import KernelPCA
from sklearn.manifold import TSNE
from sklearn.metrics import euclidean_distances, accuracy_score

from collections import Counter
from scipy.optimize import linear_sum_assignment
import xlsxwriter



def processing_label(label, truth, n_clusters):
    point = 0
    k = 0
    label_order = []
    label_matrix = np.zeros((n_clusters, n_clusters), np.int64)

    for i in range(len(truth)):
        if truth[point] == truth[i]:
            continue
        else:
            label_order.append(truth[point])
            counter = Counter(label[point:i])
            point = i
            for j in range(n_clusters):
                label_matrix[k][j] = counter[j]
            k += 1

    label_order.append(truth[point])
    counter = Counter(label[point:len(label) - 1])
    for j in range(n_clusters):
        label_matrix[n_clusters - 1][j] = counter[j]
    row_ind, col_ind = linear_sum_assignment(-label_matrix)
    for j in range(len(label)):
        for i in range(n_clusters):
            if label[j] == col_ind[i]:
                label[j] = label_order[i] + n_clusters
    return label - n_clusters


if __name__ == "__main__":
    cell_num = 2655
    # Read the data processed by the Module1
    file_path = './Data/after_bin/Adj_KPCA_%s/cell_dict.npy' % cell_num
    cell_dict = np.load(file_path, allow_pickle=True).item()
    print(cell_dict.values())

    # Use X to store the list of features for all cells
    X = []
    for cell in cell_dict.keys():
        X.append(cell_dict[(cell[0],cell[1])])
    # cluster_X is the feature matrix of all cells, and the feature vector of each cell is one row.
    # Each column of the matrix is the eigenvector of a cell, and the contact matrix of the 23 chromosomes of a cell is compressed into a column of eigenvectors.
    cluster_X = np.array(X)
    # The following line of code is used to implement"Principal component extraction"
    pca = KernelPCA(n_components=min(cluster_X.shape) - 1, kernel='cosine')
    pca.fit(cluster_X)
    pca_cluster_X = pca.transform(cluster_X)
    Y = []
    # The following line of code is used to get the true label
    for (i,j) in cell_dict.keys():
        Y.append(i)
    label = np.array(Y)
    gammakk = 3
    file = './result/gamma=%d.xlsx' % (gammakk)
    workbook = xlsxwriter.Workbook(file)
    worksheet1 = workbook.add_worksheet('result')
    worksheet1.write(0, 0, 'Top n dimensions')
    worksheet1.write(0, 1, 'ARI')
    worksheet1.write(0, 2, 'AMI')
    worksheet1.write(0, 3, 'HM')
    worksheet1.write(0, 4, 'FM')
    print("<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    print("gamma = ", gammakk)
    for i in range(40):
        data = pca_cluster_X[:, :i + 1]
        similarity_matrix_o = euclidean_distances(data)
        final_matrix = np.hstack((similarity_matrix_o, data))
        y_pred1 = SpectralClustering(n_clusters=4, gamma=gammakk, affinity='rbf').fit_predict(final_matrix)
        y_pred1 = processing_label(y_pred1, label, 4)
        ari = metrics.adjusted_rand_score(label, y_pred1)
        ami = metrics.adjusted_mutual_info_score(label, y_pred1)
        hm = metrics.homogeneity_score(label, y_pred1)
        fm = metrics.fowlkes_mallows_score(label, y_pred1)

        print("i=", i, "gamma=", gammakk, "Ari", ari, "Ami", ami, "hm", hm, "fm", fm)
        worksheet1.write(i + 1, 0, i)
        worksheet1.write(i + 1, 1, ari)
        worksheet1.write(i + 1, 2, ami)
        worksheet1.write(i + 1, 3, hm)
        worksheet1.write(i + 1, 4, fm)
    print("<<<<<<<<<<<<<<<<<<<<<<<>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    workbook.close()

