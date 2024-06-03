# GENERAL STOCK PREDICTIONS

[![CD](https://github.com/THEWhiteArrow/ml-general-stock-predictions/actions/workflows/github-action-cd.yml/badge.svg)](https://github.com/THEWhiteArrow/ml-general-stock-predictions/actions/workflows/github-action-cd.yml)
[![CI](https://github.com/THEWhiteArrow/ml-general-stock-predictions/actions/workflows/github-action-ci.yml/badge.svg)](https://github.com/THEWhiteArrow/ml-general-stock-predictions/actions/workflows/github-action-ci.yml/badge.svg)
![GitHub Latest Release)](https://img.shields.io/github/v/release/THEWhiteArrow/ml-general-stock-predictions?logo=github)

## Introduction

This project aims to forecast the stock prices of multiple companies using a machine learning model. The dataset used in this project is obtained from Yahoo Finance.

## Phase 1

All the data is automatically gathered and basic analysis is performed.
Model is trained and capable of saving the predictions for the upcoming days.

## Phase 2

The results of predictions are persisted in cloud storage. The databse of choise is MongoDb.

## Visual Studio Code

The project is developed using dev containers in Visual Studio Code. The dev container is based on the `Python 3` image. The dev container is configured to use the `Python 3.12` interpreter.

## Installation

Project is based on poetry for dependency management. To install the dependencies, run the following command in the root directory of the project:

```bash
make install
```

## Dataset

The dataset used in this project is obtained from:

-   Yahoo Finance

The gathering of the dataset is fully automated meaning it can be updated at any time to include the latest data. The dataset is stored in the `data` directory.

To update the dataset, run the following command:

```bash
make scrape
```
