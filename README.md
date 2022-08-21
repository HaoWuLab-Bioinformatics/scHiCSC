# scHiCSC
## Introduction
scHiCSC is a novel single-cell Hi-C clustering framework by contact-weight-based smoothing and feature fusion.It achieves an optimal and stable clustering effect in the datasets with large-scale cell numbers and can cluster the cells of small size in the whole dataset.

## Overview
<img src="framework.png" width="1000" height="500" />  

The scHiCSC framework consists of three crucial steps: cell embedding generation,feature fusion, and spectral clustering.In this framework, we propose a new smoothing approach based on contact number weight, and construct cell embedding sequentially by a random walk with restart smoothing. Furthermore, we present a new feature fusion approach to achieve the cell embedding created in the preceding stage and generate a feature fusion matrix. Finally, the spectral clustering algorithm is used to achieve cell clustering.

## Usage
The code of scHiCSC contains two modules:
### Module 1: 
scHiCSC proposes "smoothing based on contact number weight", "RWR(random walk with restart)-based smoothing" and "Contact binarization" to impute the chromosome contact matrices for each cell and each chromosome separately. Thus you can run the script as:

``` python './src/ML1&ML3/Module1.py' ```  or ``` python './src/All human cell data of the Ramani/Module1.py'```

or ``` python './src/800cells/Module1.py'```

### Module 2:
After imputation, scHiCSC generate the cell embedding. Then, a novel feature fusion method is proposed to further supplement the feature information of cells by fusing the chromosome structure information within cells and the distance information between cells. Finally, scHiCSC uses the spectral clustering algorithm to achieve cell clustering.You can run the script as:

``` python './src/ML1&ML3/Module2.py' ```  or ``` python './src/All human cell data of the Ramani/Module2.py'```

or ``` python './src/800cells/Module2.py'```

Note：Folders named Files and parameters need to be placed in the project directory you created
## Dependency
Python 3.6   
sklearn  
numpy  




## Contact us

If you have any questions, please contact us: haowu@sdu.edu.cn.

