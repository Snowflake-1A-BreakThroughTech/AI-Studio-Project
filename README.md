# Brooklyn Transport Demand Prediction Dashboard

### 👥 **Team Members**

| Name             | GitHub Handle | Contribution                                                             |
|------------------|---------------|--------------------------------------------------------------------------|
| Hannah Lee   | @lee-H1208 | OSM Data Collection & Preprocessing, Model Training and Evaluation, Streamlit Map Development |
| Charles Walford   | @charleswal-a | Data collection & Processing, Statistics and Scores Calculations, Streamlit Table Development |
| Emily Ren  | @seren5 | MTA Data Collection & Preprocessing, Data Visualization |
| Emily Olivares  | @ EmilyOliv | Data collection, Population Data Preprocessing and Statistics |

---

## 🎯 **Project Highlights**

- Developed a machine learning model using `HistGradientBoostingRegressor` to forecast transit demand by ZIP code in Brooklyn based on projected population increases.
- Achieved cross-validation score of 0.739, demonstrating high accuracy on the model’s insights into transportation deserts for [Snowflake](https://www.snowflake.com/en/).
- Generated actionable insights to inform business decisions at [Snowflake](https://www.snowflake.com/en/).
- Implemented a Streamlit application to generate visualizations that display needed information to address access to key healthcare amenities.

---

## 👩🏽‍💻 **Setup and Installation**

1. Clone the Repository
   ```bash
   git clone https://github.com/Snowflake-1A-BreakThroughTech/AI-Studio-Project.git
   cd src
   ```
2. Install Dependencies

   ```bash
   pip install sklearn, snowflake, notebook, matplotlib, numpy
   ```

3. Run the Notebook
   ```bash
   jupyter notebook ModelTrainingandEvaluation.ipynb
   ```
4. Run the Streamlit Application
   ```bash
   streamlit run streamlit_app.py
   ```

---

## 🏗️ **Project Overview**

This ML Challenge Project of navigating healthcare deserts was assigned to us by Snowflake, where we analyzed real-world data sets and identified patterns and relationships with the guidance of our AI Studio Coach and Challenge Advisors.

Our AI Studio host company was [Snowflake](https://www.snowflake.com/en/), and our project objective and scope was to identify vulnerable areas where the residents might have difficulties on having access to transportation, as low access to transit causes low access to healthcare amenities. We aimed to analyze gaps and risks that highlight the areas with the most needs, particularly with increases in population.

New York City suffers from borough inequality, and many parts of Brooklyn do not have the transportation access they need to access different facilities such as healthcare. Our work is designed for: 
Urban planners and transportation agencies seeking to identify neighborhoods with limited access to public transportation
Local government officials and community organizations working to allocate resources and advocate for better transit options
Residents living in transportation deserts who may benefit from improved transit accessibility and planning efforts

---

## 📊 **Data Exploration**

* **Datasets**: Open Street Map (OSM) and MTA Data, Snowflake Marketplace and MTA, 
* **Data format**: .csv files
* **Data preprocessing**: Fixing null and missing values, Calculated zip code statistics, Finding amenity locations and associated zip codes
* **Challenges**: Lack of robust and relevant data, Lack of zipcode grouping to combine datasets
---

## 🧠 **Model Development**

Using `make_pipeline()`:
* `SimpleImputer`: To handle missing values using median
* `HistGradientBoostingRegressor`: Main prediction model

### Hyperparameter Tuning

**Goal**: Maximize cross-validated R2 score while avoiding overfitting.
* `KFold Cross-Validation`
* `RandomizedSearchCV`

---

## 📈 **Results & Key Findings**

### Model Evaluation Results

<div align="center">
  
| Training R2 | CV R2 |
|:-----------:|:-----:|
|    0.998    | 0.739 |

</div>

* The training R2 is extremely high, telling us that the model is able to fit the patterns in the training data very accurately. This is also shown by the blue line.
* The cross-validation R2 is a bit lower. This gap is expected because we have a relatively small dataset consisting of only 37 zip codes, which naturally causes variability.
* The red line on the learning curve shows this. We see it steadily increase and stabilize, which means the model generalizes better with more examples.
* The shaded area represents variance between folds, which again shows that with more data, we would likely improve performance even further.

### Project Results & Key Findings

* The heat maps suggest the formation of demand clusters in areas of Brooklyn depending on the population size.
* Increases in population would most likely affect Central and South Brooklyn the most.
* The most impacted zip codes contain areas with high population density and few immediate subway options.




---

## 🚀 **Next Steps**

1. Expand to healthcare or food demand to help allocate resources to underserved communities.
2. Incorporate demographic and infrastructure features for more accurate predictions.
3. Improve our dashboard by making it more dynamic for users to explore “what-if” scenarios.
4. Overlay MTA data onto the map to visualize how public transit accessibility relates to demand patterns.

---

## 📝 **License**

This project is licensed under the MIT License.

---

## 📄 **References** 

* [UT Urban Information Lab - Transit Desert Dashboard](https://sites.utexas.edu/uil/2024/07/27/developing-a-transit-desert-interactive-dashboard-supervised-modeling-for-forecasting-transit-deserts/)
* [USF Transit Deserts Paper](https://digitalcommons.usf.edu/cgi/viewcontent.cgi?article=1054&context=jpt)

---

## 🙏 **Acknowledgements** 

Thank you to our Challenge Advisors, Joe Warbington and Tess Dicker, and our AI Studio Coach Abhijay Rane for the amazing support throughout the program!
