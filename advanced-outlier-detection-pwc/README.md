# Outlier Detection for Modelling Wind Turbine Power Curves
![](https://assets.justenergy.com/wp-content/uploads/2020/11/wind-energy-image-definition.jpg)

## Problem Statement

- In Wind Turbines, Scada Systems measure and save data such as wind speed, wind direction, generated power etc. This file was taken from a wind turbine's scada system that is working and generating power in Turkey.
- When modelling the power curve of a wind turbine, data is often noisy and full of outliers due to issues such as unplanned maintenance, sensor failure, start/stopping etc. Removal of outliers is required in order to effectively model the power curve of a turbine's standard performance as they will impact the performance of any modelling method.
- Outlier removal can be a lengthy process. This method is an adapted form of the process presented in the paper below and is computationally low cost with potential for being developed as a program that can be used with any turbine data. 
- The method utilises a simple form of computer vision to analyse generated scatter plots, identifying normal observations vs outliers, and using this information to create rules which can classify instances as either normal or abnormal. 
- Future work will involve developing the program as part of the final project of my MSc.

Referenced paper: https://ieeexplore.ieee.org/document/9293311 (A Fast Abnormal Data Cleaning Algorithm for Performance Evaluation of Wind Turbine)
The dataset is available here: https://www.kaggle.com/berkerisen/wind-turbine-scada-dataset
