# scHiCSC
## Introduction
scHiCSC is a novel single-cell Hi-C clustering framework by contact-weight-based smoothing and feature fusion.It achieves a good and stable clustering effect in the datasets with large-scale cell numbers and can cluster the cells whose number is very small in the whole dataset.

## Usage
### Smooth chromesome contact matrix
In order to better discriminate different types of cells and obtain the excellent clustering effect,we propose a new smoothing approach based on contact number weight, and construct cell embedding sequentially by a random walk with restart smoothing.Thus you can run the 

###Feature fusion and Clustering

First, you should perform data preprocessing, you can run the script as: 

`python data prepare.py`  

Then you can extract features you need through running the script as:  

`python feature_code.py` or `python psednc.py`  

Finally if you want to compile and run StackTADB, you can run the script as:  

Fisrst of all ,you should perform 
`python './626cells/Module1.py'`

`python './626cells/Module2.py'`

## Dependency
Python 3.6   
keras  2.3.1  
sklearn  
numpy  
mlxtend  
h5py 




Note：Folders named Files and parameters need to be placed in the project directory you created

## Contact us

If you have any questions, please contact us: haowu@sdu.edu.cn.

