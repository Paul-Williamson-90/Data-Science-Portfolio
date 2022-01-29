# Modelling the Power Curve of Wind Turbines
![](https://assets.justenergy.com/wp-content/uploads/2020/11/wind-energy-image-definition.jpg)

## Problem Statement

- In Wind Turbines, Scada Systems measure and save data such as wind speed, wind direction, generated power etc. This file was taken from a wind turbine's scada system that is working and generating power in Turkey.
- The objective was to model typical performance of the wind turbines, removing outliers and anomalies which would impact the model fit
- The final model uses a Radial Basis Function kernel on a Support Vector Machine

This was a basic attempt at modelling the power curve of the turbines. The focus of a future project will research better methods for modelling the power curve and identifying outliers. The end result will be a data-driven approach for detecting yaw misalignment and early fault detection.

The dataset is available here: https://www.kaggle.com/berkerisen/wind-turbine-scada-dataset
