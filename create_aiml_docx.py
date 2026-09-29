import os
import sys
import zipfile

def escape_xml(text):
    if not text:
        return ""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")

def generate_minimal_docx(output_path, title, subtitle, content_blocks):
    """
    Generate a valid Microsoft Word .docx file using standard python zipfile library.
    Zero external dependencies required!
    """
    # 1. document.xml
    body_xml_parts = []
    
    # Title
    body_xml_parts.append(f'<w:p><w:pPr><w:jc w:val="center"/><w:rPr><w:b/><w:sz w:val="36"/><w:color w:val="1E293B"/></w:rPr></w:pPr><w:r><w:rPr><w:b/><w:sz w:val="36"/><w:color w:val="1E293B"/></w:rPr><w:t>{escape_xml(title)}</w:t></w:r></w:p>')
    
    if subtitle:
        body_xml_parts.append(f'<w:p><w:pPr><w:jc w:val="center"/><w:rPr><w:i/><w:sz w:val="22"/><w:color w:val="64748B"/></w:rPr></w:pPr><w:r><w:rPr><w:i/><w:sz w:val="22"/><w:color w:val="64748B"/></w:rPr><w:t>{escape_xml(subtitle)}</w:t></w:r></w:p>')
    
    body_xml_parts.append('<w:p/>')

    for block in content_blocks:
        heading = block.get('heading', '')
        if heading:
            body_xml_parts.append(f'<w:p><w:pPr><w:rPr><w:b/><w:sz w:val="26"/><w:color w:val="1E40AF"/></w:rPr></w:pPr><w:r><w:rPr><w:b/><w:sz w:val="26"/><w:color w:val="1E40AF"/></w:rPr><w:t>{escape_xml(heading)}</w:t></w:r></w:p>')
        
        for p_info in block.get('paragraphs', []):
            bold_prefix = p_info.get('bold_prefix', '')
            text = p_info.get('text', '')
            
            p_xml = '<w:p><w:pPr><w:rPr><w:sz w:val="22"/></w:rPr></w:pPr>'
            if bold_prefix:
                p_xml += f'<w:r><w:rPr><w:b/><w:sz w:val="22"/><w:color w:val="0F172A"/></w:rPr><w:t>{escape_xml(bold_prefix)} </w:t></w:r>'
            if text:
                p_xml += f'<w:r><w:rPr><w:sz w:val="22"/><w:color w:val="334155"/></w:rPr><w:t>{escape_xml(text)}</w:t></w:r>'
            p_xml += '</w:p>'
            body_xml_parts.append(p_xml)
        
        body_xml_parts.append('<w:p/>')

    doc_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:body>
        {''.join(body_xml_parts)}
    </w:body>
</w:document>"""

    content_types_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""

    rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

    doc_rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>"""

    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('[Content_Types].xml', content_types_xml)
        zf.writestr('_rels/.rels', rels_xml)
        zf.writestr('word/document.xml', doc_xml)
        zf.writestr('word/_rels/document.xml.rels', doc_rels_xml)

def escape_xml(text):
    if not text:
        return ""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")


