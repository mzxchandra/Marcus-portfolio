# -*- coding: utf-8 -*-
"""119 Final project

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1WWYVPLp4MLWOiUOp8Yjle_pq8RTDs3JR
"""

import statsmodels.api as sm
import pandas as pd
import numpy as np
import sklearn as sk
from statsmodels.stats.outliers_influence import variance_inflation_factor

from google.colab import files
uploaded = files.upload()

import io
life_exp = pd.read_csv(io.BytesIO(uploaded['Life Expectancy Data.csv']))

"""#Part A: Introduction to the dataset

This dataset was created using data collected from the World Health Organization (data on health-related factors) and the United Nations (data on economic-related factors). It compiled data from these two data sources collected over a period of 15 years (2000-2015) for the purpose of helping countries identify key predictors of life expectancy. We were interested in this dataset in particular because it included a broad range variables covering economic, health, and mortality factors that will allow us to conduct multi-dimensional analyses of life expectancy.

Links:
https://www.kaggle.com/datasets/kumarajarshi/life-expectancy-who


https://www.who.int/data/gho/data/indicators/indicators-index

From Kaggle listed by Kumar Rajarshi.

Acknowledgements:
The data was collected from WHO and United Nations website with the help of Deeksha Russell and Duan Wang.

#Part B: Literature Review
One study that synthesized WHO data and United Nations Data is 2014 Global geographic analysis of mortality from ischaemic heart disease by country, age and income, authored by Alexandra N. Nowbar et al. In this study, Nowbar used WHO data to study the prevalence of heart disease across countries and used United Nations data to separate countries by GDP per capita. They discovered that age-specific death rates for heart disease have been gradually declining over time, while total death rates have remained constant due to an aging population.  This information can help us understand the impact of economic development on health outcomes, which is relevant to our analysis of life expectancy.
Another study that synthesized data from the World Health Organization and the United Nations was Global healthcare expenditure on diabetes for 2010 and 2030, authored by Ping Zhang et al. By analyzing data from the World Health Organization and the United Nations, they found that 12% of all health expenditures were expected to be spent on diabetes in 2010. However, this amount varied across countries, with poorer countries spending the least on diabetes. They concluded that more resources should be allocated to these countries for basic diabetes care. In our project, we plan to investigate health spending as a parameter, so this study provides us valuable information on the effect health spending has on disease/mortality rates.

#Part C: Data Analysis
This dataset is huge, with numerous NaN cells for multiple variables. From Table 1, which shows the percentage of missing cells for each variable, we decided to examine variables with few missing values. It is important to find a balance between eliminating variables with missing values. We decided to eliminate variables up to "thinness 5-9 years,” as the change in missing value percentage from 5% to 1% is significant. Exploratory data analysis was performed on all variables after “thinness 5-9 years” (based on Table 1). From the correlation matrix (not shown on report), “under-five deaths” and “infant deaths” (r = 0.997) are collinear as they both relate to deaths. Thinness 1-19 years and thinness 5-9 years (0.939) are also collinear because both are about thinness. Polio and diphtheria (0.668) has a high correlation relative to the other variables (but not high enough to indicate high collinearity). The rest of the variables have relatively low (< 0.5) correlation.
	If we plot the response variable (Life Expectancy) histogram (Figure 1), we see that it is skewed. We therefore use logarithm to save the response variable. This is also a sign that regularization methods should be performed to improve the dataset. After fitting an OLS model (linear), we examine the scatterplot of residuals against predicted values. From the scatterplot of life expectancy against its residuals (Figure 2), we see that it is not randomly dispersed. At lower life expectancy values, only positive residuals are recorded. And as life expectancy increases, there are significantly more datasets that are dispersed in the center. This shows that a linear regression model without regularization may not be appropriate. Furthermore, upon examining the VIF, there are various high values, such as infant deaths and under five deaths (which is consistent with the correlation matrix). Other high values include Polio and Diphtheria (22), as well as both of the thinness (18).

We now look at three types of regularizations: ridge, kNN, neural network. We determined that ridge gives the model the best fit based on the highest (closest to 0) neg_mean_squared_error of cross_val_score.

Using Ridge CV from sklearn with 5 fold cross validation, we determine the best alpha to be 0.6 (shown by the black vertical line). The most significant variable is “under-five deaths” (-0.240907), though its effects are negated by “infant death” (0.238711), which, again, is expected due to collinearity. The cross validation score (neg_mean_squared_error) is -0.005085 (nrmse = -0.0713).
For kNN regression, we test k values from 1-100. From the graph, we can conclude that at k =3, the negative 10-fold CV error is the lowest at -7.401981. This, however, is higher than the ridge error.

Using neural networks, after fitting several different models we found an optimal model with one 10-unit hidden layer, using the linear activation function, and a batch size of 64, and epoch of 50. It yielded a low negative root mean squared error of (-0.0737). We were reluctant to increase batch size and epoch further because of overfitting, and the improvement in error score was marginal. This approach performed well, but it still had a higher error than our linear ridge model, and the approach seems less appropriate for our relatively small dataset with 2888 observations.
We also experimented with a logistic approach. We took the average world life expectancy for each year, and assigned “low” life expectancy to observations that performed below their respective average. We first fit our logistic model without regularization (Figure 5), which resulted in a AUC of 0.884. We then tried different parameters like LASSO and Ridge penalties, which all yielded high AUC scores (around 0.90). These models performed well, but they are limited in that the output only tells us the likelihood of an observation having below average or above average life expectancy.
"""

