# Character-Level CNN and Transformer Models for Phishing URL Detection
## A URL-Only Adaptation of PhishTransformer

**Term Paper**  
**Project:** Phishing URL Detection with PhishTransformer  
**Course:** Applied Machine Learning  
**Date:** October 2026

## Abstract

Phishing attacks use deceptive URLs to obtain credentials, payment information, and other sensitive data. This project evaluates character-level deep learning for binary phishing URL classification. It adapts the local-plus-global design motivation of PhishTransformer by comparing a CNN-only model, a Transformer-only model, and a hybrid CNN + Transformer model under the same data split and training budget. Phishing URLs are taken from the verified PhishTank feed and legitimate domains from the Tranco top-million list. URLs are lowercased, whitespace is removed, HTTP/HTTPS schemes and leading `www.` are canonicalized, and each URL is encoded as a 256-character sequence.

Because the available CPU environment could not train the full source pool, a reproducible balanced sample of 1,000 URLs per class is used. The 2,000 URLs are split stratified 80/20 into 1,600 training and 400 test examples. In the final clean run, CNN-only and the hybrid model both obtain 99.25% accuracy and 99.24% F1-score; the hybrid has ROC-AUC 99.57%. The Transformer-only model obtains 91.75% accuracy and 91.25% F1-score under the same two-epoch budget. The hybrid is saved for deployment, with a tie-break that prefers the proposed hybrid architecture. These results are not directly comparable to the base paper's approximately 99% precision, recall, and F1 because the sources, labels, collection process, and evaluation protocol differ.

**Keywords:** phishing detection, URL classification, character-level modeling, CNN, Transformer, self-attention, cybersecurity, Flask.

## 1. Introduction

A URL is available before a browser loads a webpage, making it a useful early detection surface. Attackers can manipulate domain names, subdomains, separators, paths, digits, and brand-related tokens to make malicious URLs appear trustworthy. Blacklists are useful for known threats but cannot reliably identify newly created URLs. Hand-engineered lexical features can also require continual adaptation.

This project asks whether a character-level model can learn useful URL representations directly from strings. The study compares local pattern learning through convolution, long-range contextual modeling through Transformer self-attention, and a hybrid architecture that combines both.

### Objectives

- Build a reproducible character-level URL preprocessing pipeline.
- Compare CNN-only, Transformer-only, and hybrid CNN + Transformer models.
- Report accuracy, precision, recall, F1-score, ROC-AUC, and confusion matrices.
- Deploy the selected model through a Flask web interface.
- Compare the project scope and results with the cited PhishTransformer paper without claiming exact reproduction.

## 2. Base Paper and Related Work

Asiri et al. proposed PhishTransformer, which combines convolutional feature extraction with Transformer encoding. Its data collection process extracts URLs embedded in webpage content, including hyperlinks and iframes. The paper reports approximately 99% precision, recall, and F1-score and an average five-fold accuracy of 0.989 for its experimental setup.

This project preserves the local-plus-global architectural motivation but changes the input scope to URL strings. It does not collect webpage HTML, inspect scripts, use screenshots, query DNS, or reproduce the base paper's exact datasets. Other URL research includes lexical analysis on ISCX-URL2016, character and word convolutional representations such as URLNet, and Transformer-based URL models such as URLTran.

## 3. Dataset and Scope

The final project uses only raw URL/domain sources:

| File | Source | Label | Use |
|---|---|---:|---|
| `verified_online.csv` | PhishTank | 1 | Verified phishing URL strings |
| `top-1m.csv` | Tranco | 0 | Popular legitimate domains |

After normalization and de-duplication, the available pool contains approximately 68,471 phishing URLs and 999,996 legitimate domains. To keep the experiment executable in the available CPU environment, the pipeline samples 1,000 examples from each class using random seed 42.

## 4. Methodology

### 4.1 Normalization and encoding

Each value is lowercased and whitespace is removed. Existing `http://` or `https://` prefixes and a leading `www.` are removed, then a uniform `http://` prefix is added. This prevents the source-specific scheme from becoming a shortcut. Duplicate and empty values are discarded.

Characters are mapped to integer IDs. `<PAD>` has index 0 and `<UNK>` has index 1. URLs are truncated or right-padded to 256 characters. In the final run, the vocabulary contains 59 symbols. The balanced data has shape $2000 \times 256$; the stratified split produces 1,600 training and 400 test URLs.

### 4.2 CNN-only model

The CNN model uses a 128-dimensional character embedding followed by two one-dimensional convolution layers with 128 filters and kernel sizes 3 and 5. ReLU activations and same padding preserve local sequence structure. Global max pooling creates a fixed representation for a dense 128-unit ReLU layer, dropout 0.2, and a sigmoid output.

### 4.3 Transformer-only model

The Transformer model uses the same embedding and two Transformer blocks. Each block has four-head self-attention, residual connections, layer normalization, and a feed-forward network with dimensions 256 and 128. Global average pooling precedes the shared classifier. The implementation does not include positional embeddings, which limits the model's ability to distinguish character order.

### 4.4 Hybrid model