qa_pairs = [
    {
        "q_num": 1,
        "question": "Explain Supervised vs. Unsupervised Learning with real-world applications.",
        "model_answer": (
            "Supervised learning is a machine learning paradigm where models are trained on labeled datasets containing both input features and corresponding target output labels. "
            "The algorithm learns a mapping function from inputs to outputs by minimizing a loss function during training. Common algorithms include Linear Regression, Support Vector Machines (SVM), and Random Forests. "
            "Real-world applications include email spam detection, credit scoring, medical disease diagnosis, and image classification. "
            "In contrast, unsupervised learning processes unlabeled datasets where no target output labels are provided. The goal is to discover hidden patterns, underlying structures, clusters, or probability distributions within the data. "
            "Key algorithms include K-Means clustering, Hierarchical clustering, and Principal Component Analysis (PCA) for dimensionality reduction. "
            "Real-world applications include customer market segmentation, anomaly detection in financial transactions, and recommendation engine feature clustering."
        ),
        "student_answer": (
            "Supervised learning trains machine learning models using labeled data where every training example includes input features and expected target labels. "
            "The model learns to predict outputs for unseen data by reducing classification or regression error. Examples include spam filtering, image recognition, and medical diagnostics. "
            "Algorithms used are Decision Trees, Support Vector Machines, and Logistic Regression. "
            "Unsupervised learning deals with completely unlabeled data where target outputs are absent. The algorithm autonomously groups data points based on feature similarity and distance metrics. "
            "Algorithms like K-Means and Principal Component Analysis (PCA) are used for customer segmentation, anomaly detection, and data visualization without prior human labeling."
        ),
        "key_concepts": "labeled data, mapping function, classification, regression, unlabeled data, clustering, K-Means, PCA, customer segmentation",
        "max_marks": 10.0
    },
    {
        "q_num": 2,
        "question": "Describe Overfitting and Underfitting in Machine Learning and strategies to mitigate them.",
        "model_answer": (
            "Overfitting occurs when a machine learning model learns the training data excessively well, including noise, outliers, and random fluctuations, rather than capturing the underlying general distribution. "
            "An overfitted model achieves near-zero error on training data but exhibits high error and poor generalization on unseen validation or test data. "
            "Causes include excessive model complexity, deep decision tree depth, and insufficient training data volume. Strategies to mitigate overfitting include applying L1 (Lasso) and L2 (Ridge) regularization, implementing dropout in neural networks, pruning decision trees, performing cross-validation, and acquiring additional training datasets. "
            "Underfitting occurs when a model is overly simplistic and fails to capture the core relationships in the dataset, resulting in high error on both training and test data. "
            "Mitigation techniques include increasing model complexity, introducing polynomial features, reducing regularization intensity, and training for more iterations."
        ),
        "student_answer": (
            "Overfitting happens when a model becomes too complex and memorizes the training data, including noise and random outliers. "
            "As a result, training accuracy is extremely high, but test accuracy drops significantly due to poor generalization. "
            "To prevent overfitting, developers use regularization techniques like L1 and L2 penalty, apply dropout in deep neural networks, use K-fold cross-validation, and prune decision tree nodes. "
            "Underfitting occurs when a model is too simple to capture patterns in the data, leading to low accuracy on both training and test sets. "
            "Underfitting is fixed by using more complex architectures, adding relevant polynomial features, and decreasing regularization constraints."
        ),
        "key_concepts": "overfitting, underfitting, memorizes noise, generalization error, L1 L2 regularization, dropout, tree pruning, model complexity",
        "max_marks": 10.0
    },
    {
        "q_num": 3,
        "question": "Explain the Bias-Variance Tradeoff and its impact on model generalization performance.",
        "model_answer": (
            "The Bias-Variance Tradeoff is a fundamental concept in supervised machine learning that describes the balance between two sources of error that prevent learning algorithms from generalizing beyond their training set. "
            "Bias represents the error introduced by approximating a real-world complex problem using a simplified model assumptions. High bias leads to underfitting, where the model misses relevant relations between features and targets. "
            "Variance represents the model's sensitivity to small fluctuations in the training dataset. High variance leads to overfitting, where the model fits random noise instead of intended signal. "
            "Total generalization error is the sum of squared bias, variance, and irreducible error. "
            "Achieving optimal generalization performance requires selecting a model complexity that minimizes the total error, balancing low bias and low variance through hyperparameter tuning, ensemble methods like Random Forests (variance reduction), and boosting algorithms (bias reduction)."
        ),
        "student_answer": (
            "The Bias-Variance Tradeoff balances two types of errors in machine learning models to maximize prediction accuracy on unseen test data. "
            "Bias measures how much model predictions deviate from actual target values due to oversimplified assumptions. High bias causes underfitting because the model cannot capture underlying trends. "
            "Variance measures how sensitive the model is to small changes in training data. High variance causes overfitting because the model adapts to noisy data points. "
            "Total error equals bias squared plus variance plus irreducible error. "
            "To find the sweet spot, engineers tune hyperparameters, apply ensemble techniques like Bagging to lower variance, and use Boosting algorithms to lower bias."
        ),
        "key_concepts": "bias variance tradeoff, underfitting, simplified assumptions, sensitivity to noise, overfitting, total error, model generalization, hyperparameter tuning",
        "max_marks": 10.0
    },
    {
        "q_num": 4,
        "question": "Explain the Architecture and Working Principles of Convolutional Neural Networks (CNNs).",
        "model_answer": (
            "Convolutional Neural Networks (CNNs) are specialized deep feedforward artificial neural networks designed primarily for processing structured grid data such as images and video streams. "
            "The CNN architecture consists of three core layer types: Convolutional layers, Pooling layers, and Fully Connected layers. "
            "The Convolutional layer applies learnable kernel filters across the input image using sliding dot product operations to produce feature maps, capturing local spatial hierarchies such as edges, textures, shapes, and high-level object representations while reducing parameters via weight sharing. "
            "The Pooling layer (e.g., Max Pooling or Average Pooling) downsamples feature maps to reduce spatial dimensions, computational expense, and control overfitting while granting spatial translation invariance. "
            "Finally, flattened spatial features are passed into Fully Connected layers with Softmax or Sigmoid activation functions to perform final classification or bounding box regression tasks."
        ),
        "student_answer": (
            "Convolutional Neural Networks (CNNs) are deep learning neural networks tailored for computer vision and image processing tasks. "
            "A CNN architecture consists of Convolutional layers, Pooling layers, and Fully Connected dense layers. "
            "In Convolutional layers, small filter matrices slide over input images to compute dot products, creating feature maps that extract visual primitives like edges, corners, and object parts. Weight sharing reduces overall parameters. "
            "Pooling layers, such as Max Pooling, reduce the dimensions of feature maps, lowering memory usage and making feature detection invariant to small shifts. "
            "Dense fully connected layers flatten the feature vectors and use activation functions like Softmax to output final classification labels."
        ),
        "key_concepts": "CNN, convolutional layers, kernel filters, feature maps, weight sharing, max pooling, spatial invariance, fully connected layers, softmax classification",
        "max_marks": 10.0
    },
    {
        "q_num": 5,
        "question": "Describe Gradient Descent Optimization, Learning Rate Tuning, and Adam Optimizer.",
        "model_answer": (
            "Gradient Descent is an iterative first-order optimization algorithm used to minimize objective loss functions in machine learning and deep learning models. "
            "It calculates the partial derivatives of the loss function with respect to model parameters (weights and biases), updating parameters in the direction of steepest descending gradient. "
            "The step size taken in each parameter update is governed by the learning rate hyperparameter. If the learning rate is too large, the algorithm may overshoot global minima and diverge; if it is too small, convergence becomes extremely slow or gets trapped in local minima. "
            "Stochastic Gradient Descent (SGD) computes gradients on mini-batches to improve speed and escape saddle points. "
            "The Adaptive Moment Estimation (Adam) optimizer enhances SGD by combining Momentum (tracking exponential moving averages of past gradients) and RMSProp (scaling updates inversely proportional to root mean square of recent squared gradients), providing individual adaptive learning rates for each parameter."
        ),
        "student_answer": (
            "Gradient Descent is an optimization method that minimizes loss functions by updating model weights opposite to the gradient vector direction. "
            "The learning rate determines the step size per iteration. A high learning rate causes divergence and overshooting, while a very low learning rate slows training and risks local minima stagnation. "
            "Mini-batch SGD updates weights using small data batches for efficiency. "
            "The Adam optimizer combines Momentum and RMSProp. It maintains exponentially decaying averages of past gradients and squared gradients, dynamically adjusting individual learning rates for every parameter, leading to faster and robust convergence."
        ),
        "key_concepts": "gradient descent, loss function minimization, partial derivatives, learning rate tuning, divergence, local minima, SGD, Adam optimizer, momentum, RMSProp",
        "max_marks": 10.0
    },
    {
        "q_num": 6,
        "question": "Explain K-Fold Cross-Validation and why it is superior to a simple train-test split.",
        "model_answer": (
            "K-Fold Cross-Validation is a resampling procedure used to evaluate machine learning models on limited data samples in an unbiased and robust manner. "
            "The dataset is randomly partitioned into K equal-sized subsets or folds. The training and evaluation process is repeated K times: in each iteration, K-1 folds serve as training data while the remaining single fold acts as the validation set. "
            "The final performance score is calculated by averaging validation metrics across all K iterations, providing a reliable estimate of model performance with computed standard deviation. "
            "K-Fold Cross-Validation is superior to a basic single train-test split because every data point is used for both training and validation exactly once, reducing performance estimation variance caused by arbitrary data splits. "
            "It is particularly valuable for hyperparameter tuning and model selection on small to medium-sized datasets where single split train sets may suffer from sampling bias."
        ),
        "student_answer": (
            "K-Fold Cross-Validation splits a dataset into K equal parts or folds to evaluate model generalization performance reliably. "
            "During K iterations, K-1 folds are used for model training, and the remaining 1 fold serves as validation data. Each fold acts as the test set exactly once. "
            "The average score across all K folds represents the overall model performance metric. "
            "Compared to a single train-test split, K-Fold cross-validation reduces evaluation variance and eliminates sampling bias because all observations are tested. "
            "It prevents accidental easy or hard test splits, making it ideal for hyperparameter tuning and model comparison."
        ),
        "key_concepts": "K-fold cross validation, resampling procedure, K iterations, validation metric averaging, sampling bias reduction, variance reduction, hyperparameter tuning",
        "max_marks": 10.0
    },
    {
        "q_num": 7,
        "question": "Compare Decision Trees and Random Forest Ensemble Methods, explaining Bagging and Feature Randomness.",
        "model_answer": (
            "A Decision Tree is a non-parametric supervised learning method that constructs a hierarchical tree structure by recursively splitting data based on feature thresholds that maximize information gain or minimize Gini impurity. "
            "While interpretable, individual decision trees are highly prone to high variance and overfitting complex datasets. "
            "Random Forest is an ensemble learning method that solves decision tree overfitting by combining multiple decision trees using Bootstrap Aggregating (Bagging) and feature randomness. "
            "Bagging creates multiple bootstrap sub-datasets by sampling the training data with replacement, training an independent decision tree on each sub-sample. "
            "Feature randomness ensures that at each split node in every tree, only a random subset of total features is considered, decorrelating individual trees. "
            "Final predictions are aggregated via majority voting for classification or mean averaging for regression tasks, significantly reducing variance while preserving low bias."
        ),
        "student_answer": (
            "A Decision Tree splits data recursively into decision nodes using feature criteria like Gini impurity or Information Gain. Decision trees are easy to interpret but frequently overfit training data. "
            "Random Forest is an ensemble algorithm combining many decision trees to increase accuracy and lower variance. "
            "It uses Bagging (Bootstrap Aggregating) by generating random sub-samples with replacement to train separate trees. "
            "It also uses Feature Randomness, selecting a random subset of features at each node split to decorrelate individual trees. "
            "For classification, predictions are aggregated by majority vote, while regression takes the average, creating a highly resilient model."
        ),
        "key_concepts": "decision tree, Gini impurity, information gain, random forest, ensemble method, bagging, bootstrap aggregation, feature randomness, decorrelation, majority voting",
        "max_marks": 10.0
    },
    {
        "q_num": 8,
        "question": "Explain Natural Language Processing (NLP) Self-Attention Mechanism and Transformer Architecture.",
        "model_answer": (
            "The Transformer architecture revolutionized Natural Language Processing (NLP) by replacing sequential Recurrent Neural Networks (RNNs) with parallelizable self-attention mechanisms. "
            "Self-attention allows the model to dynamically compute contextual relationship weights between all words in a sequence simultaneously, regardless of their distance. "
            "Given input embeddings combined with positional encodings, the mechanism projects inputs into Query (Q), Key (K), and Value (V) matrices. "
            "Attention scores are calculated by taking the scaled dot-product of Query and Key matrices, passing scores through Softmax, and multiplying by Value matrices: Attention(Q,K,V) = Softmax(QK^T / sqrt(d_k))V. "
            "Multi-Head Attention runs multiple self-attention operations in parallel, capturing diverse linguistic relationships (syntax, semantics, coreference). "
            "Transformers enable parallel GPU computation during training, serving as the foundational building block for modern Large Language Models (LLMs) such as GPT-4, BERT, and Llama."
        ),
        "student_answer": (
            "The Transformer architecture replaced sequential RNNs in NLP by introducing self-attention mechanisms that enable parallel processing of text sequences. "
            "Self-attention computes dynamic attention weights between every pair of words in a sentence, capturing long-range dependencies effectively. "
            "The input embeddings use Query (Q), Key (K), and Value (V) vectors. Scaled dot-product attention computes compatibility between Queries and Keys, applies Softmax, and multiplies by Values. "
            "Multi-Head Attention projects Q, K, V into multiple subspaces to capture distinct context relationships concurrently. "
            "Transformers allow fast GPU training and form the architectural foundation for Large Language Models like GPT, BERT, and Llama."
        ),
        "key_concepts": "transformer architecture, self attention mechanism, query key value, scaled dot product, multi head attention, parallel processing, large language models, LLM",
        "max_marks": 10.0
    },
    {
        "q_num": 9,
        "question": "Define Confusion Matrix Metrics: Precision, Recall, F1-Score, and describe when each should be prioritized.",
        "model_answer": (
            "A Confusion Matrix evaluates classification model performance by tabulating True Positives (TP), True Negatives (TN), False Positives (FP), and False Negatives (FN). "
            "Precision = TP / (TP + FP) measures the proportion of positive predictions that were actually correct. High Precision is prioritized in scenarios where False Positives carry severe costs or inconvenience, such as email spam classification (preventing important emails from landing in spam folders) or fraud suspicion alerts. "
            "Recall (Sensitivity) = TP / (TP + FN) measures the proportion of actual positive cases successfully detected. High Recall is prioritized when False Negatives are dangerous or critical, such as cancer medical screening or autonomous vehicle collision detection. "
            "F1-Score = 2 * (Precision * Recall) / (Precision + Recall) is the harmonic mean of Precision and Recall, serving as a balanced evaluation metric on imbalanced datasets where both false positives and false negatives must be minimized."
        ),
        "student_answer": (
            "A Confusion Matrix measures classification performance using True Positives (TP), True Negatives (TN), False Positives (FP), and False Negatives (FN). "
            "Precision = TP / (TP + FP) calculates the accuracy of positive predictions. Precision is prioritized when False Positives are costly, such as spam detection where genuine emails should not be flagged. "
            "Recall = TP / (TP + FN) measures the ratio of actual positives correctly identified. Recall is critical when False Negatives are dangerous, like medical disease diagnosis or threat detection. "
            "F1-Score is the harmonic mean of Precision and Recall, providing a single balanced metric for imbalanced datasets."
        ),
        "key_concepts": "confusion matrix, precision, recall, sensitivity, F1 score, true positive, false positive, false negative, imbalanced datasets, medical screening, spam detection",
        "max_marks": 10.0
    },
    {
        "q_num": 10,
        "question": "Explain Reinforcement Learning Core Concepts: Agent, Environment, Reward, Policy, and Q-Learning Algorithm.",
        "model_answer": (
            "Reinforcement Learning (RL) is a machine learning paradigm focused on decision-making where an autonomous Agent learns optimal action policies through trial-and-error interaction with a dynamic Environment. "
            "At each discrete time step, the Agent observes state S, selects action A based on its Policy, transitions to new state S', and receives a scalar Reward R. "
            "The Policy (π) defines the agent's behavior mapping states to actions. The goal is to maximize cumulative discounted long-term rewards. "
            "Q-Learning is a model-free, off-policy temporal difference algorithm that learns quality values Q(s, a) representing expected cumulative rewards for taking action a in state s. "
            "The Q-value update follows the Bellman Equation: Q(s, a) <- Q(s, a) + alpha * [R + gamma * max_a' Q(s', a') - Q(s, a)], where alpha is learning rate and gamma is discount factor. Deep Q-Networks (DQN) combine Q-learning with deep neural networks for high-dimensional state spaces."
        ),
        "student_answer": (
            "Reinforcement Learning (RL) trains an Agent to make sequential decisions inside an Environment by maximizing cumulative rewards. "
            "At each step, the agent reads current state S, takes action A guided by Policy π, transitions to state S', and receives Reward R. "
            "The Policy determines action choices per state to achieve maximum long-term reward. "
            "Q-Learning is a model-free RL algorithm that updates Q-values Q(s, a) using the Bellman Equation update rule: Q(s,a) = Q(s,a) + alpha * (R + gamma * max Q(s', a') - Q(s,a)). "
            "Deep Q-Networks (DQN) use neural networks to approximate Q-values in complex environments like robotics and game AI."
        ),
        "key_concepts": "reinforcement learning, agent, environment, reward, policy, Q-learning, Bellman equation, temporal difference, deep Q networks, DQN, cumulative reward",
        "max_marks": 10.0
    }
]

