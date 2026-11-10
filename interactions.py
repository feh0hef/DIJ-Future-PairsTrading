import torch
from statistics.cov import signal_correlation, cluster_signal_correlation, run_inter_cluster_analysis, save_covariances_to_json

def main():
    print("Starting daily inter-cluster negative covariance pipeline...")
    
    
    matrix = signal_correlation()
    
    clusters, model = cluster_signal_correlation(matrix, k=6)
    print(f"Clustering process completed. {len(clusters)} contracts successfully mapped.")

 
    cov_results = run_inter_cluster_analysis(matrix, clusters, sample=False)
    print("PyTorch cross-covariance matrix processing successfully completed.")


    save_covariances_to_json(matrix, clusters, cov_results, filename="daily_covariance.json")

if __name__ == "__main__":
    main()