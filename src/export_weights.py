import os
import joblib
import numpy as np

def main():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    model_path = os.path.join(base_dir, "models", "energy_mlp.pkl")
    out_path = os.path.join(base_dir, "models", "energy_mlp_weights.npz")
    
    print(f"Loading pickled MLP model from: {model_path}...")
    model = joblib.load(model_path)
    
    # Extract coefficients and intercepts
    coefs = model.coefs_
    intercepts = model.intercepts_
    
    print(f"Model loaded successfully.")
    print(f"Number of layers: {len(coefs) + 1}")
    for i, (w, b) in enumerate(zip(coefs, intercepts)):
        print(f"  Layer {i+1} -> {i+2}: Weights shape = {w.shape}, Bias shape = {b.shape}")
        
    # Save as .npz archive
    print(f"Saving weights to: {out_path}...")
    np.savez(
        out_path,
        w1=coefs[0],
        b1=intercepts[0],
        w2=coefs[1],
        b2=intercepts[1],
        w3=coefs[2],
        b3=intercepts[2]
    )
    print("Export complete!")

if __name__ == "__main__":
    main()