def build_all_docx():
    # 1. Master Answer Key DOCX blocks
    master_blocks = []
    for item in qa_pairs:
        master_blocks.append({
            "heading": f"Q{item['q_num']}. {item['question']} [Max Marks: {item['max_marks']:.0f}]",
            "paragraphs": [
                {"bold_prefix": "Model Solution:", "text": item['model_answer']},
                {"bold_prefix": "Required Key Concepts:", "text": item['key_concepts']}
            ]
        })

    # 2. Student Answer Sheet DOCX blocks
    student_blocks = [
        {
            "heading": "STUDENT IDENTIFICATION & EXAM DETAILS",
            "paragraphs": [
                {"bold_prefix": "Roll No:", "text": "STU-2026-AIML-099"},
                {"bold_prefix": "Student Name:", "text": "Ananya Sharma"},
                {"bold_prefix": "Subject:", "text": "Artificial Intelligence & ML (CS-501)"},
                {"bold_prefix": "Exam Type:", "text": "Theory End-Semester Examination"},
                {"bold_prefix": "Total Questions:", "text": "10 Answered"}
            ]
        }
    ]

    for item in qa_pairs:
        student_blocks.append({
            "heading": f"Question {item['q_num']}: {item['question']}",
            "paragraphs": [
                {"bold_prefix": f"Q{item['q_num']} Student Answer:", "text": item['student_answer']}
            ]
        })

