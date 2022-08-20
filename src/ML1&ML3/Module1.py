import numpy as np
from multiprocessing import Pool
from itertools import chain
import sys
sys.path.append("..")
import gc
import math
from sklearn.preprocessing import normalize


# This function is used to realize “Smoothing based on contact number weight”
def g_con(matrix, chr_name):
    new_matrix1 = normalize(matrix, axis=1, norm='l2')
    new_matrix2 = matrix.dot(new_matrix1)
    new_matrix3 = np.triu(new_matrix2, 1) + np.triu(new_matrix2, 1).T
    return new_matrix3 + np.diag(np.diag(matrix)) # 处理后的上三角 + 处理后的下三角 + 处理前的主对角线元素 形成平滑后的方阵


# The function of reading matrix
def read_matrix(file_path):
    file = open(file_path)
    lines = file.readlines()
    a = []
    for line in lines:
        a.append(line.split())
    a = np.array(a).astype(float)
    return a


# This function is used to rank matrices in the order(1,1)->(1,2)...->(2,1)->...as [1, 2, 3]
def matrix_list(matrix):
    return list(chain.from_iterable(matrix))


# This function is used to realize "Contact binarization".
# The threshold th3 in this paper is actually to sort all elements of the transition probability matrix P from small to large.
# Elements greater than the first 80 % element value in matrix P are assigned to 1, and other elements are assigned to 0
# Before entering this function, each row of matrix matrix represents the transition probability matrix P of chr_name chromosome in a cell of one type
def original_select(matrix, prct):
    if prct > -1:
        # obtains 80 percentiles of each row of matrix matrix.
        thres = np.percentile(matrix, 100 - prct, axis=1)
        Q_concat = (matrix > thres[:, None])
    return Q_concat


# This function is used to achieve "RWR-based smoothing", where parameter rp is the restart probability.
# The random walk with restarts algorithm (RWR)
def random_walk_imp(matrix, rp):
    row, _ = matrix.shape
    row_sum = np.sum(matrix, axis=1)
    for i in range(row_sum.shape[0]):
        if row_sum[i] == 0:
            row_sum[i] = 0.001
    nor_matrix = np.divide(matrix.T, row_sum).T
    Q = np.eye(row)
    I = np.eye(row)
    for i in range(30):
        # The random walk process can be represented by the following matrix operations.
        Q_new = rp * np.dot(Q, nor_matrix) + (1 - rp) * I
        delta = np.linalg.norm(Q - Q_new)
        Q = Q_new.copy()
        # When delta is less than threshold, restart random walk process converges and restart random walk process terminates.
        if delta < 1e-6:
            break
    return Q


# This function is used to generate the chromosome contact matrix
# and perform "Smoothing based on contact number weight" and "RWR-based smoothing".
def con_ran(arg):
    rindex, cell_id, type, chr_name, index, rp = arg
    # Specifies the file path to use, where type is a cell type, cell _ id is the number of cells in a type, such as 44 cells in GM12878, whose number is 1-44
    # chr_name is the marker of chromosomes. Human cells have 23 chromosomes corresponding to 1,2... 22,X.
    # contact_626, 2655 The first and second columns of the dataset are bin numbers, and the third column is the contact count of two bins
    file_path = "../dataset/contact_626/%s/cell_%s_%s.txt" % (type, str(cell_id), chr_name)
    f = "../data"
    ##################################################################
    chr_file = open(file_path)
    lines = chr_file.readlines()
    contact_matrix = np.zeros((index, index))
    for line in lines:
        # bin1, bin2 is the number of two chromosome segments, num is the number of contacts between bin1 and bin2
        bin1, bin2, num = line.split()
        contact_matrix[int(bin1), int(bin2)] += int(num)
        if bin1 != bin2:
            contact_matrix[int(bin2), int(bin1)] += int(num)
    # Reducing the Influence of Noise Data
    contact_matrix = np.log2(contact_matrix + 1)
    g_matrix1 = g_con(contact_matrix, chr_name)
    g_matrix2 = g_con(g_matrix1, chr_name)
    g_matrix3 = g_con(g_matrix2, chr_name)
    g_matrix4 = g_con(g_matrix3, chr_name)
    g_matrix5 = g_con(g_matrix4, chr_name)
    g_matrix6 = g_con(g_matrix5, chr_name)
    r_matrix = random_walk_imp(g_matrix6, rp)
    r_path = "./Data/after_smooth/Adj_KPCA_626/%s/cell_%s_%s.txt" % (type, str(cell_id), chr_name)
    np.savetxt(r_path, r_matrix, fmt='%f', delimiter=' ')

