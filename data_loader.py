import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler

def load_wban_data(csv_path):
    """
    Loads 'wban_har.csv', engineers features, scales, and splits by Person ID.
    """
    df = pd.read_csv(csv_path)
    
    # 1. Feature Engineering: Extract statistical features from accelerometer data
    # This is CRITICAL for HAR (Human Activity Recognition) tasks
    features = []
    labels = []
    persons = []
    
    # Window size for feature extraction (50 samples = ~1 second at 50Hz)
    window_size = 50
    
    for person in df['Person'].unique():
        person_data = df[df['Person'] == person]
        
        # Slide window through the data
        for i in range(0, len(person_data) - window_size, window_size // 2):
            window = person_data.iloc[i:i+window_size]
            
            if len(window) < window_size:
                continue
            
            # Extract features from each window
            feature_vector = []
            
            for axis in ['Acc_x', 'Acc_y', 'Acc_z']:
                values = window[axis].values
                
                # Time-domain features
                feature_vector.extend([
                    np.mean(values),           # Mean
                    np.std(values),            # Standard deviation
                    np.max(values),            # Maximum
                    np.min(values),            # Minimum
                    np.max(values) - np.min(values),  # Range
                    np.median(values),         # Median
                    np.percentile(values, 25), # 25th percentile
                    np.percentile(values, 75), # 75th percentile
                ])
                
                # Frequency-domain features (simple)
                fft_values = np.abs(np.fft.fft(values))[:window_size//2]
                feature_vector.extend([
                    np.mean(fft_values),       # Mean frequency magnitude
                    np.std(fft_values),        # Std of frequency magnitude
                    np.max(fft_values),        # Dominant frequency strength
                ])
            
            # Cross-axis features
            feature_vector.extend([
                np.sqrt(np.sum(window[['Acc_x', 'Acc_y', 'Acc_z']].values**2, axis=1)).mean(),  # Signal magnitude area
                np.corrcoef(window['Acc_x'], window['Acc_y'])[0,1],  # X-Y correlation
                np.corrcoef(window['Acc_x'], window['Acc_z'])[0,1],  # X-Z correlation
                np.corrcoef(window['Acc_y'], window['Acc_z'])[0,1],  # Y-Z correlation
            ])
            
            features.append(feature_vector)
            labels.append(window['Class'].mode()[0])  # Most common class in window
            persons.append(person)
    
    # Convert to numpy arrays
    X = np.array(features)
    
    # 2. Label Encoding: Convert Activity names to numbers (0-4)
    le = LabelEncoder()
    y = le.fit_transform(labels)
    persons = np.array(persons)
    
    # 3. Scaling: CRITICAL for neural networks
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # 4. Federated Split: Group data by 'Person' column
    federated_data = {}
    person_ids = np.unique(persons)
    
    for pid in person_ids:
        mask = persons == pid
        X_p = X_scaled[mask]
        y_p = y[mask]
        
        # Split into training and test sets per node (80/20 split)
        split = int(len(X_p) * 0.8)
        
        # Shuffle the data before splitting
        indices = np.random.permutation(len(X_p))
        X_p = X_p[indices]
        y_p = y_p[indices]
        
        federated_data[pid] = {
            'X_train': X_p[:split], 
            'y_train': y_p[:split],
            'X_test': X_p[split:], 
            'y_test': y_p[split:]
        }
    
    print(f"✓ Data loaded: {len(X)} samples, {X.shape[1]} features, {len(person_ids)} nodes")
    print(f"✓ Class distribution: {np.bincount(y)}")
        
    return federated_data, le, X.shape[1]
