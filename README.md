# Phishing URL Detection with PhishTransformer

A research and application project for detecting phishing URLs with character-level deep learning. The project compares a CNN baseline, a Transformer model, and a hybrid CNN + Transformer model, then exposes the trained model through a small Flask web application.

**Student:** Sarmad Ali (i22-1997)

## Research Paper

**Base paper:** Asiri, S., Xiao, Y., Li, T., and other authors, "PhishTransformer: A Novel Approach to Detect Phishing Attacks Using URL Collection and Transformer," *Electronics*, 13(1), Article 30, 2024.

- DOI: [10.3390/electronics13010030](https://doi.org/10.3390/electronics13010030)
- Paper page: [MDPI Electronics](https://www.mdpi.com/2079-9292/13/1/30)

### Technique used in the paper

The paper proposes a deep-learning system that:

1. Collects URLs embedded in webpage content, including hyperlinks and iframes.
2. Uses convolutional layers to learn local URL patterns.
3. Uses Transformer encoder layers and self-attention to learn long-range relationships.
4. Combines the extracted features in a classifier.
5. Predicts whether the webpage is legitimate or phishing.

The paper reports experiments on 10,000 URLs and reports approximately 99% F1-score, precision, and recall for its own experimental setup. Those values are paper results and are not claimed as results of this repository.

### Adaptation in this project

This project follows the paper's local-pattern plus global-context idea, but uses URL strings only. The PhishTank and Tranco files provide URL/domain text rather than webpage HTML. Therefore, this project does not claim to reproduce the paper's webpage-content collection pipeline.

The implementation uses:

- Character-level URL encoding
- Maximum URL length: 256 characters
- Embedding dimension: 128
- CNN kernels: 3 and 5
- Transformer attention heads: 4
- Transformer blocks: 2
- Feed-forward dimension: 256
- Binary sigmoid classifier

## Models

Three models are trained for comparison:

| Model | Purpose |
|---|---|
| CNN-only | Baseline for local character patterns such as suspicious tokens and separators |
| Transformer-only | Baseline for long-range dependencies across the URL |
| Hybrid CNN + Transformer | Proposed model combining local and global URL features |

### Model flow

```text
URL string
  -> normalization and character encoding
  -> embedding layer, 128 dimensions
  -> CNN branch and/or Transformer encoder branch
  -> global pooling
  -> Dense(128) + Dropout(0.2)
  -> sigmoid output
  -> legitimate or phishing
```

## Datasets

Download the two raw URL sources from their official sources and place them in `Dataset/`:

| File | Source | Label | Reference size |
|---|---|---|---:|
| `verified_online.csv` | [PhishTank](https://phishtank.org/) | Verified phishing | 50,602 |
| `top-1m.csv` | [Tranco](https://tranco-list.eu/) | Legitimate domains | 1,000,000 |

The notebook cleans URLs, removes duplicates, balances the two classes using the smaller class size, and performs an 80/20 stratified train/test split. The final counts are calculated from the files available locally and must be reported from the actual run.

## Project Structure

```text
Phishing-URL-Detection/
├── Dataset/
│   ├── verified_online.csv
│   └── top-1m.csv
├── notebooks/
│   └── Phishing_URL_Detection_Final.ipynb
├── app/
│   ├── app.py
│   ├── templates/index.html
│   └── static/
│       ├── style.css
│       └── script.js
├── models/                         # Created after training
│   ├── final_phishing_model.keras
│   └── vocab.json
├── results/                        # Created after evaluation
├── test_urls.txt
├── requirements.txt
└── README.md
```

## Notebook Workflow

The final notebook contains these sections:

1. Introduction
2. Dataset loading
3. Data cleaning
4. Exploratory data analysis
5. Character-level URL encoding
6. Data balancing
7. Train/test split
8. CNN model
9. Transformer model
10. Hybrid CNN + Transformer model
11. Base paper technique adaptation
12. Model training
13. Evaluation
14. Accuracy, precision, recall, and F1-score
15. Confusion matrix
16. ROC-AUC
17. Model comparison
18. Test sample URLs
19. Save final model
20. Prediction function

The notebook saves:

- `models/final_phishing_model.keras`
- `models/vocab.json`
- `results/metrics.csv`
- `results/confusion_matrix.png`
- `results/roc_curve.png`

## Installation

Use Python 3.8 or newer. TensorFlow installation may vary by operating system and hardware.

```bash
python -m pip install -r requirements.txt
```

## Run the Notebook

1. Download and place the two datasets in `Dataset/`.
2. Open `notebooks/Phishing_URL_Detection_Final.ipynb`.
3. Run the cells from top to bottom.
4. Review the generated metrics and plots in `results/`.

```bash
jupyter notebook notebooks/Phishing_URL_Detection_Final.ipynb
```

Do not copy historical metrics into the final report unless the current run reproduces them. Accuracy, precision, recall, F1-score, and AUC must come from the current dataset split and trained model.

## Flask Website

The Flask application provides a browser interface for entering a URL and receiving:

- Normalized URL
- Prediction: `PHISHING` or `LEGITIMATE`
- Model confidence
- A short interpretation of the prediction

Start it from the project root after installing requirements and running the notebook:

```bash
python app/app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in a browser.

The app loads `models/final_phishing_model.keras` and `models/vocab.json`. If those files do not exist, it displays a clear "model not loaded" state and does not fabricate a prediction.

The application is a research demonstration, not a browser security product. Do not visit suspicious URLs merely to test them.

## Test URLs

`test_urls.txt` contains 15 legitimate URL fixtures and 15 phishing-pattern fixtures. The phishing fixtures use reserved `.invalid` domains so they cannot resolve and should not be presented as live phishing-feed observations. For an academically valid dataset test, replace them with labeled rows exported from PhishTank and record the source and download date.

## Evaluation Metrics

- **Accuracy:** overall proportion of correct predictions
- **Precision:** proportion of predicted phishing URLs that are phishing
- **Recall:** proportion of phishing URLs detected by the model
- **F1-score:** harmonic mean of precision and recall
- **ROC-AUC:** ranking quality across classification thresholds
- **Confusion matrix:** counts of true/false legitimate and phishing predictions

Because phishing detection is a security task, recall and false-negative errors deserve particular attention. A high accuracy score alone is not sufficient, especially when class balance or dataset source changes.

## Limitations

- The model analyzes URL text and does not inspect page HTML, scripts, screenshots, certificates, or DNS records.
- Dataset quality, duplication, source age, and class balance affect the reported metrics.
- A prediction is a statistical signal, not proof that a URL is safe.
- The base paper's webpage-content URL collection is not implemented in this URL-only adaptation.
- Results must be regenerated when the dataset, split, preprocessing, or model configuration changes.

## References

1. Asiri, S. et al. (2024). *PhishTransformer: A Novel Approach to Detect Phishing Attacks Using URL Collection and Transformer*. Electronics, 13(1), 30. [DOI](https://doi.org/10.3390/electronics13010030)
2. [PhishTank](https://phishtank.org/)
3. [Tranco Research URL Ranking](https://tranco-list.eu/)