def main():
    # Note : Before the program runs, the following folders should be created under the root directory of the program :
    # /Data/after_smooth/Adj_KPCA_626/GM12878、HAP1、HeLa、K562
    # /Data/after_bin/Adj_KPCA_626/
    ##################################################################
    # Note : "combo_ hg19.genomesize" is the length of 23 chromosomes that are common to human cells, regardless of which cell in humans, the 23 chromosomes are this length, in unit of the number of base pairs.
    # The first and second columns of contacts_626,2655 and other data sets are bin ( chromosome fragment ) numbers, and the third column is the contact count of two bins.
    ###################################################################
    # Step 1: Divide 23 chromosomes into blocks according to the specified resolution
    # Indicate the number of cells of each type in the dataset
    types = {'HeLa': 258, 'HAP1': 214, 'GM12878': 44, 'K562': 110}
    # Specify the resolution
    resolutions = [1000000]
    # Specify the restart probability
    rp = 0.1
    tps = sorted(types)
    # The file contains the names of 23 chromosomes in human cells and the corresponding length of each chromosome ( length in base units, length is the number of bases contained, length 90 indicates that the chromosome contains 90 base pairs )
    f = open("../combo_hg19.genomesize")
    index = {}
    for resolution in resolutions:
        index[resolution] = {}
        lines = f.readlines()
        for line in lines:
            chr_name, length = line.split()
            chr_name = chr_name.split('_')[1]
            max_len = int(int(length) / resolution)
            index[resolution][chr_name] = max_len + 1
        f.seek(0, 0)
    f.close()
    resolution = 1000000
    print(index)
    # 1mbp means that 1M (100,000) base pairs are used as resolutions, so rindex is used to mark the resolution of the index
    rindex = "1mbp"
    #########################################################################################################
    # The second step is to generate chromosome contact matrix and perform ' Smoothing based on contact number weight ' and ' RWR-based smoothing '.
    # Initialize process pool
    p = Pool(23)
    for type in tps:
        for c_num in range(types[type]):
            cell_id = c_num + 1
            args = [[rindex, cell_id, type, chr_name, index[resolution][chr_name], rp] for chr_name in
                    index[resolution]]
            print(args)
            p.map(con_ran, args)
    p.close()
    # Clean up memory, because a lot of data has been done before, so you need to recover and release memory immediately
    gc.collect()
    # #########################################################################################################
    # Step 3 : Contact binarization
    C_matrix = []
    length = 0
    new_chr_matrix = []
    # chr_name:chr1、chr2....chr22、chrx
    for chr_name in index[resolution]:
        new_chr_matrix.clear()
        pca_index = []
        print(chr_name)
        for type in tps:
            print(type)
            for c_num in range(types[type]):
                cell_id = c_num + 1
                r_path = "./Data/after_smooth/Adj_KPCA_626/%s/cell_%s_%s.txt" % (type, str(cell_id), chr_name)
                print(r_path)
                # r_matrix is a transition probability matrix P after random walk smoothing
                r_matrix = read_matrix(r_path)
                new_chr_matrix.append(matrix_list(r_matrix))
                cindex = (type, cell_id)
                pca_index.append(cindex)
        new_chr_matrix = np.array(new_chr_matrix)
        # After the processing of the previous line of code, the new_chr_matrix at this time becomes a two-dimensional array of the numpy class,
        # that is, a matrix, which is the probability transition matrix of the chromosome chr_name in all cells of all types.
        # Each row of the matrix represents the transition probability matrix P of chromosome number chr_name in a cell of a type according to the order of (1,1)->(1,2)...->(2,1)->..  into a list
        # So new_chr_matrix.shape[1] is the square of the number of chromosome fragments cut out from chromosome chr_name.
        length += new_chr_matrix.shape[1]
        # Original _ select is a custom function for contact binarization
        new_new_matrix = original_select(new_chr_matrix, 20)
        # After the previous line of code processing, the matrix is the probability transition matrix of chromosome number chr_name in all cells of all types after contact binarization
        C_matrix.append(new_new_matrix)
        new_chr_matrix = new_chr_matrix.tolist()

    # Here C_matrix is a list, but each element in the list is a two-dimensional array, that is, a matrix, that is, the probability transition matrix of a chromosome in all cells of all types is a matrix after contact binarization.
    # And each row of this matrix represents the transition probability matrix P of a chromosome in a cell of a type. After contact binarization, the matrix (called a binary matrix) is arranged in a list(a one-dimensional array) in the following order: (1,1)->(1,2)...->(2,1)->...
    C_matrix = np.concatenate(C_matrix, axis=1)

    cell_dict = {}

    for i, j in zip(pca_index, C_matrix):
        if i[0] == 'GM12878':
            cell_dict[(0, i[1])] = j
        elif i[0] == 'HAP1':
            cell_dict[(1, i[1])] = j
        elif i[0] == 'HeLa':
            cell_dict[(2, i[1])] = j
        elif i[0] == 'K562':
            cell_dict[(3, i[1])] = j

    out_path1 = './Data/after_bin/Adj_KPCA_626/cell_dict.npy'
    np.save(out_path1, cell_dict)

if __name__ == "__main__":
    main()