missing = life_exp[['Country', 'Year', 'Status', 'Life expectancy ', 'Adult Mortality',
       'infant deaths', 'Alcohol', 'percentage expenditure', 'Hepatitis B',
       'Measles ', ' BMI ', 'under-five deaths ', 'Polio', 'Total expenditure',
       'Diphtheria ', ' HIV/AIDS', 'GDP', 'Population',
       ' thinness  1-19 years', ' thinness 5-9 years',
       'Income composition of resources', 'Schooling']].isna().sum()

missing_df = pd.DataFrame({
    "% missing values" : missing*100/life_exp.shape[0]
})
missing_df.sort_values(by = "% missing values", ascending = False)

"""From this, we know to eliminate columns with a significant number of missing values (for example, roughly 20% of the countries do not have reported data for Population and Hepititus B , so it's not worthwile to considering these variable when building a model). It is important to find a balance between eliminating variables with missing values, and eliminating countries with missing values. We decided to eliminate variables from the table above until we reached "thinness 5-9 years" because of the big drop off from 5% to 1% of data being missing. Further, when eliminating rows with missing values afterwards, we found that it was the same 2 countries that lacked data across variables, so it was a reasonable decision."""

life_exp = life_exp.drop(columns = ["Population", "GDP", "Hepatitis B", "Schooling", "Total expenditure", "Alcohol", "Income composition of resources"])
life_exp = life_exp.dropna()
life_exp = pd.get_dummies(life_exp, columns = ['Status'])
life_exp["Country + Year"] = life_exp["Country"] + " " + life_exp['Year'].astype(str)
life_exp = life_exp.drop(['Country','Year'], axis = 1)
life_exp = life_exp[['Country + Year', 'Life expectancy ', 'Adult Mortality', 'infant deaths',
       'percentage expenditure', 'Measles ', ' BMI ', 'under-five deaths ',
       'Polio', 'Diphtheria ', ' HIV/AIDS', ' thinness  1-19 years',
       ' thinness 5-9 years', 'Status_Developed', 'Status_Developing']]

from statsmodels.stats.outliers_influence import variance_inflation_factor
numerical = ['Adult Mortality', 'infant deaths',
       'percentage expenditure', 'Measles ', ' BMI ', 'under-five deaths ',
       'Polio', 'Diphtheria ', ' HIV/AIDS', ' thinness  1-19 years',
       ' thinness 5-9 years']

X = life_exp[numerical]

vif = pd.DataFrame()
vif["feature"] = X.columns
vif["VIF"] = [variance_inflation_factor(X.values, i) for i in range(len(X.columns))]
vif

"""From looking at the Variance Inflation Factors, we find that there is evidence of collinearity among our numerical variables.

Infant deaths and under-five deaths are highly correlated with each other and this tracks because countries with poor public health are ill-equipped to tackle malnutrition, and diseases which are common causes for both.

Polio and Diphtheria seem to be highly correlated with each other, they are both immunizations, and it is likely that most countries that administer one of them will also administer the other.

Lastly, the two thinnesss categories are highly correlated.

**Linear Regression, Ridge**
"""

life_exp = pd.read_csv(io.BytesIO(uploaded['Life Expectancy Data.csv']))
life_exp = life_exp.drop(columns = ["Population", "GDP", "Hepatitis B", "Schooling", "Total expenditure", "Alcohol", "Income composition of resources"])
life_exp = life_exp.dropna()
life_exp = pd.get_dummies(life_exp, columns = ['Status'])
life_exp["Country + Year"] = life_exp["Country"] + " " + life_exp['Year'].astype(str)
life_exp = life_exp.drop(['Country','Year'], axis = 1)
life_exp = life_exp[['Life expectancy ', 'Adult Mortality', 'infant deaths',
       'percentage expenditure', 'Measles ', ' BMI ', 'under-five deaths ',
       'Polio', 'Diphtheria ', ' HIV/AIDS', ' thinness  1-19 years',
       ' thinness 5-9 years', 'Status_Developed', 'Status_Developing']]