import io

def generate_minimal_docx_bytes(title, subtitle, content_blocks):
    buf = io.BytesIO()
    
    body_xml_parts = []
    body_xml_parts.append(f'<w:p><w:pPr><w:jc w:val="center"/><w:rPr><w:b/><w:sz w:val="36"/><w:color w:val="1E293B"/></w:rPr></w:pPr><w:r><w:rPr><w:b/><w:sz w:val="36"/><w:color w:val="1E293B"/></w:rPr><w:t>{escape_xml(title)}</w:t></w:r></w:p>')
    if subtitle:
        body_xml_parts.append(f'<w:p><w:pPr><w:jc w:val="center"/><w:rPr><w:i/><w:sz w:val="22"/><w:color w:val="64748B"/></w:rPr></w:pPr><w:r><w:rPr><w:i/><w:sz w:val="22"/><w:color w:val="64748B"/></w:rPr><w:t>{escape_xml(subtitle)}</w:t></w:r></w:p>')
    body_xml_parts.append('<w:p/>')

    for block in content_blocks:
        heading = block.get('heading', '')
        if heading:
            body_xml_parts.append(f'<w:p><w:pPr><w:rPr><w:b/><w:sz w:val="26"/><w:color w:val="1E40AF"/></w:rPr></w:pPr><w:r><w:rPr><w:b/><w:sz w:val="26"/><w:color w:val="1E40AF"/></w:rPr><w:t>{escape_xml(heading)}</w:t></w:r></w:p>')
        
        for p_info in block.get('paragraphs', []):
            bold_prefix = p_info.get('bold_prefix', '')
            text = p_info.get('text', '')
            p_xml = '<w:p><w:pPr><w:rPr><w:sz w:val="22"/></w:rPr></w:pPr>'
            if bold_prefix:
                p_xml += f'<w:r><w:rPr><w:b/><w:sz w:val="22"/><w:color w:val="0F172A"/></w:rPr><w:t>{escape_xml(bold_prefix)} </w:t></w:r>'
            if text:
                p_xml += f'<w:r><w:rPr><w:sz w:val="22"/><w:color w:val="334155"/></w:rPr><w:t>{escape_xml(text)}</w:t></w:r>'
            p_xml += '</w:p>'
            body_xml_parts.append(p_xml)
        body_xml_parts.append('<w:p/>')

    doc_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
    <w:body>
        {''.join(body_xml_parts)}
    </w:body>
