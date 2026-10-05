# Football Match Prediction with Von

This repository contains the research project for a master's thesis investigating the use of **Von**, an open-source System One model, for football match outcome prediction on English Premier League.

The study examines whether information contained in **pre-match football articles** can improve match outcome predictions, and how Von compares with conventional machine learning models based on structured statistical data.

## Research Objective

The main objective is to investigate how different types of information and modelling approaches can be combined to predict football match outcomes.

The study compares:

1. **Conventional machine learning models** trained on structured pre-match statistical data.
2. **Von fine-tuned on pre-match football articles**, using unstructured textual information from sources such as Sports Mole.
3. **Von fine-tuned on both football articles and structured statistical data**, examining whether Von can benefit from combining textual and numerical information.
4. **Hybrid models**, where Von's predictions are provided as additional features to conventional machine learning models.

The models will be evaluated using historical football match data while ensuring that only information available before each match is used for prediction.

## Experimental Setup

The project is structured around several modelling approaches:

```text
                    ┌─────────────────────────┐
                    │   Structured Statistics │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │ Conventional ML Models  │
                    └────────────┬────────────┘
                                 │
                                 │
┌──────────────────┐             │
│ Pre-match        │             │
│ football articles│             │
└────────┬─────────┘             │
         │                       │
         ▼                       │
┌──────────────────┐             │
│       Von        │─────────────┤
└────────┬─────────┘             │
         │                       │
         │ predictions           │
         ▼                       ▼
                 ┌──────────────────────┐
                 │    Hybrid Models     │
                 └──────────────────────┘
```

The main comparisons are:

* **Statistics → Conventional ML**
* **Articles → Von**
* **Articles + Statistics → Von**
* **Statistics + Von Predictions → Hybrid ML**

This allows the study to examine both the predictive value of textual information and whether Von provides information that complements conventional statistical models.

## Data

The textual component consists of **pre-match football articles**, with Sports Mole being used as a primary source of match previews.

The structured component consists of **pre-match statistical features** describing factors such as team performance and historical match characteristics.

An important principle of the study is to prevent **data leakage**. For each match, the models are only given information that would have been available before the match took place.

## Evaluation

The models will be evaluated using probabilistic and classification-based metrics. The primary evaluation will focus on the quality of the predicted outcome probabilities rather than simply whether the most likely outcome was correct.

Potential evaluation metrics include:

* Log loss
* Brier score
* Calibration
* Accuracy

The evaluation will use temporally appropriate train/validation/test splits to better reflect how the models would perform when predicting future matches.

## Research Questions

The study investigates questions such as:

1. How accurately can Von predict football match outcomes using pre-match football articles?
2. How does Von compare with conventional machine learning models trained on structured statistical data?
3. Does providing structured statistical data in addition to pre-match articles improve Von's predictions?
4. Do Von's predictions provide additional predictive information that can improve conventional machine learning models?
5. Does combining Von with conventional machine learning result in better predictions than either approach alone?

## Repository Structure

The repository will contain the code and supporting resources required for data collection, preprocessing, model training, prediction, evaluation, and analysis.

The structure may include:

```text
├── data/              # Data and processed datasets
├── src/               # Source code
├── models/            # Model configurations and saved models
├── results/           # Evaluation results
└── README.md
```

The exact structure may evolve as the research progresses.

## Status

This project is currently under development as part of a master's thesis. The experimental setup, data sources, model configurations, and evaluation methodology may be refined during the research process.