#Splitting Test vs. Training Data
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score


# Select the independent and dependent variables
X = life_exp.drop(['Life expectancy '], axis=1)
y = life_exp['Life expectancy ']

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

#Linear Regression
# Create a linear regression model and fit it to the training data
model = LinearRegression()
model.fit(X_train, y_train)

# Make predictions on the test data
y_pred = model.predict(X_test)

# Evaluate the model performance
mse = mean_squared_error(y_test, y_pred)
nrmse = (-1)*((mse)**(1/2))
r2 = r2_score(y_test, y_pred)

print(f"Mean squared error: {mse:.2f}")
print(f"R^2 score: {r2:.2f}")
print("Negative Root Mean Squared Error:", nrmse)

from sklearn.linear_model import Ridge
#Ridge Regression

# Create a ridge regression model and fit it to the training data
model = Ridge(alpha=1)  # alpha is the regularization parameter
model.fit(X_train, y_train)

# Make predictions on the test data
y_pred = model.predict(X_test)

# Evaluate the model performance
mse = mean_squared_error(y_test, y_pred)
nrmse = (-1)*((mse)**(1/2))
r2 = r2_score(y_test, y_pred)

print(f"Mean squared error: {mse:.2f}")
print(f"R^2 score: {r2:.2f}")
print("Negative Root Mean Squared Error:", nrmse)

"""**Neural Network**"""

import tensorflow as tf
import keras
from sklearn.preprocessing import StandardScaler
import sklearn as sk
from keras.models import Sequential
from keras.layers import Activation, Dense
import warnings

import io
life_exp = pd.read_csv(io.BytesIO(uploaded['Life Expectancy Data.csv']))
life_exp = life_exp.drop(columns = ["Population", "GDP", "Hepatitis B", "Schooling", "Total expenditure", "Alcohol", "Income composition of resources"])
life_exp = life_exp.dropna()
life_exp = pd.get_dummies(life_exp, columns = ['Status'])
life_exp["Country + Year"] = life_exp["Country"] + " " + life_exp['Year'].astype(str)
life_exp = life_exp.drop(['Country','Year'], axis = 1)
life_exp = life_exp[['Country + Year', 'Life expectancy ', 'Adult Mortality', 'infant deaths',
       'percentage expenditure', 'Measles ', ' BMI ', 'under-five deaths ',
       'Polio', 'Diphtheria ', ' HIV/AIDS', ' thinness  1-19 years',
       ' thinness 5-9 years', 'Status_Developed', 'Status_Developing']]

X = life_exp[['Adult Mortality', 'infant deaths',
       'percentage expenditure', 'Measles ', ' BMI ', 'under-five deaths ',
       'Polio', 'Diphtheria ', ' HIV/AIDS', ' thinness  1-19 years',
       ' thinness 5-9 years', 'Status_Developed', 'Status_Developing']]

Y = np.log(life_exp["Life expectancy "]) #Log Life expectancy
scaler = StandardScaler()
scaler.fit(X)

X_pp = pd.DataFrame(scaler.transform(X), columns = [['Adult Mortality', 'infant deaths',
       'percentage expenditure', 'Measles ', ' BMI ', 'under-five deaths ',
       'Polio', 'Diphtheria ', ' HIV/AIDS', ' thinness  1-19 years',
       ' thinness 5-9 years', 'Status_Developed', 'Status_Developing']])

def neuralnetwork():
    model= Sequential([
        Dense(10, input_dim = 13, activation="linear"),
        Dense(1)
    ])
    model.compile(optimizer='sgd', loss='mse', metrics = [tf.keras.metrics.RootMeanSquaredError()])
    return(model)

estimator= tf.keras.wrappers.scikit_learn.KerasRegressor(build_fn=neuralnetwork, epochs=50, batch_size=64, verbose=0)
kfold= sklearn.model_selection.RepeatedKFold(n_splits=10, n_repeats=1)
results = sklearn.model_selection.cross_val_score(estimator, X_pp, Y, cv=kfold, scoring = "neg_root_mean_squared_error")
NRMSE = results.mean()  #Mean RMSE
NRMSE

"""**Logistic Regression**"""

from sklearn import metrics
from sklearn.metrics import accuracy_score, confusion_matrix, roc_auc_score, roc_curve

