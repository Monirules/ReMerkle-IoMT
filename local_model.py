import numpy as np
from sklearn.ensemble import RandomForestClassifier
import warnings
warnings.filterwarnings('ignore')

def create_har_model(num_classes, input_shape):
    """
    Creates a Random Forest Classifier for Human Activity Recognition.
    This works better for federated learning without complex weight sync.
    """
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=15,
        min_samples_split=10,
        min_samples_leaf=4,
        random_state=42,
        n_jobs=-1,
        warm_start=False
    )
    
    return model

def train_local_model(model, X_train, y_train):
    """
    Step 1: Local Training.
    Trains the model locally on node data.
    """
    model.fit(X_train, y_train)
    
    # For Random Forest, we return the trees as "weights"
    weights = {
        'estimators': model.estimators_,
        'classes': model.classes_,
        'n_classes': model.n_classes_,
        'n_features_in': model.n_features_in_
    }
    
    return weights

def set_model_weights(model, weights):
    """
    Set model weights (trees) from aggregated weights.
    """
    if not weights or not isinstance(weights, dict):
        return model
    
    try:
        # For aggregated trees, we need to merge them
        if 'estimators' in weights:
            model.estimators_ = weights['estimators']
            model.classes_ = weights['classes']
            model.n_classes_ = weights['n_classes']
            model.n_features_in_ = weights['n_features_in']
            model._sklearn_is_fitted = True
    except Exception as e:
        pass
    
    return model

def evaluate_model(model, X_test, y_test):
    """
    Evaluate model accuracy.
    """
    try:
        score = model.score(X_test, y_test)
        return score
    except:
        return 0.2

def get_model_entropy(model, X_test, num_classes):
    """
    Step 2 / Gate 3: The Quality Check.
    Measures prediction confidence.
    """
    try:
        probs = model.predict_proba(X_test)
        entropy = -np.sum(probs * np.log(probs + 1e-9), axis=1)
        return np.mean(entropy)
    except:
        return 2.0
