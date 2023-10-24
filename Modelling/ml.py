import xgboost

model = xgboost.Booster()
model.load_model('Modelling/model.tar.gz')

import shap
import xgboost


# Load your model
model = xgboost.Booster()
model.load_model('path_to_your_model_artifact')

# Compute SHAP values
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X)

# Plot the SHAP values for a single prediction
shap.force_plot(explainer.expected_value, shap_values[0,:], X.iloc[0,:])

# Plot summary of SHAP values for all features
shap.summary_plot(shap_values, X)