warnings.filterwarnings("ignore")
life_exp = pd.read_csv(io.BytesIO(uploaded['Life Expectancy Data.csv']))
life_exp = life_exp.drop(columns = ["Population", "GDP", "Hepatitis B", "Schooling", "Total expenditure", "Alcohol", "Income composition of resources"])
life_exp = life_exp.dropna()
life_exp = pd.get_dummies(life_exp, columns = ['Status'])
life_exp["Country + Year"] = life_exp["Country"] + " " + life_exp['Year'].astype(str)
life_exp = life_exp.drop(['Country','Year'], axis = 1)
life_exp = life_exp[['Country + Year', 'Life expectancy ', 'Adult Mortality', 'infant deaths',
       'percentage expenditure', 'Measles ', ' BMI ', 'under-five deaths ',
       'Polio', 'Diphtheria ', ' HIV/AIDS', ' thinness  1-19 years',
       ' thinness 5-9 years', 'Status_Developed', 'Status_Developing']]

avg_df = pd.read_csv(io.BytesIO(uploaded['Life Expectancy Data.csv']))
avg_df = avg_df.drop(columns = ["Population", "GDP", "Hepatitis B", "Schooling", "Total expenditure", "Alcohol", "Income composition of resources"])
avg_df = avg_df.dropna()
yearly_averages = avg_df.groupby("Year")["Life expectancy "].mean()
average = []
for i in yearly_averages:
    average.append(i)
years = []
for i in range(2000,2016):
    years.append(i)

yearly_df = pd.DataFrame({
    "Year": years,
    "World average life expectancy": average
})
avg_2 = pd.merge(avg_df, yearly_df, on = "Year")
avg_2["Life Expectancy Difference"] = avg_2["Life expectancy "] - avg_2["World average life expectancy"]

def low_le(value):
    """We want to say that if the life expectancy is equal or greater than the world average,
    it is not a low life expectancy country"""
    if value >= 0:
        return("False")
    else:
        return("True")

avg_2["Low life expectancy"] = avg_2.apply(lambda x: low_le(x["Life Expectancy Difference"]), axis = 1)
avg_2["Country + Year"] = avg_2["Country"] + " " + avg_2['Year'].astype(str)
avg_2 = avg_2.drop(columns = {"World average life expectancy", "Life expectancy ", "Life Expectancy Difference", "Country", "Year"})
avg_2 = pd.get_dummies(avg_2, columns = ['Status', "Low life expectancy"])
avg_2 = avg_2[['Low life expectancy_True', "Country + Year", 'Adult Mortality', 'infant deaths',
       'percentage expenditure', 'Measles ', ' BMI ', 'under-five deaths ',
       'Polio', 'Diphtheria ', ' HIV/AIDS', ' thinness  1-19 years',
       ' thinness 5-9 years', 'Status_Developed', 'Status_Developing']]
avg_2 = avg_2.rename(columns = {"Low life expectancy_True": "Low L.E."})

X = avg_2[['Adult Mortality', 'infant deaths',
       'percentage expenditure', 'Measles ', ' BMI ', 'under-five deaths ',
       'Polio', 'Diphtheria ', ' HIV/AIDS', ' thinness  1-19 years',
       ' thinness 5-9 years', 'Status_Developed', 'Status_Developing']]
X = sm.add_constant(X)
Y = avg_2[["Low L.E."]]

model1 = sm.Logit(Y, X).fit()
model1.summary()

import matplotlib.pyplot as plt
fpr, tpr, thresholds = metrics.roc_curve(Y, model1.predict()>0.30, pos_label=1)
plt.plot(fpr, tpr)
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title("ROC curve for logistic regression")
print("AUC = ", metrics.auc(fpr, tpr))

"""# Part D: Summary

Comparing the cross validation scores, we decided ultimately that our linear ridge regression model was most appropriate for creating a Life Expectancy predictor from this data. Our final equation with an alpha of 0.6 is:
Life expectancy = Adult Mortality * -0.044287 + Infant deaths * 0.238711 + percentage expenditure * 0.013742 - Measles * 0.004334 + BMI * 0.026778 - Under-five deaths*-0.240907 + Polio * 0.015004 + Diphtheria * 0.019319 - HIV/AIDS * 0.04161 - Thinness 1-19 years * 0.014641 + Thinness 5-9 years * 0.00426 + Status_Developed * 0.018438​​.

Groupwork statement: Chris performed exploratory data analysis and our KNN and linear ridge regressions, Justin undertook literature review and fitted our linear models, Marcus cleaned the initial dataset and performed neural network and logistic regressions.
"""