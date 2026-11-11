### C1：每个数据集上“最佳 SMOTE” vs “最佳降采样”（AUC，5×2 CV）

| dataset     | under_sampler   |   under_auc | smote_sampler   |   smote_auc |    delta | winner    |
|:------------|:----------------|------------:|:----------------|------------:|---------:|:----------|
| pima        | rus100          |      0.788  | smote200        |      0.7817 |  -0.0063 | Under     |
| phoneme     | rus100          |      0.8941 | smote200        |      0.9026 |   0.0085 | SMOTE     |
| mammography | rus100          |      0.8938 | smote200        |      0.8977 |   0.0039 | SMOTE     |
| oil         | rus50           |      0.7924 | smote500        |      0.828  |   0.0356 | SMOTE     |
| satimage    | rus50           |      0.907  | smote100        |      0.9095 |   0.0026 | SMOTE     |
| qsar-biodeg | rus100          |      0.8405 | smote500        |      0.8724 |   0.0319 | SMOTE     |
| **合计**      |                 |    nan      |                 |    nan      | nan      | SMOTE 5/6 |
