# TODO:

# NOTES AND OBSERVATIONS

-   the model is to be trained on the stocks historical data that includes main features such as:

    -   close price
    -   stock area
    -   stock volume

-   the model is to predict the prices of the stocks
-   the data for the model should be pulled at the end of trading day so that todays data can be used - **IMPORTANT**
-   the hyperparameters may cause the model to over generalise data and minimise the loss function by predicting straight line - **IMPORTANT**

# PROJECT FUTURE

-   instead of predicting the price, the model should predict the relationshiip ratio between stock prices

    -   for each stocks data teh close price and volume should be standardized
    -   into calculations the rations should eb included and later inversed to retrive the price
    -   this way the model will be able to focus less on the raw prices but more on real life stocks trading behaviours

-   the model should include relevant sentimenatl events into predictions
-   notify which stocks do no make sense to include in the model (number of NaN is too high)