The hybrid model applies a convolution with kernel size 3 before two Transformer blocks. The convolution captures local, order-aware patterns while self-attention models longer relationships. This is the closest adaptation of the base paper's local-plus-global architecture.

### 4.5 Training

All models use Adam with learning rate 0.0001, binary cross-entropy, batch size 8, and two maximum epochs. Early stopping and learning-rate reduction use patience 1. The short budget is a resource constraint; the Transformer-only model should not be interpreted as fully optimized.

For a binary prediction, the classifier estimates $p(y=1\mid u)$ and predicts phishing when the probability is at least 0.5. Binary cross-entropy is:

$$L=-\frac{1}{N}\sum_i[y_i\log(\hat p_i)+(1-y_i)\log(1-\hat p_i)]$$

## 5. Results

| Model | Accuracy | Precision | Recall | F1-score | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| CNN-only | 99.25% | 100.00% | 98.50% | 99.24% | 99.56% |
| Transformer-only | 91.75% | 97.18% | 86.00% | 91.25% | 97.66% |
| Hybrid CNN + Transformer | 99.25% | 100.00% | 98.50% | 99.24% | 99.57% |

The hybrid model is selected when it ties the CNN-only model on F1-score. The generated artifacts are `results/metrics.csv`, `results/confusion_matrix.png`, `results/roc_curve.png`, `models/final_phishing_model.keras`, and `models/vocab.json`.

The included `test_urls.txt` and `test_urls.csv` are offline fixtures, not independent real-world evaluation data. The live website correctly classifies all 30 included fixtures after the normalization fixes, but this result should not be presented as a production benchmark because the fixtures are synthetic and structurally simple.

## 6. Comparison with the Base Paper

| Dimension | Base PhishTransformer paper | This project |
|---|---|---|
| Input | URLs collected from webpage content, including hyperlinks and iframes | URL strings and domains only |
| Phishing sources | PhishArmy and PhishTank | PhishTank verified feed |
| Legitimate source | Alexa-based benign URLs | Tranco top-million domains |
| Architecture | CNN + Transformer | CNN-only, Transformer-only, and hybrid comparison |
| Reported best result | Approximately 99% precision, recall, and F1; five-fold accuracy 0.989 | Hybrid: 99.25% accuracy, 99.24% F1, 99.57% ROC-AUC |
| Exact comparability | Not applicable | Different data and protocol |

The scores are numerically close, but they do not establish that one system is better. The project uses a small balanced sample, a random split, and a two-epoch budget. Future evaluation should use path-matched legitimate URLs, domain-grouped and temporal splits, repeated seeds, longer training, and calibration analysis.

## 7. Human-Computer Interaction and Deployment

The Flask interface provides a focused workflow: enter a URL, submit it, and receive a label, confidence, normalized URL, and explanation. The interface does not visit the URL, which reduces risk during testing. The application exposes `POST /api/analyze` and loads the same vocabulary and normalization behavior used during training.

The interface is a research demonstration, not a browser security product. It has no authentication, rate limiting, monitoring, probability calibration, or adversarial robustness guarantee. A production interface should communicate uncertainty clearly, avoid presenting confidence as proof of safety, and provide accessible error states.

## 8. Limitations and Future Work

- The two source classes have different collection processes and may contain source-specific shortcuts.
- A random URL split may place related domains or campaigns in both partitions.
- The 2,000-sample experiment and two-epoch budget limit generalization claims.
- The Transformer has no positional encoding.
- URL-only analysis does not inspect webpage content, DNS, certificates, redirects, or hosting.

Future work should add legitimate URLs with paths, train on the full phishing feed, add positional embeddings, use validation-only model selection, evaluate grouped and chronological splits, compare against numeric-feature models using ISCX-URL2016, and test adversarial and homoglyph variants.

## 9. Conclusion

This project demonstrates a reproducible URL-only adaptation of the local-plus-global PhishTransformer idea. The hybrid model matches the CNN baseline at 99.25% accuracy and 99.24% F1 on the current controlled test split, while the Transformer-only model performs lower under the same short training budget. The result is promising as a prototype but should not be treated as evidence of real-world 99% detection because the source distributions and evaluation protocol contain important structural differences.

## References

1. S. Asiri et al., “PhishTransformer: A Novel Approach to Detect Phishing Attacks Using URL Collection and Transformer,” *Electronics*, vol. 13, no. 1, 2024. DOI: 10.3390/electronics13010030.
2. H. Le et al., “URLNet: Learning a URL Representation with Deep Learning for Malicious URL Detection,” arXiv:1802.03162, 2018.
3. P. Maneriker et al., “URLTran: Improving Phishing URL Detection Using Transformers,” arXiv:2106.05256, 2021.
4. P. Xu, “A Transformer-Based Model to Detect Phishing URLs,” arXiv:2109.02138, 2021.
5. M. S. I. Mamun et al., “Detecting Malicious URLs Using Lexical Analysis,” NSS 2016.
6. PhishTank, https://phishtank.org/
7. Tranco, https://tranco-list.eu/