</w:document>"""

    content_types_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
    <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
    <Default Extension="xml" ContentType="application/xml"/>
    <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""

    rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
    <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

    doc_rels_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>"""

    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('[Content_Types].xml', content_types_xml)
        zf.writestr('_rels/.rels', rels_xml)
        zf.writestr('word/document.xml', doc_xml)
        zf.writestr('word/_rels/document.xml.rels', doc_rels_xml)
    
    return buf.getvalue()

def get_aiml_docx_bytes():
    master_blocks = []
    for item in qa_pairs:
        master_blocks.append({
            "heading": f"Q{item['q_num']}. {item['question']} [Max Marks: {item['max_marks']:.0f}]",
            "paragraphs": [
                {"bold_prefix": "Model Solution:", "text": item['model_answer']},
                {"bold_prefix": "Required Key Concepts:", "text": item['key_concepts']}
            ]
        })

    student_blocks = [
        {
            "heading": "STUDENT IDENTIFICATION & EXAM DETAILS",
            "paragraphs": [
                {"bold_prefix": "Roll No:", "text": "STU-2026-AIML-099"},
                {"bold_prefix": "Student Name:", "text": "Ananya Sharma"},
                {"bold_prefix": "Subject:", "text": "Artificial Intelligence & ML (CS-501)"},
                {"bold_prefix": "Exam Type:", "text": "Theory End-Semester Examination"},
                {"bold_prefix": "Total Questions:", "text": "10 Answered"}
            ]
        }
    ]
    for item in qa_pairs:
        student_blocks.append({
            "heading": f"Question {item['q_num']}: {item['question']}",
            "paragraphs": [
                {"bold_prefix": f"Q{item['q_num']} Student Answer:", "text": item['student_answer']}
            ]
        })

    m_bytes = generate_minimal_docx_bytes(
        title="AI & Machine Learning (CS-501) - Master Marking Scheme",
        subtitle="10 Comprehensive Questions & Model Solutions | Total Max Marks: 100",
        content_blocks=master_blocks
    )
    s_bytes = generate_minimal_docx_bytes(
        title="STUDENT END-SEMESTER ANSWER SHEET",
        subtitle="Department of Computer Science & Engineering",
        content_blocks=student_blocks
    )

    curr_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        with open(os.path.join(curr_dir, "AIML_Master_Answer_Key.docx"), "wb") as f:
            f.write(m_bytes)
        with open(os.path.join(curr_dir, "AIML_Student_Answer_Sheet.docx"), "wb") as f:
            f.write(s_bytes)
    except Exception:
        pass

    return m_bytes, s_bytes

def build_all_docx():
    m_bytes, s_bytes = get_aiml_docx_bytes()
    curr_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        m_path = os.path.join(curr_dir, "AIML_Master_Answer_Key.docx")
        s_path = os.path.join(curr_dir, "AIML_Student_Answer_Sheet.docx")
        with open(m_path, "wb") as f:
            f.write(m_bytes)
        with open(s_path, "wb") as f:
            f.write(s_bytes)
        print(f"Generated benchmark files successfully: {os.path.basename(m_path)}, {os.path.basename(s_path)}")
    except Exception as e:
        print(f"Error writing benchmark docx files: {e}")

build_all_docx()
